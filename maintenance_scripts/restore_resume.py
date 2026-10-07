import re

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

import_stmt = "from backend.resume_processor import extract_text, scan_resume_text, cross_check_skills\n"
if "from backend.resume_processor" not in code:
    code = code.replace("import os\n", "import os\n" + import_stmt)

resume_code = """
# RESUME
@app.route('/api/resume/scan', methods=['POST'])
def scan_resume():
    try:
        file = request.files.get('resume')
        text = request.form.get('text', '')
        if file:
            filename = secure_filename(file.filename)
            import tempfile, uuid
            temp_path = os.path.join(tempfile.gettempdir(), f'{uuid.uuid4()}_{filename}')
            file.save(temp_path)
            try:
                text = extract_text(temp_path)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        result = scan_resume_text(text, {'skills': ['python','django','fastapi','sql','react','javascript'], 'min_exp': 2})
        ai_feedback = None
        if text:
            ai_feedback = ask_groq(
                'You are a senior technical recruiter. Review the resume and provide actionable feedback in 3 bullet points.',
                f'Resume:\\n{text[:2000]}\\n\\nGive 3 specific improvement tips.')
            if ai_feedback is None:
                return jsonify({'success': False, 'error': 'AI service is temporarily unavailable.'}), 503
        
        user = get_candidate_data(session.get('user_id', 1))
        user['candidate_skills'] = result.get('skills_found', [])
        user['resume_score'] = result.get('match_score', 0)
        save_candidate_data(user)
        
        response_text = f"<h3>Resume Scan Complete</h3><p>Match Score: {result.get('match_score')}%</p>"
        if result.get('skills_found'):
            response_text += f"<p>Skills found: {', '.join(result.get('skills_found'))}</p>"
        if ai_feedback:
            response_text += f"<h4>AI Recruiter Feedback:</h4><div>{ai_feedback.replace('*', '')}</div>"
        
        return jsonify({'success': True, 'result': response_text})
    except Exception as e:
        app.logger.error(f"Error scanning resume: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
"""

if "@app.route('/api/resume/scan'" not in code:
    # Insert it before the __main__ block
    code = code.replace("if __name__ == '__main__':", resume_code + "\n\nif __name__ == '__main__':")
    
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Restored resume scanner endpoint to app.py")
