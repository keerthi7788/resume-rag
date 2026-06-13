"""Resume RAG pipeline: ingest resumes, chunk by section, embed, and persist in ChromaDB."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings
from docx import Document
from metadata_extractor import (
    extract_resume_metadata as extract_resume_metadata_dict,
    metadata_to_chroma_fields,
    parse_resume_sections,
)
from resume_chunker import chunk_resume_by_headers, chunk_to_document
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_COLLECTION_NAME = "resumes"
DEFAULT_PERSIST_DIR = "./chroma_db"
DEFAULT_RESUMES_DIR = "./resumes"
CHUNK_SECTIONS = ("education", "experience", "skills", "projects", "certifications")


class ResumeProcessingError(Exception):
    """Raised when a resume cannot be processed."""


class UnsupportedFileTypeError(ResumeProcessingError):
    """Raised when a resume file type is not supported."""


@dataclass
class ResumeMetadata:
    """Structured metadata extracted from a resume."""

    candidate_name: str = ""
    skills: list[str] = field(default_factory=list)
    education: str = ""
    years_of_experience: int | float = 0
    source_file: str = ""

    def to_dict(self) -> dict[str, str | int | float]:
        fields = metadata_to_chroma_fields(
            {
                "candidate_name": self.candidate_name,
                "skills": self.skills,
                "years_of_experience": self.years_of_experience,
                "education": self.education,
            },
            source_file=self.source_file,
        )
        return fields


@dataclass
class ResumeChunk:
    """A section-level chunk from a resume."""

    chunk_id: str
    section: str
    content: str
    metadata: ResumeMetadata
    chunk_index: int

    @property
    def text(self) -> str:
        """Backward-compatible alias for chunk body text."""
        return self.content


def extract_text_from_pdf(file_path: Path) -> str:
    """Extract plain text from a PDF resume."""
    try:
        reader = PdfReader(str(file_path))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages).strip()
        if not text:
            raise ResumeProcessingError(f"No text extracted from PDF: {file_path}")
        return text
    except ResumeProcessingError:
        raise
    except Exception as exc:
        raise ResumeProcessingError(f"Failed to read PDF {file_path}: {exc}") from exc


def extract_text_from_docx(file_path: Path) -> str:
    """Extract plain text from a DOCX resume."""
    try:
        document = Document(str(file_path))
        paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
        text = "\n".join(paragraphs).strip()
        if not text:
            raise ResumeProcessingError(f"No text extracted from DOCX: {file_path}")
        return text
    except ResumeProcessingError:
        raise
    except Exception as exc:
        raise ResumeProcessingError(f"Failed to read DOCX {file_path}: {exc}") from exc


def extract_text_from_txt(file_path: Path) -> str:
    """Extract plain text from a TXT resume."""
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace").strip()
        if not text:
            raise ResumeProcessingError(f"No text extracted from TXT: {file_path}")
        return text
    except ResumeProcessingError:
        raise
    except Exception as exc:
        raise ResumeProcessingError(f"Failed to read TXT {file_path}: {exc}") from exc


def extract_resume_text(file_path: Path | str) -> str:
    """Dispatch text extraction based on file extension."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return extract_text_from_pdf(path)
    if suffix == ".docx":
        return extract_text_from_docx(path)
    if suffix == ".txt":
        return extract_text_from_txt(path)

    raise UnsupportedFileTypeError(f"Unsupported resume format: {suffix} ({path})")


def extract_metadata(text: str, source_file: str = "") -> ResumeMetadata:
    """Extract candidate metadata from resume text."""
    metadata = extract_resume_metadata_dict(text)
    return ResumeMetadata(
        candidate_name=metadata["candidate_name"],
        skills=metadata["skills"],
        education=metadata["education"],
        years_of_experience=metadata["years_of_experience"],
        source_file=source_file,
    )


def chunk_resume_by_sections(text: str) -> dict[str, str]:
    """Split resume text into section chunks keyed by normalized header names."""
    return parse_resume_sections(text)


def build_resume_chunks(text: str, metadata: ResumeMetadata) -> list[ResumeChunk]:
    """Create semantic section chunks with attached metadata."""
    resume_id = Path(metadata.source_file).stem if metadata.source_file else "resume"
    section_chunks = chunk_resume_by_headers(text, resume_id=resume_id)

    return [
        ResumeChunk(
            chunk_id=chunk["chunk_id"],
            section=chunk["section"],
            content=chunk["content"],
            metadata=metadata,
            chunk_index=index,
        )
        for index, chunk in enumerate(section_chunks)
    ]


def list_resume_files(resumes_dir: Path | str) -> list[Path]:
    """Return supported resume files from a directory."""
    directory = Path(resumes_dir)
    if not directory.exists():
        raise FileNotFoundError(f"Resumes directory not found: {directory}")
    if not directory.is_dir():
        raise NotADirectoryError(f"Resumes path is not a directory: {directory}")

    files = sorted(
        path
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    logger.info("Found %d supported resume file(s) in %s", len(files), directory)
    return files


def _get_embedding_model(model_name: str = EMBEDDING_MODEL_NAME) -> SentenceTransformer:
    logger.info("Loading embedding model: %s", model_name)
    return SentenceTransformer(model_name)


def _get_chroma_client(persist_dir: Path | str) -> chromadb.PersistentClient:
    path = Path(persist_dir)
    path.mkdir(parents=True, exist_ok=True)
    logger.info("Using ChromaDB persist directory: %s", path)
    return chromadb.PersistentClient(
        path=str(path),
        settings=Settings(anonymized_telemetry=False),
    )


def build_vector_store(
    resumes_dir: Path | str = DEFAULT_RESUMES_DIR,
    persist_dir: Path | str = DEFAULT_PERSIST_DIR,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    reset_collection: bool = False,
) -> chromadb.Collection:
    """
    Read resumes, extract metadata, chunk by section, embed, and persist in ChromaDB.

    Args:
        resumes_dir: Folder containing PDF, DOCX, and TXT resumes.
        persist_dir: Local directory for ChromaDB persistence.
        collection_name: Name of the Chroma collection.
        reset_collection: If True, delete and recreate the collection before ingest.

    Returns:
        The populated ChromaDB collection.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    resume_paths = list_resume_files(resumes_dir)
    if not resume_paths:
        logger.warning("No resume files found in %s", resumes_dir)
        return _get_chroma_client(persist_dir).get_or_create_collection(name=collection_name)

    model = _get_embedding_model()
    client = _get_chroma_client(persist_dir)

    if reset_collection:
        try:
            client.delete_collection(name=collection_name)
            logger.info("Deleted existing collection: %s", collection_name)
        except Exception:
            logger.debug("Collection %s did not exist; creating a new one", collection_name)

    collection = client.get_or_create_collection(name=collection_name)

    all_ids: list[str] = []
    all_documents: list[str] = []
    all_embeddings: list[list[float]] = []
    all_metadatas: list[dict[str, Any]] = []

    for resume_path in resume_paths:
        try:
            logger.info("Processing resume: %s", resume_path.name)
            text = extract_resume_text(resume_path)
            metadata = extract_metadata(text, source_file=resume_path.name)
            chunks = build_resume_chunks(text, metadata)

            if not chunks:
                logger.warning("No chunks generated for %s", resume_path.name)
                continue

            for chunk in chunks:
                document = chunk_to_document(
                    {
                        "chunk_id": chunk.chunk_id,
                        "section": chunk.section,
                        "content": chunk.content,
                    }
                )
                embedding = model.encode(document, normalize_embeddings=True).tolist()

                chunk_metadata = metadata.to_dict()
                chunk_metadata.update(
                    {
                        "section": chunk.section,
                        "chunk_index": chunk.chunk_index,
                    }
                )

                all_ids.append(chunk.chunk_id)
                all_documents.append(document)
                all_embeddings.append(embedding)
                all_metadatas.append(chunk_metadata)

            logger.info(
                "Processed %s | candidate=%s | chunks=%d | skills=%d | years=%s",
                resume_path.name,
                metadata.candidate_name,
                len(chunks),
                len(metadata.skills),
                metadata.years_of_experience,
            )
        except ResumeProcessingError as exc:
            logger.error("Skipping resume %s: %s", resume_path.name, exc)
        except Exception as exc:
            logger.exception("Unexpected error while processing %s: %s", resume_path.name, exc)

    if all_ids:
        collection.add(
            ids=all_ids,
            documents=all_documents,
            embeddings=all_embeddings,
            metadatas=all_metadatas,
        )
        logger.info("Stored %d chunk(s) in collection '%s'", len(all_ids), collection_name)
    else:
        logger.warning("No chunks were stored in collection '%s'", collection_name)

    return collection


__all__ = [
    "CHUNK_SECTIONS",
    "ResumeChunk",
    "ResumeMetadata",
    "ResumeProcessingError",
    "UnsupportedFileTypeError",
    "build_resume_chunks",
    "build_vector_store",
    "chunk_resume_by_sections",
    "extract_metadata",
    "extract_resume_text",
    "extract_text_from_docx",
    "extract_text_from_pdf",
    "extract_text_from_txt",
    "list_resume_files",
]
