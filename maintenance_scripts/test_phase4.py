import requests
import json
import os
import glob

sessions = glob.glob('data/placement_sessions/*.json')
if not sessions:
    print("No sessions found.")
    exit(1)
session_id = os.path.basename(sessions[0]).split('.json')[0]

print(f"Triggering Orchestrator for session {session_id}...")

# 1. Trigger replan to get the baseline plan
print("\\n--- GETTING PLAN 1 ---")
res = requests.post(f'http://localhost:5000/api/placement-session/{session_id}/replan')
data = res.json()
print("Orchestrator Reason:", data.get("reason"))
print("Plan:", json.dumps(data.get("current_plan"), indent=2))

# 2. To simulate skipping baseline, let's inject 8 dummy answers into the history so the orchestrator moves to the gaps
with open(sessions[0], 'r', encoding='utf-8') as f:
    session_data = json.load(f)
    
while len(session_data.get("assessment_history", [])) < 8:
    session_data["assessment_history"].append({
        "type": "baseline_quiz",
        "topic": "Dummy",
        "score_delta": 0
    })

with open(sessions[0], 'w', encoding='utf-8') as f:
    json.dump(session_data, f, indent=2)

print("\\n--- GETTING PLAN 2 (Post-Baseline) ---")
res2 = requests.post(f'http://localhost:5000/api/placement-session/{session_id}/replan')
data2 = res2.json()
print("Orchestrator Reason:", data2.get("reason"))
print("Plan:", json.dumps(data2.get("current_plan"), indent=2))

# 3. Trigger replan again. The previous state was "learning_mode". 
# The orchestrator should now shift to "quiz_mode" for the same topic.
print("\\n--- GETTING PLAN 3 (Shift to Quiz) ---")
res3 = requests.post(f'http://localhost:5000/api/placement-session/{session_id}/replan')
data3 = res3.json()
print("Orchestrator Reason:", data3.get("reason"))
print("Plan:", json.dumps(data3.get("current_plan"), indent=2))
