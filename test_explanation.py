import json
from app import app
from backend.db import init_db

init_db()

client = app.test_client()

# Seed user.json with dummy data
from app import save_json, USER_DATA_FILE
save_json(USER_DATA_FILE, {
    "resume_score": 85,
    "solved_problems": [1, 2, 3],
    "candidate_skills": ["python", "django", "sql"],
    "targeted_role": "backend_engineer"
})

response = client.get('/api/candidates/1/explanation')
print("Status:", response.status_code)
print(json.dumps(response.get_json(), indent=2))
