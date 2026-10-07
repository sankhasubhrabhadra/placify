import re

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Make sure backend.placement_session is imported
if "from backend.placement_session import create_session, get_session, save_session" not in code:
    code = code.replace("import os\n", "import os\nfrom backend.placement_session import create_session, get_session, save_session\nimport json\n")

new_routes = """
# PLACEMENT SESSION PHASE 2
@app.route('/api/placement-session/create', methods=['POST'])
def api_placement_session_create():
    try:
        company = request.form.get('company', '')
        role = request.form.get('role', '')
        time_budget = int(request.form.get('timeBudget', 120))
        strengths = request.form.get('strengths', '')
        
        resume_file = request.files.get('resume')
        study_material_file = request.files.get('studyMaterial')
        
        resume_text = ""
        study_text = ""
        
        if resume_file:
            filename = secure_filename(resume_file.filename)
            import tempfile, uuid
            temp_path = os.path.join(tempfile.gettempdir(), f'{uuid.uuid4()}_{filename}')
            resume_file.save(temp_path)
            try:
                resume_text = extract_text(temp_path)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        if study_material_file:
            filename = secure_filename(study_material_file.filename)
            temp_path = os.path.join(tempfile.gettempdir(), f'{uuid.uuid4()}_{filename}')
            study_material_file.save(temp_path)
            try:
                study_text = extract_text(temp_path)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        # Call ask_groq to extract role requirements
        system_prompt = '''You are a highly analytical technical recruiter intelligence AI.
Extract the role requirements (skills, languages, frameworks, CS fundamentals, behavioral expectations) 
and any publicly-known interview pattern information for this company and role.

CRITICAL REQUIREMENT (PER SECTION 5 OF SPEC):
You must tag EVERY extracted skill/requirement with a confidence level (HIGH, MEDIUM, or LOW) and 
provide the evidence that supports it (e.g. "Mentioned in study material", "Standard for L4 at Google", 
"Commonly asked based on public interview patterns").
DO NOT present speculation as fact. 

Return your response AS A VALID JSON OBJECT exactly matching this schema:
{
  "extracted_requirements": [
    {"skill": "Python", "confidence": "HIGH", "evidence": "..."}
  ],
  "interview_patterns": [
    "string pattern 1", "string pattern 2"
  ]
}
'''
        user_prompt = f"Company: {company}\\nRole: {role}\\n"
        if study_text:
            user_prompt += f"Study Material/JD:\\n{study_text[:3000]}\\n"
            
        ai_response = ask_groq(system_prompt, user_prompt)
        
        # Parse JSON from ai_response
        intel = {"extracted_requirements": [], "interview_patterns": []}
        if ai_response:
            try:
                # Find JSON block if wrapped in markdown
                if "```json" in ai_response:
                    json_str = ai_response.split("```json")[1].split("```")[0].strip()
                else:
                    json_str = ai_response.strip()
                parsed = json.loads(json_str)
                
                # Filter out claims without confidence tags
                reqs = parsed.get("extracted_requirements", [])
                valid_reqs = []
                for r in reqs:
                    if r.get("confidence") in ["HIGH", "MEDIUM", "LOW"]:
                        valid_reqs.append(r)
                
                intel["extracted_requirements"] = valid_reqs
                intel["interview_patterns"] = parsed.get("interview_patterns", [])
                
            except Exception as e:
                app.logger.error(f"Failed to parse LLM JSON: {e}")
                # Fallback empty structure
                pass
                
        # Create session
        candidate_id = str(session.get('user_id', 1))
        session_data = create_session(candidate_id, company, role, time_budget)
        
        # Hydrate session with intel and candidate data
        session_data["company_role_intelligence"] = intel
        session_data["candidate"]["resume_data"] = {"raw_text": resume_text[:1000]} # Truncate for size
        session_data["candidate"]["strengths_notes"] = strengths
        
        save_session(session_data["session_id"], session_data)
        
        return jsonify({"success": True, "session_id": session_data["session_id"]})
        
    except Exception as e:
        app.logger.error(f"Error in create placement session: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/placement-session/<session_id>', methods=['GET'])
def api_placement_session_get(session_id):
    session_data = get_session(session_id)
    if not session_data:
        return jsonify({"success": False, "error": "Session not found"}), 404
    return jsonify({"success": True, "session": session_data})
"""

if "@app.route('/api/placement-session/create'" not in code:
    code = code.replace("if __name__ == '__main__':", new_routes + "\nif __name__ == '__main__':")
    
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Added placement session routes to app.py")
