import os

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# We want to replace everything from "# Ask Groq" down to the end of the interview_session_chat function
start_marker = "    # Ask Groq"
end_marker = "    return jsonify({'success': True, 'response': response_text})"

start_idx = code.find(start_marker)
end_idx = code.find(end_marker, start_idx) + len(end_marker)

new_code = """    # Directly format messages for Ollama API to avoid role confusion
    ollama_messages = [{"role": "system", "content": final_prompt}]
    
    # Pass actual message array
    for m in messages:
        # Ensure roles map to what Ollama expects: 'user' or 'assistant'
        role = 'assistant' if m['role'] == 'assistant' else 'user'
        ollama_messages.append({"role": role, "content": m['content']})
        
    payload = {
        "model": os.environ.get('OLLAMA_MODEL', 'qwen2.5:1.5b'),
        "messages": ollama_messages,
        "stream": False,
        "options": {
            "temperature": 0.7
        }
    }
    
    try:
        response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=60)
        response.raise_for_status()
        response_text = response.json()['message']['content'].strip()
        return jsonify({'success': True, 'response': response_text})
    except Exception as e:
        app.logger.error(f"Chat error: {e}")
        return jsonify({'success': False, 'error': 'AI service is temporarily unavailable.'}), 503"""

if start_idx != -1 and end_idx != -1:
    # Also we need to strip out the history_text construction before final_prompt
    
    # Just replace the whole chunk
    code = code[:start_idx] + new_code + code[end_idx:]
    
    # Remove history_text block
    history_block = """    history_text = ""
    for m in messages[:-1]:
        role = "Interviewer" if m['role'] == 'assistant' else "Candidate"
        history_text += f"{role}: {m['content']}\\n"
        
    last_user_message = messages[-1]['content']
    
    vision_context = data.get('vision_context', '')
    final_prompt = system_prompt
    if vision_context:
        final_prompt += f"\\n\\n[SYSTEM OBSERVATION: {vision_context} - If they look unprofessional, nervous, or distracted, subtly call it out as a real interviewer would.]"
    if history_text:
        final_prompt += f"\\n\\nChat History:\\n{history_text}\""""
    
    new_history_block = """    vision_context = data.get('vision_context', '')
    final_prompt = system_prompt
    if vision_context:
        final_prompt += f"\\n\\n[SYSTEM OBSERVATION: {vision_context} - If they look unprofessional, nervous, or distracted, subtly call it out as a real interviewer would.]\""""
        
    code = code.replace(history_block, new_history_block)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(code)
    print("Successfully replaced.")
else:
    print("Could not find markers.")
