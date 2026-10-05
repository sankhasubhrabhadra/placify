import os
import json

file_path = os.path.join('backend', 'resume_processor.py')
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update SKILL_TAXONOMY
old_tax_end = '    "etl": ["etl", "data pipeline", "data pipelines"],\n}'
new_tax_end = """    "etl": ["etl", "data pipeline", "data pipelines"],
    "data structures": ["data structures", "array", "tree", "hash table", "linked list", "graph", "matrix"],
    "algorithms": ["algorithms", "dynamic programming", "greedy", "sorting", "searching", "depth-first search", "breadth-first search", "union find", "two pointers"],
}"""
if old_tax_end in code:
    code = code.replace(old_tax_end, new_tax_end)

# 2. Add cross_check_skills function
cross_check_code = """

def cross_check_skills(candidate_skills: List[str], solved_problems: List[Dict]) -> Dict[str, List[str]]:
    \"\"\"Cross-checks resume skills against platform performance.\"\"\"
    demonstrated_skills = set()
    
    if solved_problems:
        # All executed code is Python currently
        demonstrated_skills.add("python")
        
    for prob in solved_problems:
        tags = prob.get("tags", [])
        for tag in tags:
            tag_lower = tag.lower()
            # Map tags to taxonomy
            for skill_key, aliases in SKILL_TAXONOMY.items():
                if tag_lower in aliases:
                    demonstrated_skills.add(skill_key)
                    
    candidate_set = set(s.lower() for s in candidate_skills)
    
    verified = list(candidate_set & demonstrated_skills)
    unverified = list(candidate_set - demonstrated_skills)
    opportunities = list(demonstrated_skills - candidate_set)
    
    return {
        "verified_skills": sorted(verified),
        "unverified_skills": sorted(unverified),
        "opportunities": sorted(opportunities)
    }

"""
code += cross_check_code

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

# 3. Patch app.py explanation endpoint
app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    app_code = f.read()

# Add import for cross_check_skills
app_code = app_code.replace("from backend.resume_processor import scan_resume_text", "from backend.resume_processor import scan_resume_text, cross_check_skills")

# Modify get_candidate_explanation to use cross_check_skills
old_expl_start = """    # Calculate confidence
    candidate_data = {"""

new_expl_start = """    # Cross-check skills
    all_questions = load_json(CODING_QUESTIONS_PATH, [])
    solved_objs = [q for q in all_questions if q.get('id') in solved]
    cross_check = cross_check_skills(candidate_skills, solved_objs)
    
    # Calculate confidence
    candidate_data = {"""

app_code = app_code.replace(old_expl_start, new_expl_start)

old_expl_call = """        consistency_score=confidence_result.get("consistency_confidence", 100.0)
    )
    
    return jsonify({'success': True, 'explanation': explanation})"""

new_expl_call = """        consistency_score=confidence_result.get("consistency_confidence", 100.0)
    )
    
    explanation['verified_skills'] = cross_check['verified_skills']
    explanation['unverified_skills'] = cross_check['unverified_skills']
    explanation['opportunities'] = cross_check['opportunities']
    
    return jsonify({'success': True, 'explanation': explanation})"""

app_code = app_code.replace(old_expl_call, new_expl_call)

# Apply to simulation as well
old_sim = """        return generate_explanation(
            candidate_id=candidate_id, decision=dec, final_score=f_score, scores=scores,
            confidence_score=conf_score, fraud_score=fraud_score, candidate_skills=c_skills,
            required_skills=required_skills, timing_anomalies=timing_anomalies,
            consistency_score=conf_res.get("consistency_confidence", 100.0)
        )"""

new_sim = """        expl = generate_explanation(
            candidate_id=candidate_id, decision=dec, final_score=f_score, scores=scores,
            confidence_score=conf_score, fraud_score=fraud_score, candidate_skills=c_skills,
            required_skills=required_skills, timing_anomalies=timing_anomalies,
            consistency_score=conf_res.get("consistency_confidence", 100.0)
        )
        cross_c = cross_check_skills(c_skills, solved_objs)
        expl['verified_skills'] = cross_c['verified_skills']
        expl['unverified_skills'] = cross_c['unverified_skills']
        expl['opportunities'] = cross_c['opportunities']
        return expl"""

# But wait, solved_objs is not defined in simulate_skill_impact!
# I need to define it at the top of simulate_skill_impact
old_sim_start = """    targeted_role = user.get('targeted_role', 'backend_engineer')
    required_skills = job_roles.get(targeted_role, {}).get('required_skills', ['python', 'sql'])"""

new_sim_start = """    targeted_role = user.get('targeted_role', 'backend_engineer')
    required_skills = job_roles.get(targeted_role, {}).get('required_skills', ['python', 'sql'])
    
    all_questions = load_json(CODING_QUESTIONS_PATH, [])
    solved_objs = [q for q in all_questions if q.get('id') in solved]"""

app_code = app_code.replace(old_sim_start, new_sim_start)
app_code = app_code.replace(old_sim, new_sim)


with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_code)

print("Phase 6 backend patched")
