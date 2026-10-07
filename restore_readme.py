import re

file_path = 'README.md'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

old_text = "*(Note: The legacy \"Resume Scanner\" feature has been deprecated and removed to maintain focus on live interview and coding performance).*"
new_text = "- 📄 **Resume Scanner (`jobs.html`)**: Parses resumes and scores your fit against target roles. Skills are cross-checked against your actual solved-problem history from the coding practice module."

code = code.replace(old_text, new_text)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)
