import re

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

if "from backend.readiness import generate_readiness_report, simulate_what_if" not in code:
    code = code.replace("from backend.activities import", "from backend.readiness import generate_readiness_report, simulate_what_if\nfrom backend.activities import")

new_routes = """
# PLACEMENT SESSION PHASE 6 (READINESS)
@app.route('/api/placement-session/<session_id>/readiness-report', methods=['GET'])
def api_placement_session_readiness(session_id):
    report = generate_readiness_report(session_id)
    if "error" in report:
        return jsonify({"success": False, "error": report["error"]}), 500
    return jsonify({"success": True, "report": report})

@app.route('/api/placement-session/<session_id>/simulate', methods=['GET'])
def api_placement_session_simulate(session_id):
    skill = request.args.get('skill', '')
    sim = simulate_what_if(session_id, skill)
    if "error" in sim:
        return jsonify({"success": False, "error": sim["error"]}), 500
    return jsonify({"success": True, "simulation": sim})
"""

if "/api/placement-session/<session_id>/readiness-report" not in code:
    code = code.replace("if __name__ == '__main__':", new_routes + "\nif __name__ == '__main__':")
    
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Added Phase 6 endpoints to app.py")
