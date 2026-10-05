file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

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

with open('.env.example', 'a', encoding='utf-8') as f:
    f.write('GROQ_MODEL=openai/gpt-oss-20b\n')

print("Patch applied successfully.")
