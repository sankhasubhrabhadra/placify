import json
from app import app
from backend.db import init_db

init_db()
client = app.test_client()

# Check explanation endpoint explicitly
response = client.get('/api/candidates/1/explanation')
print("Explanation Status:", response.status_code)

# Check dashboard stats
stats_response = client.get('/api/dashboard/stats')
print("Stats Status:", stats_response.status_code)

# Check dashboard progress
prog_response = client.get('/api/dashboard/progress')
print("Progress Status:", prog_response.status_code)
