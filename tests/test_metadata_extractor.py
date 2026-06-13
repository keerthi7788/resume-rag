"""Unit tests for resume metadata extraction."""

import unittest

from metadata_extractor import (
    estimate_years_from_experience_text,
    extract_candidate_name,
    extract_education,
    extract_resume_metadata,
    extract_skills,
    extract_years_of_experience,
    format_education_text,
    parse_resume_sections,
    parse_skill_tokens,
)


SAMPLE_RESUME = """Jane Doe
jane.doe@email.com | +1 555-0100

Skills
Python, FastAPI, PostgreSQL, Docker, AWS, Machine Learning

Experience
Senior Software Engineer | Acme Corp | Jan 2020 - Present
- Built scalable APIs and data pipelines.

Software Engineer | Beta Labs | Jun 2016 - Dec 2019
- Developed backend services in Python and Node.js.

Education
B.Tech Computer Science, State University, 2016

Projects
Resume RAG Search - semantic search over candidate resumes using embeddings.
"""


INLINE_RESUME = """Name: John Smith
john@example.com

Technical Skills
Java, Spring Boot, Kubernetes

Work Experience
Engineer at Foo Inc | 2018 - 2022

Education: M.S. Computer Science, MIT, 2018
"""

INLINE_SKILLS_RESUME = """John Smith
john@example.com

Technical Skills: Java, Spring Boot, Kubernetes
"""


NO_SECTION_RESUME = """Alice Johnson
alice@corp.com

5 years of experience building data platforms with Python and Spark.
Bachelor of Science in Information Technology, City College, 2015.
"""


class TestParseResumeSections(unittest.TestCase):
    def test_splits_known_sections(self) -> None:
        sections = parse_resume_sections(SAMPLE_RESUME)
        self.assertIn("general", sections)
        self.assertIn("skills", sections)
        self.assertIn("experience", sections)
        self.assertIn("education", sections)
        self.assertIn("projects", sections)
        self.assertIn("Python", sections["skills"])

    def test_recognizes_section_aliases(self) -> None:
        sections = parse_resume_sections(INLINE_RESUME)
        self.assertIn("skills", sections)
        self.assertIn("experience", sections)


class TestExtractCandidateName(unittest.TestCase):
    def test_from_preamble(self) -> None:
        self.assertEqual(extract_candidate_name(SAMPLE_RESUME), "Jane Doe")

    def test_from_inline_name_pattern(self) -> None:
        self.assertEqual(extract_candidate_name(INLINE_RESUME), "John Smith")

    def test_empty_text_returns_empty_string(self) -> None:
        self.assertEqual(extract_candidate_name(""), "")


class TestExtractSkills(unittest.TestCase):
    def test_from_skills_section(self) -> None:
        skills = extract_skills(SAMPLE_RESUME)
        self.assertEqual(
            skills,
            ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS", "Machine Learning"],
        )

    def test_inline_skills_fallback(self) -> None:
        skills = extract_skills(INLINE_SKILLS_RESUME)
        self.assertEqual(skills, ["Java", "Spring Boot", "Kubernetes"])

    def test_parse_skill_tokens_deduplicates(self) -> None:
        self.assertEqual(
            parse_skill_tokens("Python, Java\nPython | Go"),
            ["Python", "Java", "Go"],
        )


class TestExtractEducation(unittest.TestCase):
    def test_from_education_section(self) -> None:
        education = extract_education(SAMPLE_RESUME)
        self.assertEqual(education, "B.Tech Computer Science, State University, 2016")

    def test_inline_education_fallback(self) -> None:
        education = extract_education(INLINE_RESUME)
        self.assertEqual(education, "M.S. Computer Science, MIT, 2018")

    def test_degree_regex_fallback(self) -> None:
        education = extract_education(NO_SECTION_RESUME)
        self.assertIn("Bachelor", education)

    def test_format_education_text_joins_lines(self) -> None:
        text = format_education_text("B.Tech CS\nM.Tech AI")
        self.assertEqual(text, "B.Tech CS | M.Tech AI")


class TestExtractYearsOfExperience(unittest.TestCase):
    def test_from_experience_section(self) -> None:
        years = extract_years_of_experience(SAMPLE_RESUME)
        self.assertGreaterEqual(years, 9)

    def test_estimate_from_date_ranges(self) -> None:
        text = "Developer | Jan 2018 - Dec 2020\nAnalyst | 2015 - 2017"
        self.assertEqual(estimate_years_from_experience_text(text), 5.1)

    def test_missing_experience_returns_zero(self) -> None:
        self.assertEqual(extract_years_of_experience("Jane Doe\nSkills\nPython"), 0)


class TestExtractResumeMetadata(unittest.TestCase):
    def test_returns_required_schema(self) -> None:
        metadata = extract_resume_metadata(SAMPLE_RESUME)
        self.assertEqual(
            set(metadata.keys()),
            {"candidate_name", "skills", "years_of_experience", "education"},
        )
        self.assertIsInstance(metadata["candidate_name"], str)
        self.assertIsInstance(metadata["skills"], list)
        self.assertIsInstance(metadata["years_of_experience"], (int, float))
        self.assertIsInstance(metadata["education"], str)

    def test_full_sample_resume(self) -> None:
        metadata = extract_resume_metadata(SAMPLE_RESUME)
        self.assertEqual(metadata["candidate_name"], "Jane Doe")
        self.assertIn("Python", metadata["skills"])
        self.assertGreater(metadata["years_of_experience"], 0)
        self.assertIn("State University", metadata["education"])

    def test_empty_resume_defaults(self) -> None:
        metadata = extract_resume_metadata("")
        self.assertEqual(
            metadata,
            {
                "candidate_name": "",
                "skills": [],
                "years_of_experience": 0,
                "education": "",
            },
        )


if __name__ == "__main__":
    unittest.main()
