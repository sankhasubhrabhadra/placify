import requests
import os

url = 'http://localhost:5000/api/placement-session/create'

# Create a dummy resume text file
with open('dummy_resume.txt', 'w') as f:
    f.write("I am a software engineer with 5 years of Python and React experience.")

files = {'resume': open('dummy_resume.txt', 'rb')}
data = {
    'company': 'Google',
    'role': 'L4 Software Engineer',
    'timeBudget': '120',
    'strengths': 'Strong in arrays, weak in graphs'
}

print("Sending request to create session...")
response = requests.post(url, data=data, files=files)
print("Status Code:", response.status_code)
try:
    print("Response:", response.json())
except Exception as e:
    print("Response text:", response.text)
