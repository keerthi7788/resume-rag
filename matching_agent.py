from typing import TypedDict, List, Dict, Any

from langgraph.graph import StateGraph, START, END

from job_matcher import JobMatcher
from mcp_client import MCPClient


class AgentState(TypedDict):
    conversation_history: List[str]
    job_description: str
    requirements: Dict[str, Any]
    retrieved_chunks: List[Any]
    ranked_candidates: List[Any]
    report: str
    feedback: str


matcher = JobMatcher()
client = MCPClient()


def parse_jd(state: AgentState):
    print("\nParsing JD...\n")
    return state


def extract_requirements(state: AgentState):
    requirements = client.extract_requirements(
        state["job_description"]
    )

    return {
        **state,
        "requirements": requirements
    }


def search_resumes(state: AgentState):
    chunks = matcher.retrieve_matching_chunks(
        state["job_description"]
    )

    return {
        **state,
        "retrieved_chunks": chunks
    }


def rank_candidates_node(state: AgentState):

    result = matcher.match_with_details(
        state["job_description"]
    )

    print(f"\nCandidates found: {len(result.candidates)}")

    if result.filtered_out:
        print(f"Filtered candidates: {len(result.filtered_out)}")
        for candidate in result.filtered_out[:5]:
            print(candidate)

    return {
        **state,
        "ranked_candidates": result.candidates
    }

def generate_report(state: AgentState):
    report = []

    for candidate in state["ranked_candidates"]:
        report.append(
            f"""
Candidate : {candidate.candidate_name}

Score : {candidate.score}

Experience : {candidate.years_of_experience}

Skills : {candidate.skills}

Reason :

{candidate.reasoning}
"""
        )

    return {
        **state,
        "report": "\n".join(report)
    }


def human_feedback(state: AgentState):
    try:
        feedback = input("\nEnter feedback or press Enter:\n")
    except EOFError:
        feedback = ""

    return {
        **state,
        "feedback": feedback
    }


workflow = StateGraph(AgentState)

workflow.add_node("parse_jd", parse_jd)
workflow.add_node("extract_requirements", extract_requirements)
workflow.add_node("search_resumes", search_resumes)
workflow.add_node("rank_candidates", rank_candidates_node)
workflow.add_node("generate_report", generate_report)
workflow.add_node("human_feedback", human_feedback)

workflow.add_edge(START, "parse_jd")
workflow.add_edge("parse_jd", "extract_requirements")
workflow.add_edge("extract_requirements", "search_resumes")
workflow.add_edge("search_resumes", "rank_candidates")
workflow.add_edge("rank_candidates", "generate_report")
workflow.add_edge("generate_report", "human_feedback")
workflow.add_edge("human_feedback", END)

app = workflow.compile()