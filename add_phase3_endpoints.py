import re

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

if "from backend.baseline_assessment import get_next_baseline_question, process_baseline_answer, compute_skill_gaps" not in code:
    code = code.replace("from backend.placement_session", "from backend.baseline_assessment import get_next_baseline_question, process_baseline_answer, compute_skill_gaps\nfrom backend.placement_session")

new_routes = """
# PLACEMENT SESSION PHASE 3 (BASELINE)
@app.route('/api/placement-session/<session_id>/baseline/next', methods=['GET'])
def api_placement_session_baseline_next(session_id):
    try:
        result = get_next_baseline_question(session_id, ask_groq)
        if "error" in result:
            return jsonify({"success": False, "error": result["error"]}), 500
        return jsonify({"success": True, "result": result})
    except Exception as e:
        app.logger.error(f"Error in baseline next: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/placement-session/<session_id>/baseline/answer', methods=['POST'])
def api_placement_session_baseline_answer(session_id):
    try:
        data = request.json
        topic = data.get("topic")
        difficulty = data.get("difficulty")
        is_correct = data.get("is_correct")
        mistakes = data.get("mistakes", [])
        
        gaps = process_baseline_answer(session_id, topic, difficulty, is_correct, mistakes, ask_groq)
        return jsonify({"success": True, "skill_gaps": gaps})
    except Exception as e:
        app.logger.error(f"Error in baseline answer: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
"""

if "/api/placement-session/<session_id>/baseline/next" not in code:
    code = code.replace("if __name__ == '__main__':", new_routes + "\nif __name__ == '__main__':")
    
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Added Phase 3 endpoints to app.py")
