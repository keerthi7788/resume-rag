"""Semantic resume chunking by section headers without token-based splitting."""

from __future__ import annotations

import re
from typing import TypedDict

from metadata_extractor import normalize_resume_text, parse_resume_sections

CHUNK_SECTION_ORDER: tuple[str, ...] = (
    "education",
    "experience",
    "skills",
    "projects",
    "certifications",
)


class ResumeChunkDict(TypedDict):
    chunk_id: str
    section: str
    content: str


def sanitize_resume_id(resume_id: str) -> str:
    """Normalize a resume identifier for stable chunk IDs."""
    cleaned = re.sub(r"[^\w.-]+", "_", resume_id.strip())
    return cleaned.strip("_") or "resume"


def build_chunk_id(resume_id: str, section: str, index: int) -> str:
    """Build a deterministic chunk identifier."""
    safe_resume_id = sanitize_resume_id(resume_id)
    return f"{safe_resume_id}_{section}_{index}"


def chunk_resume_by_headers(
    text: str,
    resume_id: str = "",
    *,
    include_general: bool = True,
) -> list[ResumeChunkDict]:
    """
    Split a resume into section-level semantic chunks.

    Each recognized section becomes exactly one chunk. Section content is never
    split by token count or character limits, preserving section boundaries.

    Args:
        text: Raw resume text.
        resume_id: Identifier used to prefix chunk IDs (e.g. filename stem).
        include_general: Include preamble content before the first header.

    Returns:
        List of chunks shaped as:
        {"chunk_id": "", "section": "", "content": ""}
    """
    sections = parse_resume_sections(text)
    chunks: list[ResumeChunkDict] = []
    chunk_index = 0

    if include_general and (general := sections.get("general", "").strip()):
        chunks.append(
            {
                "chunk_id": build_chunk_id(resume_id, "general", chunk_index),
                "section": "general",
                "content": general,
            }
        )
        chunk_index += 1

    for section_name in CHUNK_SECTION_ORDER:
        section_content = sections.get(section_name, "").strip()
        if not section_content:
            continue
        chunks.append(
            {
                "chunk_id": build_chunk_id(resume_id, section_name, chunk_index),
                "section": section_name,
                "content": section_content,
            }
        )
        chunk_index += 1

    known_sections = set(CHUNK_SECTION_ORDER) | {"general"}
    for section_name, section_content in sections.items():
        if section_name in known_sections:
            continue
        section_content = section_content.strip()
        if not section_content:
            continue
        chunks.append(
            {
                "chunk_id": build_chunk_id(resume_id, section_name, chunk_index),
                "section": section_name,
                "content": section_content,
            }
        )
        chunk_index += 1

    return chunks


def chunk_resume_text(text: str, resume_id: str = "") -> list[ResumeChunkDict]:
    """Alias for semantic section chunking."""
    return chunk_resume_by_headers(text, resume_id=resume_id)


def chunk_to_document(chunk: ResumeChunkDict) -> str:
    """Format a chunk for embedding or storage."""
    return f"{chunk['section'].title()}:\n{chunk['content']}"
