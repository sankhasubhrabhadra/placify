import re

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# We need to insert final_prompt and vision_context definition before ollama_messages
missing_code = """
    vision_context = data.get('vision_context', '')
    final_prompt = system_prompt
    if vision_context:
        final_prompt += f"\\n\\n[SYSTEM OBSERVATION: {vision_context} - If they look unprofessional, nervous, or distracted, subtly call it out as a real interviewer would.]"
        
"""

# Insert it right before "    # Directly format messages for Ollama API"
target = "    # Directly format messages for Ollama API"
code = code.replace(target, missing_code + target)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed final_prompt NameError in app.py")
