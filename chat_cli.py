from matching_agent import app
import sys

print("Paste JD and press Ctrl+D when done:\n")

jd = sys.stdin.read()

state = {
    "conversation_history": [],
    "job_description": jd,
    "requirements": {},
    "retrieved_chunks": [],
    "ranked_candidates": [],
    "report": "",
    "feedback": ""
}

result = app.invoke(state)

print("\n===== MATCH REPORT =====\n")
print(result["report"])