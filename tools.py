from typing import Any

from requirement_parser import parse_must_have_requirements
from job_matcher import JobMatcher


matcher = JobMatcher()


def extract_requirements(jd: str) -> dict[str, Any]:
    """
    Parse JD and extract requirements.
    """

    req = parse_must_have_requirements(jd)

    return {

        "must_have": [

            {
                "type": r.requirement_type,

                "keyword": r.keyword,

                "min_years": r.min_years

            }

            for r in req.must_have
        ],

        "raw_lines": req.raw_lines
    }


def compare_candidates(candidate_ids: list[str]) -> list[dict]:
    """
    Compare candidates side by side.

    candidate_ids can be:

    [
      "backend_engineer_sneha_iyer_10y.txt",
      "devops_engineer_sanjay_kulkarni_3y.txt"
    ]
    """

    collection = matcher.collection

    results = []

    for candidate_id in candidate_ids:

        res = collection.get(

            where={

                "source_file": candidate_id

            },

            include=["metadatas"]

        )

        if not res["metadatas"]:

            continue

        metadata = res["metadatas"][0]

        results.append(

            {

                "candidate_name":

                    metadata.get(

                        "candidate_name",

                        "Unknown"

                    ),

                "source_file":

                    metadata.get(

                        "source_file"

                    ),

                "skills":

                    metadata.get(

                        "skills",

                        ""

                    ),

                "education":

                    metadata.get(

                        "education",

                        ""

                    ),

                "years_of_experience":

                    metadata.get(

                        "years_of_experience",

                        0

                    )

            }

        )

    return results


def generate_interview_questions(

    candidate_id: str

) -> list[str]:

    """
    Generate screening questions based on skills.
    """

    collection = matcher.collection

    result = collection.get(

        where={

            "source_file": candidate_id

        },

        include=["metadatas"]

    )

    if not result["metadatas"]:

        return [

            "Candidate not found."

        ]

    metadata = result["metadatas"][0]

    skills = metadata.get(

        "skills",

        ""

    )

    questions = []

    for skill in skills.split(","):

        skill = skill.strip()

        if not skill:

            continue

        questions.append(

            f"Explain your experience with {skill}."

        )

        questions.append(

            f"What challenges did you face while using {skill}?"

        )

    questions.append(

        "Describe your most challenging project."

    )

    questions.append(

        "How do you approach debugging and problem solving?"

    )

    return questions