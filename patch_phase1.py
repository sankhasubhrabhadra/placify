import os

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add GROQ_MODEL constants
code = code.replace("GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')\n",
                    "GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')\n"
                    "GROQ_MODEL = os.environ.get('GROQ_MODEL', 'openai/gpt-oss-20b')\n"
                    "GROQ_FALLBACK_MODEL = os.environ.get('GROQ_FALLBACK_MODEL', 'openai/gpt-oss-120b')\n")

# 2. Rewrite ask_groq
old_ask_groq = """def ask_groq(system_prompt, user_message, model='llama3-8b-8192'):
    if groq_client:
        try:
            completion = groq_client.chat.completions.create(
                model=model,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user',   'content': user_message}
                ],
                max_tokens=512,
                temperature=0.7,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            app.logger.error(f'Groq error: {e}')
            return f"⚠️ Groq API Error: {str(e)}. Please check your API key and rate limits."

    if not GROQ_API_KEY:
        return "⚠️ GROQ_API_KEY is not set in the environment variables. Please add it to your Render dashboard."
        
    return "⚠️ Groq is not available. Please check your requirements and API key.""""

new_ask_groq = """def ask_groq(system_prompt, user_message, model=None):
    if not GROQ_AVAILABLE or not GROQ_API_KEY or not groq_client:
        app.logger.error('Groq is not available or missing API key.')
        return None

    models_to_try = [model] if model else [GROQ_MODEL, GROQ_FALLBACK_MODEL]
    for m in models_to_try:
        try:
            completion = groq_client.chat.completions.create(
                model=m,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user',   'content': user_message}
                ],
                max_tokens=512,
                temperature=0.7,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            app.logger.error(f'Groq error with model {m}: {e}')
    
    return None"""

if old_ask_groq in code:
    code = code.replace(old_ask_groq, new_ask_groq)
else:
    print("Could not find old_ask_groq")

# 3. Update callers

code = code.replace(
    "    response_text = ask_groq(system_prompt, full_message)\n"
    "    chat_hist.append({'role': 'assistant', 'content': response_text})",
    "    response_text = ask_groq(system_prompt, full_message)\n"
    "    if response_text is None:\n"
    "        return jsonify({'success': False, 'error': 'AI service is temporarily unavailable.'}), 503\n"
    "    chat_hist.append({'role': 'assistant', 'content': response_text})"
)

code = code.replace(
    "        hint = ask_groq(system_prompt, user_msg)\n"
    "        return jsonify({'success': True, 'hint': hint})",
    "        hint = ask_groq(system_prompt, user_msg)\n"
    "        if hint is None:\n"
    "            return jsonify({'success': False, 'error': 'AI service is temporarily unavailable.'}), 503\n"
    "        return jsonify({'success': True, 'hint': hint})"
)

code = code.replace(
    "    feedback_text = ask_groq(system_prompt, f'Topic: {topic}\\n\\n{qa_text}', model='llama3-8b-8192')\n"
    "    score_match = re.search(r'SCORE:\\s*(\\d+)/10', feedback_text)",
    "    feedback_text = ask_groq(system_prompt, f'Topic: {topic}\\n\\n{qa_text}')\n"
    "    if feedback_text is None:\n"
    "        return jsonify({'success': False, 'error': 'AI service is temporarily unavailable.'}), 503\n"
    "    score_match = re.search(r'SCORE:\\s*(\\d+)/10', feedback_text)"
)

code = code.replace(
    "    response_text = ask_groq(final_prompt, last_user_message)\n"
    "    return jsonify({'success': True, 'response': response_text})",
    "    response_text = ask_groq(final_prompt, last_user_message)\n"
    "    if response_text is None:\n"
    "        return jsonify({'success': False, 'error': 'AI service is temporarily unavailable.'}), 503\n"
    "    return jsonify({'success': True, 'response': response_text})"
)

code = code.replace(
    "            ai_feedback = ask_groq(\n"
    "                'You are a senior technical recruiter. Review the resume and provide actionable feedback in 3 bullet points.',\n"
    "                f'Resume:\\n{text[:2000]}\\n\\nGive 3 specific improvement tips.')\n"
    "        return jsonify({'success': True, **result, 'ai_feedback': ai_feedback})",
    "            ai_feedback = ask_groq(\n"
    "                'You are a senior technical recruiter. Review the resume and provide actionable feedback in 3 bullet points.',\n"
    "                f'Resume:\\n{text[:2000]}\\n\\nGive 3 specific improvement tips.')\n"
    "            if ai_feedback is None:\n"
    "                return jsonify({'success': False, 'error': 'AI service is temporarily unavailable.'}), 503\n"
    "        return jsonify({'success': True, **result, 'ai_feedback': ai_feedback})"
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Patched app.py")

with open('.env.example', 'a') as f:
    f.write('GROQ_MODEL=openai/gpt-oss-20b\n')
print("Added to .env.example")
