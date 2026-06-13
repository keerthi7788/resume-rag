"""Parse must-have job requirements from job descriptions."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal

RequirementType = Literal["skill", "experience"]

MUST_HAVE_SECTION_PATTERN = re.compile(
    r"(?:must[- ]have(?:\s+requirements?)?|mandatory\s+requirements?|required\s+skills?)"
    r"\s*:?\s*(?P<body>.+?)(?=\n\s*(?:nice to have|preferred|good to have|responsibilities|about)\b|\Z)",
    re.IGNORECASE | re.DOTALL,
)
YEARS_SKILL_PATTERN = re.compile(
    r"(?P<years>\d+)\+?\s*years?\s+(?:of\s+)?(?P<skill>[A-Za-z0-9#+. /-]+?)"
    r"(?:\s+(?:experience|exp))?(?:[.,;]|\s+(?:mandatory|required)|$|\n)",
    re.IGNORECASE,
)
SKILL_MANDATORY_PATTERN = re.compile(
    r"(?P<skill>[A-Za-z0-9#+. /-]+?)\s+(?:is\s+)?(?:mandatory|required|a must)\b",
    re.IGNORECASE,
)
MANDATORY_SKILL_PATTERN = re.compile(
    r"(?:mandatory|required|must[- ]have)\s*:?\s*(?P<skill>[A-Za-z0-9#+. /,-]+)",
    re.IGNORECASE,
)
MIN_YEARS_PATTERN = re.compile(
    r"(?:minimum|at least|min\.?)\s+(?P<years>\d+)\+?\s*years?(?:\s+of)?(?:\s+(?P<skill>[A-Za-z0-9#+. /-]+))?",
    re.IGNORECASE,
)
BULLET_PATTERN = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+(?P<item>.+?)\s*$", re.MULTILINE)

KEYWORD_ALIASES: dict[str, tuple[str, ...]] = {
    "python": ("python", "py"),
    "aws": ("aws", "amazon web services"),
    "machine learning": ("machine learning", "ml", "deep learning"),
    "docker": ("docker", "containers"),
    "kubernetes": ("kubernetes", "k8s"),
    "postgresql": ("postgresql", "postgres"),
    "fastapi": ("fastapi", "fast api"),
}


@dataclass
class MustHaveRequirement:
    """A single must-have requirement extracted from a job description."""

    requirement_type: RequirementType
    keyword: str
    min_years: float | None = None
    raw_text: str = ""

    def label(self) -> str:
        if self.min_years is not None:
            return f"{self.min_years:g}+ years {self.keyword}"
        return self.keyword


@dataclass
class ParsedRequirements:
    """Structured must-have requirements parsed from a job description."""

    must_have: list[MustHaveRequirement] = field(default_factory=list)
    raw_lines: list[str] = field(default_factory=list)


@dataclass
class RequirementCheckResult:
    """Outcome of evaluating one requirement against a candidate."""

    requirement: MustHaveRequirement
    met: bool
    detail: str


def normalize_keyword(keyword: str) -> str:
    """Normalize a requirement keyword for display and matching."""
    cleaned = re.sub(r"\s+", " ", keyword.strip(" .,;:-"))
    lowered = cleaned.lower()
    for canonical, aliases in KEYWORD_ALIASES.items():
        if lowered in aliases:
            return canonical
    return cleaned


def _dedupe_requirements(requirements: list[MustHaveRequirement]) -> list[MustHaveRequirement]:
    seen: set[tuple[str, str, float | None]] = set()
    deduped: list[MustHaveRequirement] = []
    for requirement in requirements:
        key = (
            requirement.requirement_type,
            requirement.keyword.lower(),
            requirement.min_years,
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(requirement)
    return deduped


def _parse_requirement_line(line: str) -> list[MustHaveRequirement]:
    text = line.strip(" .;")
    if not text:
        return []

    requirements: list[MustHaveRequirement] = []

    years_skill_match = YEARS_SKILL_PATTERN.search(text)
    if years_skill_match:
        requirements.append(
            MustHaveRequirement(
                requirement_type="experience",
                keyword=normalize_keyword(years_skill_match.group("skill")),
                min_years=float(years_skill_match.group("years")),
                raw_text=text,
            )
        )
        return requirements

    for pattern in (SKILL_MANDATORY_PATTERN, MANDATORY_SKILL_PATTERN):
        match = pattern.search(text)
        if match:
            skill_text = match.group("skill")
            for part in re.split(r",|/|\band\b", skill_text, flags=re.IGNORECASE):
                part = part.strip(" .;")
                if part:
                    requirements.append(
                        MustHaveRequirement(
                            requirement_type="skill",
                            keyword=normalize_keyword(part),
                            raw_text=text,
                        )
                    )
            return requirements

    min_years_match = MIN_YEARS_PATTERN.search(text)
    if min_years_match:
        skill = min_years_match.group("skill")
        requirements.append(
            MustHaveRequirement(
                requirement_type="experience",
                keyword=normalize_keyword(skill) if skill else "experience",
                min_years=float(min_years_match.group("years")),
                raw_text=text,
            )
        )
        return requirements

    if re.search(r"\b(?:mandatory|required|must[- ]have)\b", text, re.IGNORECASE):
        cleaned = re.sub(
            r"^(?:mandatory|required|must[- ]have)\s*:?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )
        for part in re.split(r",|/|\band\b", cleaned, flags=re.IGNORECASE):
            part = part.strip(" .;")
            if part:
                requirements.append(
                    MustHaveRequirement(
                        requirement_type="skill",
                        keyword=normalize_keyword(part),
                        raw_text=text,
                    )
                )
    return requirements


def _extract_requirement_lines(job_description: str) -> list[str]:
    lines: list[str] = []
    section_match = MUST_HAVE_SECTION_PATTERN.search(job_description)
    if section_match:
        body = section_match.group("body")
        lines.extend(match.group("item") for match in BULLET_PATTERN.finditer(body))
        if not lines:
            lines.extend(part.strip() for part in body.splitlines() if part.strip())

    for match in YEARS_SKILL_PATTERN.finditer(job_description):
        lines.append(match.group(0).strip())
    for match in SKILL_MANDATORY_PATTERN.finditer(job_description):
        lines.append(match.group(0).strip())
    for match in MANDATORY_SKILL_PATTERN.finditer(job_description):
        lines.append(match.group(0).strip())
    for match in MIN_YEARS_PATTERN.finditer(job_description):
        lines.append(match.group(0).strip())

    return list(dict.fromkeys(line for line in lines if line))


def parse_must_have_requirements(job_description: str) -> ParsedRequirements:
    """Extract must-have requirements from a job description."""
    raw_lines = _extract_requirement_lines(job_description)
    requirements: list[MustHaveRequirement] = []
    for line in raw_lines:
        requirements.extend(_parse_requirement_line(line))
    return ParsedRequirements(
        must_have=_dedupe_requirements(requirements),
        raw_lines=raw_lines,
    )


def keyword_variants(keyword: str) -> list[str]:
    """Return searchable variants for a requirement keyword."""
    normalized = normalize_keyword(keyword).lower()
    variants = {normalized}
    for canonical, aliases in KEYWORD_ALIASES.items():
        if normalized == canonical or normalized in aliases:
            variants.update(aliases)
            variants.add(canonical)
    return sorted(variants)


def keyword_in_text(keyword: str, text: str) -> bool:
    """Check whether a keyword (or alias) appears in text."""
    lowered = text.lower()
    for variant in keyword_variants(keyword):
        if " " in variant or len(variant) > 4:
            if variant in lowered:
                return True
        elif re.search(rf"\b{re.escape(variant)}\b", lowered):
            return True
    return False


def build_candidate_corpus(
    *,
    skills: str = "",
    education: str = "",
    years_of_experience: int | float = 0,
    chunk_contents: list[str] | None = None,
) -> str:
    """Build a searchable text corpus for a candidate."""
    parts = [skills, education, str(years_of_experience)]
    if chunk_contents:
        parts.extend(chunk_contents)
    return " ".join(part for part in parts if part).lower()


def evaluate_requirement(
    requirement: MustHaveRequirement,
    corpus: str,
    years_of_experience: int | float,
) -> RequirementCheckResult:
    """Evaluate a single must-have requirement against candidate data."""
    if requirement.requirement_type == "experience" and requirement.min_years is not None:
        years_ok = float(years_of_experience) >= requirement.min_years
        if requirement.keyword.lower() in {"experience", ""}:
            met = years_ok
            detail = (
                f"Has {years_of_experience} year(s) of experience (requires {requirement.min_years:g}+)."
                if met
                else f"Only {years_of_experience} year(s) of experience; requires {requirement.min_years:g}+."
            )
            return RequirementCheckResult(requirement=requirement, met=met, detail=detail)

        skill_ok = keyword_in_text(requirement.keyword, corpus)
        met = years_ok and skill_ok
        if met:
            detail = (
                f"Meets {requirement.min_years:g}+ years requirement with "
                f"{requirement.keyword} experience ({years_of_experience} total years)."
            )
        elif not skill_ok:
            detail = f"Missing evidence of {requirement.keyword} experience."
        else:
            detail = (
                f"Has {requirement.keyword} experience but only "
                f"{years_of_experience} total year(s); requires {requirement.min_years:g}+."
            )
        return RequirementCheckResult(requirement=requirement, met=met, detail=detail)

    skill_ok = keyword_in_text(requirement.keyword, corpus)
    detail = (
        f"Required skill present: {requirement.keyword}."
        if skill_ok
        else f"Missing required skill: {requirement.keyword}."
    )
    return RequirementCheckResult(requirement=requirement, met=skill_ok, detail=detail)


def candidate_meets_requirements(
    requirements: ParsedRequirements,
    *,
    skills: str = "",
    education: str = "",
    years_of_experience: int | float = 0,
    chunk_contents: list[str] | None = None,
) -> tuple[bool, list[RequirementCheckResult]]:
    """Return whether a candidate satisfies all must-have requirements."""
    if not requirements.must_have:
        return True, []

    corpus = build_candidate_corpus(
        skills=skills,
        education=education,
        years_of_experience=years_of_experience,
        chunk_contents=chunk_contents,
    )
    checks = [
        evaluate_requirement(requirement, corpus, years_of_experience)
        for requirement in requirements.must_have
    ]
    return all(check.met for check in checks), checks


def format_requirement_checks(checks: list[RequirementCheckResult]) -> str:
    """Format requirement check results for reasoning output."""
    if not checks:
        return "No must-have requirements were specified."

    lines = ["Must-have requirement checks:"]
    for check in checks:
        status = "PASS" if check.met else "FAIL"
        lines.append(f"- [{status}] {check.requirement.label()}: {check.detail}")
    return "\n".join(lines)
