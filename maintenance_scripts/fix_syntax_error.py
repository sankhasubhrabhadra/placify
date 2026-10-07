import re

with open('frontend/script.js', 'r', encoding='utf-8') as f:
    code = f.read()

# I accidentally deleted the `try {` block before `const response = await fetch` in the Resume Scanner.
# The code currently looks like this:
#
#       const response = await fetch(API_BASE + '/api/resume/scan', {
#         method: 'POST',
#         headers: { 'Content-Type': 'application/json' },
#         body: JSON.stringify(payload)
#       });
#       const data = await response.json();
#       ...
#       } catch (err) {
#
# I need to wrap it in a try { block.
# Actually, I'll just find `const response = await fetch(API_BASE + '/api/resume/scan'` and add `try {` above it.

regex = re.compile(r"(const response = await fetch\(API_BASE \+ '/api/resume/scan')")
code = regex.sub(r"try {\n      \1", code)

with open('frontend/script.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed missing try block syntax error in script.js")
