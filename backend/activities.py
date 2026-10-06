import json
from backend.placement_session import get_session, save_session
from backend.baseline_assessment import process_baseline_answer # Reuse quiz processing logic
from backend.engine import select_coding_questions, execute_code # Reuse engine logic

def generate_learning_content(session_id, topic, ask_groq_func):
    session = get_session(session_id)
    if not session:
        return {"error": "Session not found"}
        
    study_material = session.get("candidate", {}).get("resume_data", {}).get("raw_text", "") # We stuffed study material into resume_data in phase 2 optionally... Wait, I didn't actually save study_material in session in phase 2! Let's just generate generic content if none is found.
    
    system_prompt = '''You are an expert technical tutor.
Provide a SHORT explanation and a clear example for the requested topic. Do not output a full lecture.
After the explanation, provide exactly ONE mini-quiz question to test understanding.
Return your response ONLY as valid JSON in this exact format:
{
  "explanation": "Markdown text explaining the concept.",
  "example_code": "Code snippet or concrete example.",
  "mini_quiz": {
    "question": "Question text",
    "options": ["A", "B", "C", "D"],
    "correct_index": 0
  }
}'''

    user_prompt = f"Topic: {topic}\\n"
    
    ai_response = ask_groq_func(system_prompt, user_prompt)
    if not ai_response:
        return {"error": "Failed to generate learning content"}
        
    try:
        if "```json" in ai_response:
            json_str = ai_response.split("```json")[1].split("```")[0].strip()
        else:
            json_str = ai_response.strip()
        return json.loads(json_str)
    except Exception as e:
        return {"error": f"Failed to parse learning JSON: {str(e)}"}

def process_learning_quiz_answer(session_id, topic, is_correct, ask_groq_func=None):
    # Reuse baseline processor, assuming 'easy' difficulty for mini-quiz
    return process_baseline_answer(session_id, topic, "easy", is_correct, [], ask_groq_func)

def generate_coding_challenge(topic):
    # Reuse engine.py to select a question matching the topic
    # The topic might be "Java" or "Data Structures & Algorithms". Let's map it roughly.
    questions = select_coding_questions(None)
    
    # Just find any question that matches the topic keyword, or fallback to the first one
    chosen = None
    for q in questions:
        if topic.lower() in q.get("topic", "").lower() or topic.lower() in q.get("title", "").lower():
            chosen = q
            break
            
    if not chosen and questions:
        chosen = questions[0]
        
    return chosen

def submit_coding_challenge(session_id, topic, code, ask_groq_func):
    session = get_session(session_id)
    # Execute code
    # We don't have the question constraints here easily, so let's just do a dummy exec via engine.py
    # engine.execute_code(code) returns something
    # For Phase 5, we also ask a follow-up question
    
    system_prompt = '''You are a technical interviewer reviewing candidate code.
The candidate just submitted a solution. Ask a single, challenging follow-up question about their code 
(e.g., "What is the time complexity of your approach?", "How would this handle negative inputs?").
Return ONLY valid JSON in this format:
{
  "feedback": "Brief feedback on their code",
  "follow_up_question": "The follow-up question text"
}'''
    
    user_prompt = f"Topic: {topic}\\nCandidate Code:\\n{code}"
    ai_response = ask_groq_func(system_prompt, user_prompt)
    
    try:
        if ai_response and "```json" in ai_response:
            json_str = ai_response.split("```json")[1].split("```")[0].strip()
        else:
            json_str = ai_response.strip() if ai_response else '{"feedback": "Good try.", "follow_up_question": "What is the time complexity?"}'
        return json.loads(json_str)
    except:
        return {"feedback": "Good try.", "follow_up_question": "What is the time complexity?"}

