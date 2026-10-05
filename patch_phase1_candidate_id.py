import os

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

helpers_code = """
def get_candidate_data(candidate_id=1):
    data = load_json(USER_DATA_FILE, {})
    if 'candidates' not in data:
        return data
    return data.get('candidates', {}).get(str(candidate_id), {})

def save_candidate_data(candidate_id, candidate_data):
    data = load_json(USER_DATA_FILE, {})
    if 'candidates' not in data:
        data = {'candidates': {'1': data}}
    
    data['candidates'][str(candidate_id)] = candidate_data
    save_json(USER_DATA_FILE, data)
"""

if "def get_candidate_data" not in code:
    code = code.replace("def bootstrap_data():", helpers_code + "\ndef bootstrap_data():")

old_bootstrap = """    if not os.path.exists(USER_DATA_FILE):
        save_json(USER_DATA_FILE, {
            'profile': {'name': 'Placify User', 'email': 'user@placify.dev', 'title': 'Software Engineer'},
            'preferences': {'email_notifications': True, 'public_profile': True, 'dark_mode': True},
            'solved_problems': [],
            'chat_history': []
        })"""

new_bootstrap = """    if not os.path.exists(USER_DATA_FILE):
        save_json(USER_DATA_FILE, {
            'candidates': {
                '1': {
                    'profile': {'name': 'Placify User', 'email': 'user@placify.dev', 'title': 'Software Engineer'},
                    'preferences': {'email_notifications': True, 'public_profile': True, 'dark_mode': True},
                    'solved_problems': [],
                    'chat_history': []
                }
            }
        })
    else:
        data = load_json(USER_DATA_FILE, {})
        if 'candidates' not in data:
            save_json(USER_DATA_FILE, {'candidates': {'1': data}})"""

code = code.replace(old_bootstrap, new_bootstrap)

# Replace other load_json(USER_DATA_FILE, {})
# Note: we should replace it with get_candidate_data(session.get('user_id', 1)) or simply 1 where session isn't available.
# Actually, I'll write a simple regex or just string replacement for the exact lines.

import re

def replacer(match):
    return "user = get_candidate_data(session.get('user_id', 1))"

code = re.sub(r"user\s*=\s*load_json\(USER_DATA_FILE,\s*\{\}\)", replacer, code)

# Fix save_json(USER_DATA_FILE, user)
def save_replacer(match):
    return "save_candidate_data(session.get('user_id', 1), user)"

code = re.sub(r"save_json\(USER_DATA_FILE,\s*user\)", save_replacer, code)

# Fix get_candidate_explanation
old_expl = """def get_candidate_explanation(candidate_id):
    user = get_candidate_data(session.get('user_id', 1))"""

new_expl = """def get_candidate_explanation(candidate_id):
    user = get_candidate_data(candidate_id)"""
code = code.replace(old_expl, new_expl)

# Fix simulate_skill_impact
old_sim = """def simulate_skill_impact(candidate_id):
    data = request.json or {}
    hypothetical_skills = data.get('skills', [])
    
    user = get_candidate_data(session.get('user_id', 1))"""

new_sim = """def simulate_skill_impact(candidate_id):
    data = request.json or {}
    hypothetical_skills = data.get('skills', [])
    
    user = get_candidate_data(candidate_id)"""
code = code.replace(old_sim, new_sim)

# Update scan_resume to return candidate_id
old_scan = """        user['candidate_skills'] = result.get('skills_found', [])
        user['resume_score'] = result.get('match_score', 0)
        save_candidate_data(session.get('user_id', 1), user)

        return jsonify({'success': True, **result, 'ai_feedback': ai_feedback})"""

new_scan = """        user['candidate_skills'] = result.get('skills_found', [])
        user['resume_score'] = result.get('match_score', 0)
        c_id = session.get('user_id', 1)
        save_candidate_data(c_id, user)

        return jsonify({'success': True, **result, 'ai_feedback': ai_feedback, 'candidate_id': c_id})"""
code = code.replace(old_scan, new_scan)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)
print("app.py patched!")
