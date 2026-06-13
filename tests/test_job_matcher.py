"""Unit tests for job matching logic."""

import unittest

from job_matcher import (
    CandidateMatch,
    RetrievedChunk,
    aggregate_chunks_by_candidate,
    build_match_reasoning,
    calculate_candidate_score,
    candidate_key,
    distance_to_similarity,
    parse_query_results,
    rank_candidates,
)


def make_chunk(
    chunk_id: str,
    section: str,
    similarity: float,
    candidate_name: str = "Jane Doe",
    source_file: str = "jane.pdf",
    content: str = "Python developer",
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        section=section,
        content=content,
        similarity=similarity,
        distance=1.0 - similarity,
        candidate_name=candidate_name,
        source_file=source_file,
        metadata={
            "candidate_name": candidate_name,
            "source_file": source_file,
            "section": section,
            "skills": "Python, FastAPI",
            "education": "B.Tech CS",
            "years_of_experience": 5,
        },
    )


class TestDistanceToSimilarity(unittest.TestCase):
    def test_lower_distance_yields_higher_similarity(self) -> None:
        self.assertGreater(distance_to_similarity(0.1), distance_to_similarity(0.8))


class TestCandidateAggregation(unittest.TestCase):
    def test_candidate_key_prefers_source_file(self) -> None:
        metadata = {"candidate_name": "Jane Doe", "source_file": "jane.pdf"}
        self.assertEqual(candidate_key(metadata, "jane_skills_0"), "jane.pdf")

    def test_aggregate_chunks_by_candidate(self) -> None:
        chunks = [
            make_chunk("jane_skills_0", "skills", 0.9),
            make_chunk("jane_experience_1", "experience", 0.8),
            make_chunk("john_skills_0", "skills", 0.7, candidate_name="John Smith", source_file="john.pdf"),
        ]
        grouped = aggregate_chunks_by_candidate(chunks)
        self.assertEqual(len(grouped), 2)
        self.assertEqual(len(grouped["jane.pdf"]), 2)


class TestCandidateScoring(unittest.TestCase):
    def test_skills_section_scores_higher_than_general(self) -> None:
        skills_score = calculate_candidate_score([make_chunk("jane_skills_0", "skills", 0.8)])
        general_score = calculate_candidate_score([make_chunk("jane_general_0", "general", 0.8)])
        self.assertGreater(skills_score, general_score)

    def test_multiple_chunks_increase_score(self) -> None:
        single = calculate_candidate_score([make_chunk("jane_skills_0", "skills", 0.8)])
        multiple = calculate_candidate_score(
            [
                make_chunk("jane_skills_0", "skills", 0.8),
                make_chunk("jane_experience_1", "experience", 0.75),
            ]
        )
        self.assertGreater(multiple, single)


class TestReasoning(unittest.TestCase):
    def test_build_match_reasoning_includes_sections_and_evidence(self) -> None:
        candidate = CandidateMatch(
            candidate_name="Jane Doe",
            source_file="jane.pdf",
            score=0.82,
            matched_chunks=[
                make_chunk("jane_skills_0", "skills", 0.9, content="Python, FastAPI, PostgreSQL"),
                make_chunk("jane_experience_1", "experience", 0.8, content="Built APIs at Acme Corp"),
            ],
            skills="Python, FastAPI",
            education="B.Tech CS",
            years_of_experience=5,
        )
        reasoning = build_match_reasoning(candidate)
        self.assertIn("Jane Doe", reasoning)
        self.assertIn("Skills", reasoning)
        self.assertIn("Experience", reasoning)
        self.assertIn("Python, FastAPI", reasoning)


class TestParseQueryResults(unittest.TestCase):
    def test_parse_query_results(self) -> None:
        results = {
            "ids": [["jane_skills_0"]],
            "documents": [["Skills:\nPython, FastAPI"]],
            "distances": [[0.2]],
            "metadatas": [[{"candidate_name": "Jane Doe", "source_file": "jane.pdf", "section": "skills"}]],
        }
        chunks = parse_query_results(results)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].content, "Python, FastAPI")
        self.assertEqual(chunks[0].section, "skills")


class TestRankCandidates(unittest.TestCase):
    def test_rank_candidates_orders_by_score(self) -> None:
        grouped = {
            "jane.pdf": [
                make_chunk("jane_skills_0", "skills", 0.9),
                make_chunk("jane_experience_1", "experience", 0.85),
            ],
            "john.pdf": [make_chunk("john_skills_0", "skills", 0.6, candidate_name="John Smith", source_file="john.pdf")],
        }
        ranked = rank_candidates(grouped)
        self.assertEqual(ranked[0].candidate_name, "Jane Doe")
        self.assertTrue(ranked[0].reasoning)


if __name__ == "__main__":
    unittest.main()
