import re

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

if "from backend.orchestrator import replan_roadmap" not in code:
    code = code.replace("from backend.placement_session", "from backend.orchestrator import replan_roadmap\nfrom backend.placement_session")

new_routes = """
# PLACEMENT SESSION PHASE 4 (ORCHESTRATOR)
@app.route('/api/placement-session/<session_id>/replan', methods=['POST'])
def api_placement_session_replan(session_id):
    try:
        session_data = get_session(session_id)
        if not session_data:
            return jsonify({"success": False, "error": "Session not found"}), 404
            
        new_plan, reason = replan_roadmap(session_data)
        
        # Save state
        save_session(session_id, session_data)
        
        return jsonify({
            "success": True, 
            "current_plan": new_plan,
            "reason": reason
        })
    except Exception as e:
        app.logger.error(f"Error in replan: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
"""

if "/api/placement-session/<session_id>/replan" not in code:
    code = code.replace("if __name__ == '__main__':", new_routes + "\nif __name__ == '__main__':")
    
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Added Phase 4 endpoints to app.py")
