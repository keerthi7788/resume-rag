from matching_agent import app

print("Paste Job Description and press Ctrl+D (Linux/Mac) or Ctrl+Z then Enter (Windows):\n")

try:
    while True:
        jd = input() + "\n"
except EOFError:
    pass

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

print("\n==============================")
print("MATCH REPORT")
print("==============================\n")

print(result["report"])