import re

file_path = 'frontend/interview_room.html'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Update the end fetch payload
old_end_payload = "body: JSON.stringify({ messages: chatMessages, topic: topic })"
new_end_payload = "body: JSON.stringify({ messages: chatMessages, topic: topic, vision_context: visionContext })"

code = code.replace(old_end_payload, new_end_payload)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

old_end_interview = """def end_interview():
    data = request.json or {}
    messages = data.get('messages', [])
    topic = data.get('topic', 'General')"""
new_end_interview = """def end_interview():
    data = request.json or {}
    messages = data.get('messages', [])
    topic = data.get('topic', 'General')
    vision_context = data.get('vision_context', '')"""

code = code.replace(old_end_interview, new_end_interview)

old_end_prompt = """        f"Chat History:\\n{history_text}"
    )"""
new_end_prompt = """        f"Chat History:\\n{history_text}\\n"
        f"[SYSTEM OBSERVATION OF CANDIDATE]: {vision_context}\\n"
    )"""

code = code.replace(old_end_prompt, new_end_prompt)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated end interview to include vision context.")
