"""Unit tests for semantic resume chunking."""

import unittest

from resume_chunker import (
    build_chunk_id,
    chunk_resume_by_headers,
    chunk_to_document,
)


FULL_RESUME = """Jane Doe
jane.doe@email.com

Education
B.Tech Computer Science, State University, 2016

Experience
Senior Engineer | Acme Corp | 2020 - Present
Built APIs and data pipelines.

Skills
Python, FastAPI, PostgreSQL

Projects
Resume RAG Search - semantic search over resumes.

Certifications
AWS Certified Solutions Architect
"""


class TestBuildChunkId(unittest.TestCase):
    def test_builds_stable_id(self) -> None:
        self.assertEqual(build_chunk_id("jane_doe", "skills", 2), "jane_doe_skills_2")


class TestChunkResumeByHeaders(unittest.TestCase):
    def test_returns_required_schema(self) -> None:
        chunks = chunk_resume_by_headers(FULL_RESUME, resume_id="jane")
        self.assertGreater(len(chunks), 0)
        for chunk in chunks:
            self.assertEqual(set(chunk.keys()), {"chunk_id", "section", "content"})
            self.assertTrue(chunk["chunk_id"])
            self.assertTrue(chunk["section"])
            self.assertTrue(chunk["content"])

    def test_splits_all_requested_sections(self) -> None:
        chunks = chunk_resume_by_headers(FULL_RESUME, resume_id="jane", include_general=False)
        sections = [chunk["section"] for chunk in chunks]
        self.assertEqual(
            sections,
            ["education", "experience", "skills", "projects", "certifications"],
        )

    def test_preserves_section_boundaries(self) -> None:
        chunks = chunk_resume_by_headers(FULL_RESUME, resume_id="jane", include_general=False)
        experience = next(chunk for chunk in chunks if chunk["section"] == "experience")
        self.assertIn("Senior Engineer | Acme Corp", experience["content"])
        self.assertIn("Built APIs and data pipelines.", experience["content"])
        self.assertNotIn("Python", experience["content"])

    def test_one_chunk_per_section_without_token_splitting(self) -> None:
        long_skills = "Skills\n" + ", ".join([f"Skill{i}" for i in range(200)])
        chunks = chunk_resume_by_headers(long_skills, resume_id="long")
        skill_chunks = [chunk for chunk in chunks if chunk["section"] == "skills"]
        self.assertEqual(len(skill_chunks), 1)
        self.assertIn("Skill199", skill_chunks[0]["content"])

    def test_includes_general_preamble_by_default(self) -> None:
        chunks = chunk_resume_by_headers(FULL_RESUME, resume_id="jane")
        self.assertEqual(chunks[0]["section"], "general")
        self.assertIn("Jane Doe", chunks[0]["content"])

    def test_chunk_ids_are_unique(self) -> None:
        chunks = chunk_resume_by_headers(FULL_RESUME, resume_id="jane")
        chunk_ids = [chunk["chunk_id"] for chunk in chunks]
        self.assertEqual(len(chunk_ids), len(set(chunk_ids)))

    def test_chunk_to_document_formats_section_header(self) -> None:
        chunk = {"chunk_id": "jane_skills_0", "section": "skills", "content": "Python"}
        self.assertEqual(chunk_to_document(chunk), "Skills:\nPython")


if __name__ == "__main__":
    unittest.main()
