import json
from app import app
from backend.db import init_db

init_db()

client = app.test_client()

response = client.post('/api/candidates/1/simulate', json={"skills": ["api"]})
print("Status:", response.status_code)
data = response.get_json()
if data:
    print("Score Impact of top skill:", data['recommendations'][0]['score_impact'])
    print("Original Score:", data['original']['final_score'])
    print("Simulated Score:", data['simulated']['final_score'])
