import re

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

old_prompt = """    prompt = (
        "You are an expert technical interviewer evaluating a mock interview. "
        "Based on the following chat history (which includes system notes on the candidate's posture, dress, and expressions), "
        "provide a comprehensive review.\\n"
        "Include:\\n"
        "1. Feedback on their Dress, Body Posture, and Expressions (if noted in the chat).\\n"
        "2. What technical skills they need to fix or improve based on the questions asked.\\n"
        "3. Overall performance.\\n\\n"
        f"Chat History:\\n{history_text}"
    )"""

new_prompt = """    prompt = (
        "You are a strict technical evaluator. Review the mock interview transcript provided below.\\n\\n"
        "CRITICAL RULES:\\n"
        "1. DO NOT make up or hallucinate any questions, answers, or topics that are not explicitly written in the Chat History.\\n"
        "2. If the Chat History is very short (e.g. just a 'hello'), clearly state that the interview was too short or abandoned, and give a score of N/A.\\n"
        "3. Otherwise, provide feedback based ONLY on the actual questions asked and the candidate's actual answers.\\n\\n"
        "Format your review with:\\n"
        "- Posture & Presentation (Based only on [SYSTEM OBSERVATION] notes)\\n"
        "- Technical Areas to Improve\\n"
        "- Overall Summary\\n\\n"
        f"Chat History:\\n{history_text}"
    )"""

code = code.replace(old_prompt, new_prompt)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated prompt!")
