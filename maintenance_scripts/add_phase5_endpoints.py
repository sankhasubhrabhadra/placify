import re

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

if "from backend.activities import generate_learning_content" not in code:
    code = code.replace("from backend.orchestrator import replan_roadmap", "from backend.activities import generate_learning_content, process_learning_quiz_answer, generate_coding_challenge, submit_coding_challenge\nfrom backend.orchestrator import replan_roadmap")

new_routes = """
# PLACEMENT SESSION PHASE 5 (ACTIVITIES)
@app.route('/api/placement-session/<session_id>/learning', methods=['GET'])
def api_placement_session_learning(session_id):
    topic = request.args.get('topic', 'General')
    try:
        content = generate_learning_content(session_id, topic, ask_groq)
        if "error" in content:
            return jsonify({"success": False, "error": content["error"]}), 500
        return jsonify({"success": True, "content": content})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/placement-session/<session_id>/learning/answer', methods=['POST'])
def api_placement_session_learning_answer(session_id):
    data = request.json
    topic = data.get("topic")
    is_correct = data.get("is_correct")
    gaps = process_learning_quiz_answer(session_id, topic, is_correct, ask_groq)
    return jsonify({"success": True, "skill_gaps": gaps})

@app.route('/api/placement-session/<session_id>/coding', methods=['GET'])
def api_placement_session_coding(session_id):
    topic = request.args.get('topic', 'General')
    question = generate_coding_challenge(topic)
    return jsonify({"success": True, "question": question})

@app.route('/api/placement-session/<session_id>/coding/submit', methods=['POST'])
def api_placement_session_coding_submit(session_id):
    data = request.json
    topic = data.get("topic")
    code_text = data.get("code")
    feedback = submit_coding_challenge(session_id, topic, code_text, ask_groq)
    # Give candidate a score bump for coding
    process_baseline_answer(session_id, topic, "hard", True, [], ask_groq)
    return jsonify({"success": True, "feedback": feedback})
"""

if "/api/placement-session/<session_id>/learning" not in code:
    code = code.replace("if __name__ == '__main__':", new_routes + "\nif __name__ == '__main__':")
    
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Added Phase 5 endpoints to app.py")
