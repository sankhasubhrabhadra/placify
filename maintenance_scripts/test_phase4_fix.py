import requests
import json
import os
import glob

sessions = glob.glob('data/placement_sessions/*.json')
session_id = os.path.basename(sessions[0]).split('.json')[0]

print("\\n--- GETTING PLAN 4 (Should shift to Quiz now) ---")
res = requests.post(f'http://localhost:5000/api/placement-session/{session_id}/replan')
data = res.json()
print("Orchestrator Reason:", data.get("reason"))
print("Plan:", json.dumps(data.get("current_plan"), indent=2))
