import requests
import json
import os
import glob

# Find the session we created in Phase 2
sessions = glob.glob('data/placement_sessions/*.json')
if not sessions:
    print("No sessions found.")
    exit(1)
    
session_id = os.path.basename(sessions[0]).split('.json')[0]

print(f"Testing baseline assessment for session {session_id}...")

# 1. Ask for next question
print("\\n--- GETTING NEXT QUESTION ---")
res = requests.get(f'http://localhost:5000/api/placement-session/{session_id}/baseline/next')
data = res.json()
print("Response:", json.dumps(data, indent=2))

if not data.get("success") or data.get("result", {}).get("done"):
    print("Done or error.")
    exit(1)
    
q_data = data["result"]["question"]
topic = q_data["topic"]
difficulty = q_data["difficulty"]

# 2. Submit a WRONG answer to test difficulty branching down
print(f"\\n--- SUBMITTING WRONG ANSWER FOR {topic} ---")
ans_res = requests.post(
    f'http://localhost:5000/api/placement-session/{session_id}/baseline/answer',
    json={
        "topic": topic,
        "difficulty": difficulty,
        "is_correct": False,
        "mistakes": ["Chose the wrong multiple choice option"]
    }
)
ans_data = ans_res.json()
print("Skill Gaps Updated:", json.dumps(ans_data["skill_gaps"], indent=2))

# 3. Ask for next question (should be a different topic, or if same topic, lower difficulty)
print("\\n--- GETTING NEXT QUESTION ---")
res2 = requests.get(f'http://localhost:5000/api/placement-session/{session_id}/baseline/next')
data2 = res2.json()
print("Response:", json.dumps(data2, indent=2))

# 4. Submit CORRECT answer
print(f"\\n--- SUBMITTING CORRECT ANSWER ---")
ans2_res = requests.post(
    f'http://localhost:5000/api/placement-session/{session_id}/baseline/answer',
    json={
        "topic": data2["result"]["question"]["topic"],
        "difficulty": data2["result"]["question"]["difficulty"],
        "is_correct": True,
        "mistakes": []
    }
)
print("Skill Gaps Updated:", json.dumps(ans2_res.json()["skill_gaps"], indent=2))
