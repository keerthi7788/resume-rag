from dataclasses import dataclass, field
import re


# ------------------------------------------------
# Models
# ------------------------------------------------

@dataclass
class MustHaveRequirement:

    requirement_type: str

    keyword: str | None = None

    min_years: int | None = None

    raw_text: str = ""

    def label(self):

        if self.requirement_type == "skill":
            return self.keyword

        return f"{self.min_years}+ years"


@dataclass
class ParsedRequirements:

    must_have: list[MustHaveRequirement] = field(
        default_factory=list
    )

    raw_lines: list[str] = field(
        default_factory=list
    )

    def to_dict(self):

        return {

            "must_have": [

                {

                    "type": r.requirement_type,

                    "keyword": r.keyword,

                    "min_years": r.min_years

                }

                for r in self.must_have

            ],

            "raw_lines": self.raw_lines

        }


@dataclass
class RequirementCheckResult:

    requirement: MustHaveRequirement

    met: bool

    detail: str


# ------------------------------------------------
# Ignore JD section headers
# ------------------------------------------------

SKIP_WORDS = {

    "required",

    "requirements",

    "required skills",

    "skills",

    "skills:",

    "skill",

    "experience",

    "experience:",

    "must have",

    "preferred",

    "job description",

    "senior backend engineer",

    "backend engineer",

    "senior"

}


# ------------------------------------------------
# Parse JD
# ------------------------------------------------

def parse_must_have_requirements(

    jd: str

) -> ParsedRequirements:

    parsed = ParsedRequirements()

    if not jd:

        return parsed

    lines = [

        x.strip()

        for x in jd.split("\n")

        if x.strip()

    ]

    parsed.raw_lines = lines

    for line in lines:

        lower = line.lower().strip()

        # Ignore headers

        if lower in SKIP_WORDS:

            continue

        # Experience

        match = re.search(

            r"(\d+)\s*\+?\s*years",

            lower

        )

        if match:

            parsed.must_have.append(

                MustHaveRequirement(

                    requirement_type="experience",

                    min_years=int(

                        match.group(1)

                    ),

                    raw_text=line

                )

            )

            continue

        # Ignore section names like "Experience:"

        if lower.endswith(":"):

            continue

        # Skill

        parsed.must_have.append(

            MustHaveRequirement(

                requirement_type="skill",

                keyword=line,

                raw_text=line

            )

        )

    return parsed


# ------------------------------------------------
# Candidate filtering
# ------------------------------------------------

def candidate_meets_requirements(

    requirements,

    skills,

    education,

    years_of_experience,

    chunk_contents

):

    checks = []

    all_met = True

    skills_lower = skills.lower()

    all_text = " ".join(

        chunk_contents

    ).lower()

    for req in requirements.must_have:

        if req.requirement_type == "skill":

            keyword = req.keyword.lower()

            found = (

                keyword in skills_lower

                or

                keyword in all_text

            )

            checks.append(

                RequirementCheckResult(

                    requirement=req,

                    met=found,

                    detail=

                    f"Matched skill: {req.keyword}"

                    if found

                    else

                    f"Missing required skill: {req.keyword}"

                )

            )

            if not found:

                all_met = False

        elif req.requirement_type == "experience":

            found = (

                years_of_experience

                >=

                req.min_years

            )

            checks.append(

                RequirementCheckResult(

                    requirement=req,

                    met=found,

                    detail=

                    f"Experience {years_of_experience} years"

                    if found

                    else

                    f"Need {req.min_years}+ years"

                )

            )

            if not found:

                all_met = False

    return all_met, checks


# ------------------------------------------------
# Pretty print
# ------------------------------------------------

def format_requirement_checks(

    checks

):

    output = []

    for c in checks:

        status = "PASS" if c.met else "FAIL"

        output.append(

            f"[{status}] {c.detail}"

        )

    return "\n".join(output)