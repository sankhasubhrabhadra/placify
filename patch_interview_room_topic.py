import os

file_path = 'frontend/interview_room.html'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

old_fetch_end = """        body: JSON.stringify({ messages: chatMessages })"""
new_fetch_end = """        body: JSON.stringify({ messages: chatMessages, topic: topic })"""
code = code.replace(old_fetch_end, new_fetch_end)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("interview_room.html patched!")
