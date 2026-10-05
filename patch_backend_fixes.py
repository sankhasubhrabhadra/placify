import os

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Fix 1: System prompt for conversational interview
old_conversational_prompt = """          system_prompt = (
              f"You are an interviewer at a top tech company conducting a conversational interview on the topic: {topic}. "
              "Act like a real interviewer: ask one question at a time, wait for the candidate's response, and ask probing follow-up questions. "
              "Be concise, professional, and do not break character. Keep your responses under 150 words."
          )"""
new_conversational_prompt = """          system_prompt = (
              f"You are a strict, professional interviewer at a top tech company conducting an interview on: {topic}. "
              "CRITICAL RULES: "
              "1. YOU ARE THE INTERVIEWER, the user is the candidate. "
              "2. YOU MUST ASK THE QUESTIONS. Never ask the candidate to ask you a question. "
              "3. Ask one question at a time, wait for the candidate to answer, then evaluate or ask a follow-up. "
              "4. Keep your responses under 100 words. Be concise."
          )"""
code = code.replace(old_conversational_prompt, new_conversational_prompt)

# Fix 2: end_interview saving feedback
# Update route signature to accept topic
old_end_interview = """def end_interview():
    data = request.json or {}
    messages = data.get('messages', [])
    if not messages:
        return jsonify({'success': False, 'error': 'No messages'}), 400"""
new_end_interview = """def end_interview():
    data = request.json or {}
    messages = data.get('messages', [])
    topic = data.get('topic', 'General')
    if not messages:
        return jsonify({'success': False, 'error': 'No messages'}), 400"""
code = code.replace(old_end_interview, new_end_interview)

# Update return of end_interview to save to sessions.json
old_return = """    if response_text is None:
        return jsonify({'success': False, 'error': 'AI service is temporarily unavailable.'}), 503
        
    return jsonify({'success': True, 'review': response_text})"""
new_return = """    if response_text is None:
        return jsonify({'success': False, 'error': 'AI service is temporarily unavailable.'}), 503
        
    # Save the generated review
    import datetime
    path = os.path.join(INTERVIEWS_DIR, 'sessions.json')
    iv_data = load_json(path, {'upcoming': [], 'past': []})
    new_id = max([i.get('id',0) for i in iv_data.get('upcoming',[]) + iv_data.get('past',[])], default=0) + 1
    iv_data['past'].insert(0, {
        'id': new_id, 
        'topic': topic, 
        'date': datetime.datetime.now().strftime('%B %d, %Y'), 
        'rating': 'N/A', 
        'feedback': response_text
    })
    save_json(path, iv_data)
    
    return jsonify({'success': True, 'review': response_text})"""
code = code.replace(old_return, new_return)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("app.py patched!")
