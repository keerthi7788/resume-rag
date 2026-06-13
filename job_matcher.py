"""Job-to-resume matching via semantic search over ChromaDB resume chunks."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from requirement_parser import (
    ParsedRequirements,
    RequirementCheckResult,
    candidate_meets_requirements,
    format_requirement_checks,
    parse_must_have_requirements,
)
from resume_rag import (
    DEFAULT_COLLECTION_NAME,
    DEFAULT_PERSIST_DIR,
    EMBEDDING_MODEL_NAME,
)

logger = logging.getLogger(__name__)

DEFAULT_TOP_K_CHUNKS = 10
SECTION_MATCH_WEIGHTS: dict[str, float] = {
    "skills": 1.2,
    "experience": 1.15,
    "projects": 1.05,
    "education": 0.95,
    "certifications": 1.0,
    "general": 0.85,
}


@dataclass
class RetrievedChunk:
    """A resume chunk returned from vector search."""

    chunk_id: str
    section: str
    content: str
    similarity: float
    distance: float
    candidate_name: str
    source_file: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CandidateMatch:
    """Aggregated match result for a single candidate."""

    candidate_name: str
    source_file: str
    score: float
    matched_chunks: list[RetrievedChunk] = field(default_factory=list)
    reasoning: str = ""
    skills: str = ""
    education: str = ""
    years_of_experience: int | float = 0
    meets_requirements: bool = True
    requirement_checks: list[RequirementCheckResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_name": self.candidate_name,
            "source_file": self.source_file,
            "score": self.score,
            "skills": self.skills,
            "education": self.education,
            "years_of_experience": self.years_of_experience,
            "meets_requirements": self.meets_requirements,
            "requirement_checks": [
                {
                    "requirement": check.requirement.label(),
                    "met": check.met,
                    "detail": check.detail,
                }
                for check in self.requirement_checks
            ],
            "matched_sections": [chunk.section for chunk in self.matched_chunks],
            "reasoning": self.reasoning,
            "matched_chunks": [
                {
                    "chunk_id": chunk.chunk_id,
                    "section": chunk.section,
                    "similarity": chunk.similarity,
                    "content": chunk.content,
                }
                for chunk in self.matched_chunks
            ],
        }


@dataclass
class JobMatchResult:
    """Full job match output including parsed requirements and filtered candidates."""

    requirements: ParsedRequirements
    candidates: list[CandidateMatch]
    filtered_out: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "must_have_requirements": [req.label() for req in self.requirements.must_have],
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "filtered_out": self.filtered_out,
        }


def distance_to_similarity(distance: float) -> float:
    """Convert a Chroma distance into a bounded similarity score."""
    return round(1.0 / (1.0 + max(distance, 0.0)), 4)


def candidate_key(metadata: dict[str, Any], chunk_id: str) -> str:
    """Build a stable aggregation key for a candidate."""
    source_file = str(metadata.get("source_file", "")).strip()
    if source_file:
        return source_file

    candidate_name = str(metadata.get("candidate_name", "")).strip()
    if candidate_name:
        return candidate_name.lower()

    return chunk_id.rsplit("_", 2)[0]


def aggregate_chunks_by_candidate(chunks: list[RetrievedChunk]) -> dict[str, list[RetrievedChunk]]:
    """Group retrieved chunks by candidate."""
    grouped: dict[str, list[RetrievedChunk]] = {}
    for chunk in chunks:
        key = candidate_key(chunk.metadata, chunk.chunk_id)
        grouped.setdefault(key, []).append(chunk)
    return grouped


def calculate_candidate_score(chunks: list[RetrievedChunk]) -> float:
    """
    Compute an overall candidate score from retrieved chunk similarities.

    Uses weighted section relevance, best-match strength, and multi-section coverage.
    """
    if not chunks:
        return 0.0

    weighted_similarities = [
        chunk.similarity * SECTION_MATCH_WEIGHTS.get(chunk.section, 1.0)
        for chunk in chunks
    ]
    best_weighted = max(weighted_similarities)
    average_weighted = sum(weighted_similarities) / len(weighted_similarities)
    coverage_bonus = min(0.08 * (len(chunks) - 1), 0.16)

    raw_score = best_weighted * 0.5 + average_weighted * 0.42 + coverage_bonus
    return round(min(raw_score, 1.0), 4)


def build_match_reasoning(
    candidate: CandidateMatch,
    requirement_checks: list[RequirementCheckResult] | None = None,
) -> str:
    """Generate detailed human-readable reasoning for a candidate match."""
    if not candidate.matched_chunks:
        return f"No matching resume sections were found for {candidate.candidate_name or 'this candidate'}."

    sorted_chunks = sorted(candidate.matched_chunks, key=lambda chunk: chunk.similarity, reverse=True)
    top_section = sorted_chunks[0].section.replace("_", " ").title()
    sections = ", ".join(chunk.section.replace("_", " ").title() for chunk in sorted_chunks)

    lines = [
        (
            f"{candidate.candidate_name or 'Candidate'} scored {candidate.score:.2%} based on "
            f"{len(sorted_chunks)} semantically similar resume section(s): {sections}."
        ),
        f"The strongest match came from the {top_section} section.",
    ]

    checks = requirement_checks if requirement_checks is not None else candidate.requirement_checks
    if checks:
        lines.append(format_requirement_checks(checks))

    if candidate.skills:
        lines.append(f"Resume skills: {candidate.skills}.")
    if candidate.education:
        lines.append(f"Education: {candidate.education}.")
    if candidate.years_of_experience:
        lines.append(f"Reported experience: {candidate.years_of_experience} year(s).")

    lines.append("Section-level evidence:")
    for chunk in sorted_chunks:
        preview = chunk.content.replace("\n", " ").strip()
        if len(preview) > 160:
            preview = f"{preview[:157]}..."
        lines.append(
            f"- {chunk.section.title()} (similarity {chunk.similarity:.2%}): {preview}"
        )

    return "\n".join(lines)


def filter_grouped_candidates(
    grouped_chunks: dict[str, list[RetrievedChunk]],
    requirements: ParsedRequirements,
) -> tuple[dict[str, list[RetrievedChunk]], list[dict[str, Any]]]:
    """Filter candidate chunk groups that do not meet must-have requirements."""
    if not requirements.must_have:
        return grouped_chunks, []

    passed: dict[str, list[RetrievedChunk]] = {}
    filtered_out: list[dict[str, Any]] = []

    for key, chunks in grouped_chunks.items():
        representative = chunks[0]
        metadata = representative.metadata
        meets, checks = candidate_meets_requirements(
            requirements,
            skills=str(metadata.get("skills", "")),
            education=str(metadata.get("education", "")),
            years_of_experience=metadata.get("years_of_experience", 0) or 0,
            chunk_contents=[chunk.content for chunk in chunks],
        )
        if meets:
            passed[key] = chunks
            continue

        failed_checks = [check for check in checks if not check.met]
        filtered_out.append(
            {
                "candidate_name": representative.candidate_name,
                "source_file": representative.source_file,
                "reason": "; ".join(check.detail for check in failed_checks),
                "requirement_checks": [
                    {
                        "requirement": check.requirement.label(),
                        "met": check.met,
                        "detail": check.detail,
                    }
                    for check in checks
                ],
            }
        )

    return passed, filtered_out


def parse_query_results(results: dict[str, Any]) -> list[RetrievedChunk]:
    """Convert a Chroma query response into RetrievedChunk objects."""
    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    chunks: list[RetrievedChunk] = []
    for chunk_id, document, distance, metadata in zip(ids, documents, distances, metadatas, strict=True):
        metadata = metadata or {}
        section = str(metadata.get("section", "unknown"))
        content = document or ""
        if ":\n" in content:
            _, content = content.split(":\n", 1)

        chunks.append(
            RetrievedChunk(
                chunk_id=chunk_id,
                section=section,
                content=content.strip(),
                similarity=distance_to_similarity(float(distance)),
                distance=float(distance),
                candidate_name=str(metadata.get("candidate_name", "")),
                source_file=str(metadata.get("source_file", "")),
                metadata=metadata,
            )
        )
    return chunks


def rank_candidates(
    grouped_chunks: dict[str, list[RetrievedChunk]],
    requirements: ParsedRequirements | None = None,
) -> list[CandidateMatch]:
    """Score and rank candidates from grouped retrieved chunks."""
    requirements = requirements or ParsedRequirements()
    candidates: list[CandidateMatch] = []
    for chunks in grouped_chunks.values():
        representative = chunks[0]
        metadata = representative.metadata
        meets, checks = candidate_meets_requirements(
            requirements,
            skills=str(metadata.get("skills", "")),
            education=str(metadata.get("education", "")),
            years_of_experience=metadata.get("years_of_experience", 0) or 0,
            chunk_contents=[chunk.content for chunk in chunks],
        )
        candidate = CandidateMatch(
            candidate_name=representative.candidate_name,
            source_file=representative.source_file,
            score=calculate_candidate_score(chunks),
            matched_chunks=sorted(chunks, key=lambda chunk: chunk.similarity, reverse=True),
            skills=str(metadata.get("skills", "")),
            education=str(metadata.get("education", "")),
            years_of_experience=metadata.get("years_of_experience", 0) or 0,
            meets_requirements=meets,
            requirement_checks=checks,
        )
        candidate.reasoning = build_match_reasoning(candidate, checks)
        candidates.append(candidate)

    candidates.sort(key=lambda match: match.score, reverse=True)
    return candidates


class JobMatcher:
    """Match job descriptions to ranked resume candidates using ChromaDB retrieval."""

    def __init__(
        self,
        persist_dir: Path | str = DEFAULT_PERSIST_DIR,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        model_name: str = EMBEDDING_MODEL_NAME,
        top_k_chunks: int = DEFAULT_TOP_K_CHUNKS,
        embedding_model: SentenceTransformer | None = None,
        collection: chromadb.Collection | None = None,
    ) -> None:
        self.persist_dir = Path(persist_dir)
        self.collection_name = collection_name
        self.model_name = model_name
        self.top_k_chunks = top_k_chunks
        self._model = embedding_model
        self._collection = collection

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info("Loading embedding model: %s", self.model_name)
            self._model = SentenceTransformer(self.model_name)
        return self._model

    @property
    def collection(self) -> chromadb.Collection:
        if self._collection is None:
            client = chromadb.PersistentClient(
                path=str(self.persist_dir),
                settings=Settings(anonymized_telemetry=False),
            )
            self._collection = client.get_collection(name=self.collection_name)
        return self._collection

    def embed_job_description(self, job_description: str) -> list[float]:
        """Generate a normalized embedding for the job description."""
        if not job_description.strip():
            raise ValueError("Job description text cannot be empty.")
        embedding = self.model.encode(job_description, normalize_embeddings=True)
        return embedding.tolist()

    def retrieve_matching_chunks(self, job_description: str) -> list[RetrievedChunk]:
        """Query ChromaDB and return the top matching resume chunks."""
        embedding = self.embed_job_description(job_description)
        logger.info(
            "Querying collection '%s' for top %d chunk(s)",
            self.collection_name,
            self.top_k_chunks,
        )

        try:
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=self.top_k_chunks,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            logger.error("ChromaDB query failed: %s", exc)
            raise RuntimeError(f"Failed to query resume collection '{self.collection_name}': {exc}") from exc

        chunks = parse_query_results(results)
        logger.info("Retrieved %d matching chunk(s)", len(chunks))
        return chunks

    def match(self, job_description: str) -> list[CandidateMatch]:
        """Find and rank candidates that satisfy must-have requirements."""
        return self.match_with_details(job_description).candidates

    def match_with_details(self, job_description: str) -> JobMatchResult:
        """
        Find and rank candidates for a job description.

        Pipeline:
        1. Parse must-have requirements from the job description
        2. Embed the job description and retrieve top resume chunks
        3. Aggregate chunks by candidate
        4. Filter candidates that fail must-have requirements
        5. Score and rank remaining candidates with detailed reasoning
        """
        requirements = parse_must_have_requirements(job_description)
        if requirements.must_have:
            logger.info(
                "Parsed %d must-have requirement(s): %s",
                len(requirements.must_have),
                ", ".join(req.label() for req in requirements.must_have),
            )

        chunks = self.retrieve_matching_chunks(job_description)
        if not chunks:
            logger.warning("No matching chunks found for the provided job description")
            return JobMatchResult(requirements=requirements, candidates=[], filtered_out=[])

        grouped = aggregate_chunks_by_candidate(chunks)
        passed, filtered_out = filter_grouped_candidates(grouped, requirements)
        ranked = rank_candidates(passed, requirements)

        if filtered_out:
            logger.info("Filtered out %d candidate(s) failing must-have requirements", len(filtered_out))
        logger.info("Ranked %d candidate(s)", len(ranked))
        return JobMatchResult(
            requirements=requirements,
            candidates=ranked,
            filtered_out=filtered_out,
        )

    def match_as_dicts(self, job_description: str) -> list[dict[str, Any]]:
        """Return ranked candidates as serializable dictionaries."""
        return [candidate.to_dict() for candidate in self.match(job_description)]


__all__ = [
    "CandidateMatch",
    "JobMatchResult",
    "JobMatcher",
    "RetrievedChunk",
    "aggregate_chunks_by_candidate",
    "build_match_reasoning",
    "calculate_candidate_score",
    "candidate_key",
    "distance_to_similarity",
    "filter_grouped_candidates",
    "parse_query_results",
    "rank_candidates",
]
