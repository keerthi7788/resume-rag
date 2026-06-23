from typing import TypedDict, List, Dict, Any

from langgraph.graph import StateGraph, START, END

from requirement_parser import parse_must_have_requirements
from job_matcher import JobMatcher


# -------------------------
# Agent State
# -------------------------

class AgentState(TypedDict):

    conversation_history: List[str]

    job_description: str

    requirements: Dict[str, Any]

    retrieved_chunks: List[Any]

    ranked_candidates: List[Any]

    report: str

    feedback: str


matcher = JobMatcher()


# -------------------------
# Node 1
# Parse JD
# -------------------------

def parse_jd(state: AgentState):

    jd = state["job_description"]

    print("\nParsing JD...\n")

    return {
        **state
    }


# -------------------------
# Node 2
# Extract Requirements
# -------------------------

def extract_requirements(state: AgentState):

    req = parse_must_have_requirements(
        state["job_description"]
    )

    return {
        **state,
        "requirements": req.to_dict()
        if hasattr(req, "to_dict")
        else req
    }


# -------------------------
# Node 3
# Search resumes
# -------------------------

def search_resumes(state: AgentState):

    chunks = matcher.retrieve_matching_chunks(
        state["job_description"]
    )

    return {
        **state,
        "retrieved_chunks": chunks
    }


# -------------------------
# Node 4
# Rank candidates
# -------------------------

def rank_candidates_node(state: AgentState):

    result = matcher.match_with_details(
        state["job_description"]
    )

    return {
        **state,
        "ranked_candidates": result.candidates
    }


# -------------------------
# Node 5
# Generate Report
# -------------------------

def generate_report(state: AgentState):

    report = []

    for c in state["ranked_candidates"]:

        report.append(
            f"""
Candidate : {c.candidate_name}

Score : {c.score}

Experience : {c.years_of_experience}

Skills : {c.skills}

Reason :

{c.reasoning}
"""
        )

    return {

        **state,

        "report": "\n".join(report)
    }


# -------------------------
# Node 6
# Human Feedback
# -------------------------

# -------------------------
# Node 6
# Human Feedback
# -------------------------

def human_feedback(state: AgentState):

    try:
        feedback = input(
            "\nEnter feedback or press Enter:\n"
        )

    except EOFError:
        feedback = ""

    return {

        **state,

        "feedback": feedback
    }

# -------------------------
# Build Graph
# -------------------------

workflow = StateGraph(AgentState)


workflow.add_node("parse_jd", parse_jd)

workflow.add_node(
    "extract_requirements",
    extract_requirements
)

workflow.add_node(
    "search_resumes",
    search_resumes
)

workflow.add_node(
    "rank_candidates",
    rank_candidates_node
)

workflow.add_node(
    "generate_report",
    generate_report
)

workflow.add_node(
    "human_feedback",
    human_feedback
)


workflow.add_edge(
    START,
    "parse_jd"
)

workflow.add_edge(
    "parse_jd",
    "extract_requirements"
)

workflow.add_edge(
    "extract_requirements",
    "search_resumes"
)

workflow.add_edge(
    "search_resumes",
    "rank_candidates"
)

workflow.add_edge(
    "rank_candidates",
    "generate_report"
)

workflow.add_edge(
    "generate_report",
    "human_feedback"
)

workflow.add_edge(
    "human_feedback",
    END
)


app = workflow.compile()