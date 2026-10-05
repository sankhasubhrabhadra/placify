from app import app
import json

client = app.test_client()
response = client.post('/api/chat', json={'message': 'Hello AI coach!'})
print("Status:", response.status_code)
print("Data:", response.get_json())
