import re
with open('frontend/script.js', 'r', encoding='utf-8') as f:
    code = f.read()

pattern = r'<button class="btn btn-outline" style="padding: 0\.25rem 0\.5rem; font-size: 0\.75rem;">View\s*Feedback</button>'
replacement = r'<button class="btn btn-outline" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;" onclick="viewFeedback(${p.id})">View Feedback</button>'

code = re.sub(pattern, replacement, code)

with open('frontend/script.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("regex matched and replaced!")
