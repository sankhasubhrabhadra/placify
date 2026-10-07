import requests
res = requests.post('http://localhost:5000/api/resume/scan', data={'text': 'Test resume text.'})
print(res.status_code, res.text)
