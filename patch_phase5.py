import os

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

simulate_code = """
@app.route('/api/candidates/<int:candidate_id>/simulate', methods=['POST'])
def simulate_skill_impact(candidate_id):
    data = request.json or {}
    hypothetical_skills = data.get('skills', [])
    
    user = load_json(USER_DATA_FILE, {})
    
    # Original data
    resume_score = user.get('resume_score', 0)
    solved = user.get('solved_problems', [])
    coding_score = min(100, len(solved) * 20)
    sql_score = None
    original_scores = {"resume": resume_score, "coding": coding_score, "sql": sql_score}
    candidate_skills = user.get('candidate_skills', [])
    
    job_roles = load_json(os.path.join(BASE_DIR, 'data', 'job_roles.json'), {})
    targeted_role = user.get('targeted_role', 'backend_engineer')
    required_skills = job_roles.get(targeted_role, {}).get('required_skills', ['python', 'sql'])
    
    fraud_score = 0
    timing_anomalies = 0
    
    # Helper to generate explanation given candidate skills
    def get_expl(c_skills):
        # Recalculate resume score
        matched = set(c_skills) & set(required_skills)
        r_score = int((len(matched) / len(required_skills)) * 100) if required_skills else 100
        scores = {"resume": r_score, "coding": coding_score, "sql": sql_score}
        
        c_data = {"scores": scores, "fraud_score": fraud_score, "timing_anomalies": timing_anomalies}
        conf_res = calculate_confidence_score(c_data)
        conf_score = conf_res.get("overall_confidence", 0.0)
        
        f_score = (r_score + coding_score) / 2
        dec = "shortlist" if f_score >= 80 else "interview" if f_score >= 60 else "reject"
            
        return generate_explanation(
            candidate_id=candidate_id, decision=dec, final_score=f_score, scores=scores,
            confidence_score=conf_score, fraud_score=fraud_score, candidate_skills=c_skills,
            required_skills=required_skills, timing_anomalies=timing_anomalies,
            consistency_score=conf_res.get("consistency_confidence", 100.0)
        )
        
    original_expl = get_expl(candidate_skills)
    
    new_skills = list(set(candidate_skills + hypothetical_skills))
    new_expl = get_expl(new_skills)
    
    # Calculate impact of each gap
    gaps = original_expl['skill_gaps']
    impacts = []
    for gap in gaps:
        expl = get_expl(candidate_skills + [gap])
        score_delta = expl['final_score'] - original_expl['final_score']
        impacts.append({"skill": gap, "score_impact": score_delta})
    
    impacts.sort(key=lambda x: x['score_impact'], reverse=True)
    
    return jsonify({
        'success': True,
        'original': original_expl,
        'simulated': new_expl,
        'recommendations': impacts
    })

"""

# Insert the endpoint before "if __name__ == '__main__':"
if "if __name__ == '__main__':" in code:
    code = code.replace("if __name__ == '__main__':", simulate_code + "if __name__ == '__main__':")
else:
    print("Could not find __main__ block")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("backend patched for Phase 5")
