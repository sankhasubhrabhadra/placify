import os

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Change the default models to valid Groq models
code = code.replace(
    "GROQ_MODEL = os.environ.get('GROQ_MODEL', 'openai/gpt-oss-20b')",
    "GROQ_MODEL = os.environ.get('GROQ_MODEL', 'llama-3.1-8b-instant')"
)
code = code.replace(
    "GROQ_FALLBACK_MODEL = os.environ.get('GROQ_FALLBACK_MODEL', 'openai/gpt-oss-120b')",
    "GROQ_FALLBACK_MODEL = os.environ.get('GROQ_FALLBACK_MODEL', 'llama-3.1-70b-versatile')"
)

# And if they happen to use the mock fallback, let's just make it return a fallback string instead of 503 so their hackathon demo doesn't crash completely.
# Actually, the user explicitly asked in Phase 1: "return None on total failure instead of an '⚠️ ...' string... check if response_text is None: and return a proper jsonify({'success': False, 'error': '...'}), 503"
# So returning 503 is what they explicitly requested. I should stick to that, but changing the models might fix the issue if Groq's API is strict about model strings before key validation.

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated models in app.py")
