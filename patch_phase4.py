import json
import os

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update /api/resume/scan to persist skills and score
old_resume = """        result = scan_resume_text(text, {'skills': ['python','django','fastapi','sql','react','javascript'], 'min_exp': 2})
        ai_feedback = None
        if text:
            ai_feedback = ask_groq(
                'You are a senior technical recruiter. Review the resume and provide actionable feedback in 3 bullet points.',
                f'Resume:\\n{text[:2000]}\\n\\nGive 3 specific improvement tips.')
            if ai_feedback is None:
                return jsonify({'success': False, 'error': 'AI service is temporarily unavailable.'}), 503
        return jsonify({'success': True, **result, 'ai_feedback': ai_feedback})"""

new_resume = """        result = scan_resume_text(text, {'skills': ['python','django','fastapi','sql','react','javascript'], 'min_exp': 2})
        ai_feedback = None
        if text:
            ai_feedback = ask_groq(
                'You are a senior technical recruiter. Review the resume and provide actionable feedback in 3 bullet points.',
                f'Resume:\\n{text[:2000]}\\n\\nGive 3 specific improvement tips.')
            if ai_feedback is None:
                return jsonify({'success': False, 'error': 'AI service is temporarily unavailable.'}), 503
        
        # Persist to user.json for the explanation engine
        user = load_json(USER_DATA_FILE, {})
        user['candidate_skills'] = result.get('skills_found', [])
        user['resume_score'] = result.get('match_score', 0)
        save_json(USER_DATA_FILE, user)

        return jsonify({'success': True, **result, 'ai_feedback': ai_feedback})"""

code = code.replace(old_resume, new_resume)

# 2. Add the explanation endpoint
explanation_code = """
@app.route('/api/candidates/<int:candidate_id>/explanation', methods=['GET'])
def get_candidate_explanation(candidate_id):
    user = load_json(USER_DATA_FILE, {})
    
    # Extract persisted scores
    resume_score = user.get('resume_score', 0)
    solved = user.get('solved_problems', [])
    coding_score = min(100, len(solved) * 20)  # simple scoring
    sql_score = None  # Implement later if we add SQL specific problems
    
    scores = {"resume": resume_score, "coding": coding_score, "sql": sql_score}
    candidate_skills = user.get('candidate_skills', [])
    
    # Load required skills from job_roles.json
    job_roles = load_json(os.path.join(DATA_DIR, 'job_roles.json'), {})
    targeted_role = user.get('targeted_role', 'backend_engineer')
    role_data = job_roles.get(targeted_role, {})
    required_skills = role_data.get('required_skills', ['python', 'sql'])
    
    # Default behavior metrics
    fraud_score = 0
    timing_anomalies = 0
    
    # Calculate confidence
    candidate_data = {
        "scores": scores,
        "fraud_score": fraud_score,
        "timing_anomalies": timing_anomalies
    }
    confidence_result = calculate_confidence_score(candidate_data)
    confidence_score = confidence_result.get("overall_confidence", 0.0)
    
    # Determine basic decision
    final_score = (resume_score + coding_score) / 2
    if final_score >= 80:
        decision = "shortlist"
    elif final_score >= 60:
        decision = "interview"
    else:
        decision = "reject"
        
    explanation = generate_explanation(
        candidate_id=candidate_id,
        decision=decision,
        final_score=final_score,
        scores=scores,
        confidence_score=confidence_score,
        fraud_score=fraud_score,
        candidate_skills=candidate_skills,
        required_skills=required_skills,
        timing_anomalies=timing_anomalies,
        consistency_score=confidence_result.get("consistency_confidence", 100.0)
    )
    
    return jsonify({'success': True, 'explanation': explanation})

"""

# Insert the endpoint before "if __name__ == '__main__':"
if "if __name__ == '__main__':" in code:
    code = code.replace("if __name__ == '__main__':", explanation_code + "if __name__ == '__main__':")
else:
    print("Could not find __main__ block")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("backend patched for Phase 4")
