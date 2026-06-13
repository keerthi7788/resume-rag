"""Unit tests for must-have requirement parsing and filtering."""

import unittest

from job_matcher import filter_grouped_candidates
from requirement_parser import (
    candidate_meets_requirements,
    parse_must_have_requirements,
)


JOB_WITH_REQUIREMENTS = """
Senior Backend Engineer

Must Have:
- 5+ years Python
- AWS mandatory
- Machine Learning required

Nice to have:
- Kubernetes
"""


class TestParseMustHaveRequirements(unittest.TestCase):
    def test_parses_examples_from_job_description(self) -> None:
        parsed = parse_must_have_requirements(JOB_WITH_REQUIREMENTS)
        labels = [req.label() for req in parsed.must_have]
        self.assertIn("5+ years python", labels)
        self.assertIn("aws", labels)
        self.assertIn("machine learning", labels)

    def test_parses_inline_mandatory_phrases(self) -> None:
        parsed = parse_must_have_requirements("AWS mandatory. 7+ years Python experience.")
        labels = [req.label() for req in parsed.must_have]
        self.assertIn("aws", labels)
        self.assertIn("7+ years python", labels)

    def test_empty_description_returns_no_requirements(self) -> None:
        parsed = parse_must_have_requirements("Looking for a collaborative engineer.")
        self.assertEqual(parsed.must_have, [])


class TestCandidateMeetsRequirements(unittest.TestCase):
    def test_candidate_passes_all_requirements(self) -> None:
        requirements = parse_must_have_requirements(JOB_WITH_REQUIREMENTS)
        meets, checks = candidate_meets_requirements(
            requirements,
            skills="Python, AWS, Machine Learning, FastAPI",
            education="B.Tech CS",
            years_of_experience=10,
            chunk_contents=["Built ML pipelines on AWS using Python"],
        )
        self.assertTrue(meets)
        self.assertTrue(all(check.met for check in checks))

    def test_candidate_fails_missing_skill(self) -> None:
        requirements = parse_must_have_requirements("AWS mandatory")
        meets, checks = candidate_meets_requirements(
            requirements,
            skills="Python, Docker",
            years_of_experience=8,
        )
        self.assertFalse(meets)
        self.assertFalse(checks[0].met)

    def test_candidate_fails_insufficient_years(self) -> None:
        requirements = parse_must_have_requirements("5+ years Python")
        meets, _ = candidate_meets_requirements(
            requirements,
            skills="Python",
            years_of_experience=3,
            chunk_contents=["Python developer"],
        )
        self.assertFalse(meets)


class TestFilterGroupedCandidates(unittest.TestCase):
    def test_filters_before_ranking(self) -> None:
        from job_matcher import RetrievedChunk, aggregate_chunks_by_candidate

        chunks = [
            RetrievedChunk(
                chunk_id="jane_skills_0",
                section="skills",
                content="Python, AWS, Machine Learning",
                similarity=0.9,
                distance=0.1,
                candidate_name="Jane Doe",
                source_file="jane.pdf",
                metadata={
                    "candidate_name": "Jane Doe",
                    "source_file": "jane.pdf",
                    "skills": "Python, AWS, Machine Learning",
                    "years_of_experience": 10,
                },
            ),
            RetrievedChunk(
                chunk_id="john_skills_0",
                section="skills",
                content="Java, Spring",
                similarity=0.85,
                distance=0.15,
                candidate_name="John Smith",
                source_file="john.pdf",
                metadata={
                    "candidate_name": "John Smith",
                    "source_file": "john.pdf",
                    "skills": "Java, Spring",
                    "years_of_experience": 8,
                },
            ),
        ]
        grouped = aggregate_chunks_by_candidate(chunks)
        requirements = parse_must_have_requirements(JOB_WITH_REQUIREMENTS)
        passed, filtered_out = filter_grouped_candidates(grouped, requirements)

        self.assertEqual(len(passed), 1)
        self.assertEqual(len(filtered_out), 1)
        self.assertEqual(filtered_out[0]["candidate_name"], "John Smith")


if __name__ == "__main__":
    unittest.main()
