from tools import (
    extract_requirements,
    compare_candidates,
    generate_interview_questions,
)


class MCPClient:
    """
    MCP Client.

    Currently forwards requests to the local MCP tool
    implementations.

    Later this class can be replaced with a real MCP
    transport (HTTP/stdio) without changing the agent.
    """

    def extract_requirements(self, job_description: str):
        return extract_requirements(job_description)

    def compare_candidates(self, candidate_ids: list[str]):
        return compare_candidates(candidate_ids)

    def generate_interview_questions(self, candidate_id: str):
        return generate_interview_questions(candidate_id)