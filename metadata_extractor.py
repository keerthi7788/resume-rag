"""Resume metadata extraction with section-based parsing and regex fallbacks."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, TypedDict

SECTION_ALIASES: dict[str, tuple[str, ...]] = {
    "education": ("education", "academic background", "academics", "qualifications"),
    "experience": (
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
    ),
    "skills": ("skills", "technical skills", "core competencies", "technologies"),
    "projects": ("projects", "personal projects", "key projects"),
    "certifications": (
        "certifications",
        "certification",
        "licenses",
        "credentials",
        "professional certifications",
    ),
}

SECTION_HEADER_PATTERN = re.compile(
    r"^\s*(?P<header>"
    + "|".join(
        re.escape(alias)
        for aliases in SECTION_ALIASES.values()
        for alias in aliases
    )
    + r")\s*:?\s*$",
    re.IGNORECASE | re.MULTILINE,
)

DATE_RANGE_PATTERN = re.compile(
    r"(?P<start>(?:\d{4}|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}))"
    r"\s*(?:[-–—to]+\s*)"
    r"(?P<end>(?:present|current|now|\d{4}|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}))",
    re.IGNORECASE,
)
MONTH_YEAR_PATTERN = re.compile(
    r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+(\d{4})\b",
    re.IGNORECASE,
)
YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
PHONE_PATTERN = re.compile(r"\+?\d[\d\s().-]{7,}\d")
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)

INLINE_NAME_PATTERN = re.compile(
    r"^\s*(?:name|candidate(?:\s+name)?)\s*[:|-]\s*(?P<name>.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
INLINE_SKILLS_PATTERN = re.compile(
    r"(?:technical\s+)?skills\s*[:|-]\s*(?P<skills>.+?)(?:\n\n|\n(?=[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*:)|$)",
    re.IGNORECASE | re.DOTALL,
)
INLINE_EDUCATION_PATTERN = re.compile(
    r"education\s*[:|-]\s*(?P<education>.+?)(?:\n\n|\n(?=[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*:)|$)",
    re.IGNORECASE | re.DOTALL,
)
DEGREE_PATTERN = re.compile(
    r"\b(?:"
    r"B\.?\s*(?:Tech|E|Sc|A)|M\.?\s*(?:Tech|E|Sc|A|BA)|"
    r"Ph\.?\s*D|MBA|Bachelor(?:'s)?|Master(?:'s)?|Doctor(?:ate)?"
    r")\b[^.\n]*(?:\b(?:University|College|Institute|School)\b[^.\n]*)?",
    re.IGNORECASE,
)


class ResumeMetadataDict(TypedDict):
    candidate_name: str
    skills: list[str]
    years_of_experience: int | float
    education: str


def normalize_resume_text(text: str) -> str:
    """Normalize whitespace and line endings."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _canonical_section_name(header: str) -> str:
    normalized = header.strip().lower()
    for canonical, aliases in SECTION_ALIASES.items():
        if normalized in aliases:
            return canonical
    return normalized


def parse_resume_sections(text: str) -> dict[str, str]:
    """Split resume text into canonical sections keyed by header name."""
    normalized = normalize_resume_text(text)
    matches = list(SECTION_HEADER_PATTERN.finditer(normalized))

    if not matches:
        return {"general": normalized}

    sections: dict[str, str] = {}
    preamble = normalized[: matches[0].start()].strip()
    if preamble:
        sections["general"] = preamble

    for index, match in enumerate(matches):
        section_name = _canonical_section_name(match.group("header"))
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(normalized)
        section_text = normalized[start:end].strip()
        if section_text:
            if section_name in sections:
                sections[section_name] = f"{sections[section_name]}\n{section_text}"
            else:
                sections[section_name] = section_text

    return sections


def split_non_empty_lines(text: str) -> list[str]:
    """Return stripped non-empty lines from text."""
    return [line.strip() for line in text.splitlines() if line.strip()]


def parse_skill_tokens(skills_text: str) -> list[str]:
    """Parse a skills block into a deduplicated list of skill names."""
    if not skills_text.strip():
        return []

    candidates: list[str] = []
    for raw_line in skills_text.splitlines():
        line = raw_line.strip("•-* \t")
        if not line or SECTION_HEADER_PATTERN.match(line):
            continue
        parts = re.split(r"[,;|/]", line)
        candidates.extend(part.strip() for part in parts if part.strip())

    deduped: list[str] = []
    seen: set[str] = set()
    for skill in candidates:
        key = skill.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(skill)
    return deduped


def format_education_text(education_text: str) -> str:
    """Collapse education lines into a single string."""
    if not education_text.strip():
        return ""

    entries: list[str] = []
    for raw_line in education_text.splitlines():
        line = raw_line.strip("•-* \t")
        if not line or SECTION_HEADER_PATTERN.match(line):
            continue
        entries.append(line)
    return " | ".join(entries)


def parse_month_year(value: str) -> datetime | None:
    """Parse a month-year, year, or present/current marker into a datetime."""
    value = value.strip().lower()
    if value in {"present", "current", "now"}:
        return datetime.now()

    month_match = MONTH_YEAR_PATTERN.search(value)
    if month_match:
        month_name = value[:3]
        year = int(month_match.group(1))
        month_map = {
            "jan": 1,
            "feb": 2,
            "mar": 3,
            "apr": 4,
            "may": 5,
            "jun": 6,
            "jul": 7,
            "aug": 8,
            "sep": 9,
            "oct": 10,
            "nov": 11,
            "dec": 12,
        }
        return datetime(year, month_map.get(month_name, 1), 1)

    year_match = YEAR_PATTERN.search(value)
    if year_match:
        return datetime(int(year_match.group(0)), 1, 1)

    return None


def estimate_years_from_experience_text(experience_text: str) -> int | float:
    """Estimate total years of experience from an experience section or text block."""
    if not experience_text.strip():
        return 0

    total_months = 0
    for match in DATE_RANGE_PATTERN.finditer(experience_text):
        start = parse_month_year(match.group("start"))
        end = parse_month_year(match.group("end"))
        if start and end and end >= start:
            months = (end.year - start.year) * 12 + (end.month - start.month) + 1
            total_months += max(months, 0)

    if total_months > 0:
        years = round(total_months / 12.0, 1)
        return int(years) if years == int(years) else years

    years = {int(year) for year in YEAR_PATTERN.findall(experience_text)}
    if len(years) >= 2:
        span = float(max(years) - min(years))
        return int(span) if span == int(span) else span
    return 0


def extract_candidate_name(text: str, sections: dict[str, str] | None = None) -> str:
    """
    Extract candidate name using preamble lines, then regex fallback.

    Priority:
    1. Explicit "Name:" line anywhere in the resume
    2. First plausible line in the general/preamble section
    3. First plausible line in the full document
    """
    normalized = normalize_resume_text(text)
    sections = sections or parse_resume_sections(normalized)

    inline_match = INLINE_NAME_PATTERN.search(normalized)
    if inline_match:
        return inline_match.group("name").strip().title()

    search_blocks = [sections.get("general", ""), normalized]
    for block in search_blocks:
        for line in split_non_empty_lines(block)[:8]:
            if EMAIL_PATTERN.search(line) or PHONE_PATTERN.search(line) or URL_PATTERN.search(line):
                continue
            if SECTION_HEADER_PATTERN.match(line):
                continue
            if len(line.split()) <= 6 and not line.endswith(":"):
                cleaned = re.sub(
                    r"^(resume|curriculum vitae|cv)\s*[-:]*\s*",
                    "",
                    line,
                    flags=re.IGNORECASE,
                )
                if cleaned:
                    return cleaned.strip().title()

    lines = split_non_empty_lines(normalized)
    return lines[0].title() if lines else ""


def extract_skills(text: str, sections: dict[str, str] | None = None) -> list[str]:
    """
    Extract skills from the Skills section, with inline regex fallback.

    Priority:
    1. Dedicated skills section
    2. Inline "Skills: ..." pattern in full text
    """
    normalized = normalize_resume_text(text)
    sections = sections or parse_resume_sections(normalized)

    if skills_section := sections.get("skills", ""):
        skills = parse_skill_tokens(skills_section)
        if skills:
            return skills

    inline_match = INLINE_SKILLS_PATTERN.search(normalized)
    if inline_match:
        return parse_skill_tokens(inline_match.group("skills"))

    return []


def extract_education(text: str, sections: dict[str, str] | None = None) -> str:
    """
    Extract education as a single string from section parsing or regex fallback.

    Priority:
    1. Dedicated education section
    2. Inline "Education: ..." pattern
    3. Degree/university regex anywhere in the document
    """
    normalized = normalize_resume_text(text)
    sections = sections or parse_resume_sections(normalized)

    if education_section := sections.get("education", ""):
        education = format_education_text(education_section)
        if education:
            return education

    inline_match = INLINE_EDUCATION_PATTERN.search(normalized)
    if inline_match:
        education = format_education_text(inline_match.group("education"))
        if education:
            return education

    degree_matches = [match.group(0).strip() for match in DEGREE_PATTERN.finditer(normalized)]
    if degree_matches:
        return " | ".join(dict.fromkeys(degree_matches))

    return ""


def extract_years_of_experience(text: str, sections: dict[str, str] | None = None) -> int | float:
    """
    Estimate years of experience from the Experience section or full-text regex fallback.
    """
    normalized = normalize_resume_text(text)
    sections = sections or parse_resume_sections(normalized)

    if experience_section := sections.get("experience", ""):
        years = estimate_years_from_experience_text(experience_section)
        if years:
            return years

    return estimate_years_from_experience_text(normalized)


def extract_resume_metadata(text: str) -> ResumeMetadataDict:
    """
    Extract resume metadata and return a plain dictionary.

    Returns:
        {
            "candidate_name": "",
            "skills": [],
            "years_of_experience": 0,
            "education": ""
        }
    """
    normalized = normalize_resume_text(text)
    sections = parse_resume_sections(normalized)

    return {
        "candidate_name": extract_candidate_name(normalized, sections),
        "skills": extract_skills(normalized, sections),
        "years_of_experience": extract_years_of_experience(normalized, sections),
        "education": extract_education(normalized, sections),
    }


def metadata_to_chroma_fields(metadata: ResumeMetadataDict, source_file: str = "") -> dict[str, Any]:
    """Flatten metadata for ChromaDB storage."""
    chroma_fields: dict[str, Any] = {
        "candidate_name": metadata["candidate_name"],
        "skills": ", ".join(metadata["skills"]),
        "education": metadata["education"],
        "years_of_experience": metadata["years_of_experience"],
    }
    if source_file:
        chroma_fields["source_file"] = source_file
    return chroma_fields
