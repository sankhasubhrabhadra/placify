import re

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# I will replace the block from "else:" to the end of the system_prompt declaration
old_block = r"else:\s+system_prompt = \([\s\S]*?Keep your responses under 150 words\.\"\s+\)"

new_block = """else:
        system_prompt = (
            f"You are a strict, professional interviewer at a top tech company conducting an interview on: {topic}. "
            "CRITICAL RULES: "
            "1. YOU ARE THE INTERVIEWER, the user is the candidate. "
            "2. YOU MUST ASK THE QUESTIONS. Never ask the candidate to ask you a question. "
            "3. Ask one question at a time, wait for the candidate to answer, then evaluate or ask a follow-up. "
            "4. Keep your responses under 100 words. Be concise."
        )"""

code = re.sub(old_block, new_block, code)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Replaced system prompt using regex.")
