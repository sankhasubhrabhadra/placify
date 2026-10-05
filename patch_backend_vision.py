import os
import re

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Add endpoints to app.py
analyze_frame_code = """
@app.route('/api/interviews/session/analyze_frame', methods=['POST'])
def analyze_frame():
    data = request.json or {}
    image_b64 = data.get('image', '')
    if not image_b64:
        return jsonify({'success': False, 'error': 'No image provided'}), 400
        
    image_b64 = image_b64.split(',')[-1] # Remove data URI prefix if present
    
    ollama_url = "http://localhost:11434/api/generate"
    payload = {
        "model": "moondream",
        "prompt": "Describe the person's dress, body posture, and facial expression. Are they professional, confident, or nervous? Keep it to one short sentence.",
        "images": [image_b64],
        "stream": False
    }
    try:
        response = requests.post(ollama_url, json=payload, timeout=30)
        response.raise_for_status()
        observation = response.json().get('response', '').strip()
        return jsonify({'success': True, 'observation': observation})
    except Exception as e:
        app.logger.error(f"Vision error: {e}")
        return jsonify({'success': False, 'error': 'Vision analysis failed'}), 500

@app.route('/api/interviews/session/end', methods=['POST'])
def end_interview():
    data = request.json or {}
    messages = data.get('messages', [])
    if not messages:
        return jsonify({'success': False, 'error': 'No messages'}), 400
        
    history_text = ""
    for m in messages:
        role = "Interviewer" if m['role'] == 'assistant' else "Candidate"
        history_text += f"{role}: {m['content']}\\n"
        
    prompt = (
        "You are an expert technical interviewer evaluating a mock interview. "
        "Based on the following chat history (which includes system notes on the candidate's posture, dress, and expressions), "
        "provide a comprehensive review.\\n"
        "Include:\\n"
        "1. Feedback on their Dress, Body Posture, and Expressions (if noted in the chat).\\n"
        "2. What technical skills they need to fix or improve based on the questions asked.\\n"
        "3. Overall performance.\\n\\n"
        f"Chat History:\\n{history_text}"
    )
    
    response_text = ask_groq(prompt, "Please generate the review.")
    if response_text is None:
        return jsonify({'success': False, 'error': 'AI service is temporarily unavailable.'}), 503
        
    return jsonify({'success': True, 'review': response_text})
"""

if "/api/interviews/session/analyze_frame" not in code:
    code = code + "\n" + analyze_frame_code

# Also update the chat endpoint to accept vision_context
old_chat = """    final_prompt = system_prompt
    if history_text:
        final_prompt += f"\\n\\nChat History:\\n{history_text}\""""

new_chat = """    vision_context = data.get('vision_context', '')
    final_prompt = system_prompt
    if vision_context:
        final_prompt += f"\\n\\n[SYSTEM OBSERVATION: {vision_context} - If they look unprofessional, nervous, or distracted, subtly call it out as a real interviewer would.]"
    if history_text:
        final_prompt += f"\\n\\nChat History:\\n{history_text}\""""

code = code.replace(old_chat, new_chat)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Backend patched for vision and end interview.")
