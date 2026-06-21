from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import tempfile
import uuid
import random
import json
import re
from werkzeug.utils import secure_filename
from backend.resume_processor import extract_text, scan_resume_text
from backend.engine import select_hr_questions, select_coding_questions, score_coding_answers, execute_code
from backend.scoring_logic import generate_explanation, calculate_confidence_score, determine_next_stage

# --- Groq AI import (graceful fallback) ---
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

app = Flask(__name__)
CORS(app)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR  = os.path.join(BASE_DIR, 'frontend')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ASSESSMENT_DIR = os.path.join(BASE_DIR, 'data', 'assessment')
LEARNING_DIR   = os.path.join(BASE_DIR, 'data', 'learning')
INTERVIEWS_DIR = os.path.join(BASE_DIR, 'data', 'interviews')
USER_DATA_FILE = os.path.join(BASE_DIR, 'data', 'user.json')

for d in [UPLOAD_FOLDER, ASSESSMENT_DIR, LEARNING_DIR, INTERVIEWS_DIR]:
    os.makedirs(d, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Groq Client
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
groq_client = None
if GROQ_AVAILABLE and GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)

# JSON Helpers
def load_json(path, default=None):
    if not os.path.exists(path):
        return default if default is not None else {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Groq AI Helper
def ask_groq(system_prompt, user_message, model='llama3-8b-8192'):
    if groq_client:
        try:
            completion = groq_client.chat.completions.create(
                model=model,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user',   'content': user_message}
                ],
                max_tokens=512,
                temperature=0.7,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            app.logger.error(f'Groq error: {e}')

    msg_lower = user_message.lower()
    if any(k in msg_lower for k in ['hint', 'help me', 'stuck', 'how']):
        return 'Great question! Try breaking the problem down: what data structure gives O(1) lookups? A hash map stores key-value pairs and can solve many problems in one pass.'
    if any(k in msg_lower for k in ['time complexity', 'big o', 'complexity']):
        return 'Time complexity measures how runtime grows with input size. O(n) = linear, O(n^2) = quadratic, O(log n) = logarithmic. Aim for O(n log n) or better.'
    if any(k in msg_lower for k in ['dynamic programming', 'dp']):
        return 'DP shines when: 1) Problem has overlapping subproblems, 2) Optimal substructure exists. Start with recursion + memoization, then bottom-up tabulation.'
    if any(k in msg_lower for k in ['graph', 'bfs', 'dfs']):
        return 'BFS uses a queue and explores level by level - great for shortest paths. DFS uses a stack and dives deep - great for cycle detection and topological sort.'
    if any(k in msg_lower for k in ['hello', 'hi', 'hey']):
        return 'Hi there! I am your Placify AI Coach. Ask me anything about algorithms, data structures, or interview prep!'
    return 'That is an interesting challenge! Think about: 1) What is the brute force? 2) What is the bottleneck? 3) What data structure can optimize it? You have got this!'

def bootstrap_data():
    hr_file     = os.path.join(ASSESSMENT_DIR, 'hr_questions.json')
    if not os.path.exists(hr_file):
        save_json(hr_file, [
            {'id': 1, 'question': 'Tell me about a time you worked in a team.', 'type': 'hr'},
            {'id': 2, 'question': 'What are your greatest strengths?', 'type': 'hr'},
            {'id': 3, 'question': 'Why do you want this job?', 'type': 'hr'},
            {'id': 4, 'question': 'Describe a challenging situation and how you handled it.', 'type': 'hr'},
            {'id': 5, 'question': 'Where do you see yourself in 5 years?', 'type': 'hr'},
        ])
    if not os.path.exists(USER_DATA_FILE):
        save_json(USER_DATA_FILE, {
            'profile': {'name': 'Placify User', 'email': 'user@placify.dev', 'title': 'Software Engineer'},
            'preferences': {'email_notifications': True, 'public_profile': True, 'dark_mode': True},
            'solved_problems': [],
            'chat_history': []
        })

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)

# DASHBOARD
@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    user = load_json(USER_DATA_FILE, {})
    solved = user.get('solved_problems', [])
    return jsonify({'success': True, 'stats': {'problems_solved': len(solved) if solved else 342, 'solved_trend': 12, 'streak': 14, 'global_rank': 12403, 'mock_interviews': 8}})

@app.route('/api/dashboard/chart')
def get_dashboard_chart():
    return jsonify({'success': True, 'labels': ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], 'data': [4,7,5,10,8,14,12]})

@app.route('/api/dashboard/progress')
def get_dashboard_progress():
    return jsonify({'success': True, 'progress': [
        {'title': 'Data Structures', 'completed': 120, 'total': 150, 'color': 'primary', 'color_hex': 'var(--primary-accent)'},
        {'title': 'Algorithms',      'completed': 85,  'total': 100, 'color': 'success', 'color_hex': 'var(--success-color)'},
        {'title': 'System Design',   'completed': 15,  'total': 50,  'color': 'warning', 'color_hex': 'var(--warning-color)'}
    ], 'top_skills': ['React','TypeScript','Node.js','PostgreSQL','AWS','System Design']})

@app.route('/api/dashboard/activity')
def get_dashboard_activity():
    return jsonify({'success': True, 'activities': [
        {'title': 'Solved "Two Sum"', 'time': 'Today, 2:30 PM', 'icon': 'check-circle-2', 'color': 'success'},
        {'title': 'Completed React Fundamentals', 'time': 'Yesterday', 'icon': 'book-open', 'color': 'primary'},
        {'title': 'Earned "Fast Learner" Badge', 'time': '3 days ago', 'icon': 'award', 'color': 'warning'}
    ]})

# AI CHAT
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json or {}
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'success': False, 'error': 'Empty message'}), 400
    system_prompt = ('You are Placify AI Coach, an expert computer science tutor specialising in DSA and interview prep. '
                     'Be concise, encouraging, and practical. Keep responses under 150 words.')
    user = load_json(USER_DATA_FILE, {})
    chat_hist = user.get('chat_history', [])
    chat_hist.append({'role': 'user', 'content': message})
    response_text = ask_groq(system_prompt, message)
    chat_hist.append({'role': 'assistant', 'content': response_text})
    user['chat_history'] = chat_hist[-50:]
    save_json(USER_DATA_FILE, user)
    return jsonify({'success': True, 'response': response_text})

# PROBLEMS
def load_problems():
    return load_json(os.path.join(ASSESSMENT_DIR, 'questions.json'), [])

def save_problems(problems):
    save_json(os.path.join(ASSESSMENT_DIR, 'questions.json'), problems)

@app.route('/api/problems')
def get_all_problems():
    try:
        problems = load_problems()
        difficulty = request.args.get('difficulty', 'all')
        search = request.args.get('search', '').lower()
        result = []
        for p in problems:
            if difficulty != 'all' and p.get('difficulty') != difficulty:
                continue
            if search and search not in p.get('title','').lower() and search not in ' '.join(p.get('tags',[])).lower():
                continue
            result.append({'id': p['id'], 'title': p['title'], 'difficulty': p['difficulty'],
                           'topic': p.get('topic',''), 'tags': p.get('tags',[]),
                           'acceptance': p.get('acceptance','50%'), 'solved': p.get('solved', False)})
        all_p = load_problems()
        stats = {}
        for diff in ['easy', 'medium', 'hard']:
            stats[diff] = {'solved': sum(1 for p in all_p if p.get('difficulty')==diff and p.get('solved')),
                           'total':  sum(1 for p in all_p if p.get('difficulty')==diff)}
        return jsonify({'success': True, 'problems': result, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/problems/<int:problem_id>')
def get_problem_by_id(problem_id):
    try:
        problem = next((p for p in load_problems() if p['id'] == problem_id), None)
        if not problem:
            return jsonify({'success': False, 'error': 'Not found'}), 404
        return jsonify({'success': True, 'problem': problem})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/problems/submit', methods=['POST'])
def submit_problem():
    try:
        data = request.json or {}
        problem_id = data.get('problem_id')
        code = data.get('code', '')
        problems = load_problems()
        problem = next((p for p in problems if p['id'] == problem_id), None)
        if not problem:
            return jsonify({'success': False, 'error': 'Not found'}), 404
        test_cases = problem.get('test_cases', [])
        test_results = []
        all_passed = True
        for i, tc in enumerate(test_cases):
            passed, output, error = execute_code(code, tc)
            test_results.append({'test_case': i+1, 'input': tc['input'], 'expected': tc['output'],
                                 'actual': output, 'passed': passed, 'error': error})
            if not passed:
                all_passed = False
        if all_passed:
            for p in problems:
                if p['id'] == problem_id:
                    p['solved'] = True
            save_problems(problems)
            user = load_json(USER_DATA_FILE, {})
            solved = user.get('solved_problems', [])
            if problem_id not in solved:
                solved.append(problem_id)
            user['solved_problems'] = solved
            save_json(USER_DATA_FILE, user)
        return jsonify({'success': True, 'all_passed': all_passed, 'test_results': test_results,
                        'problem_title': problem.get('title')})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/problems/<int:problem_id>/hint', methods=['POST'])
def get_problem_hint(problem_id):
    try:
        problem = next((p for p in load_problems() if p['id'] == problem_id), None)
        if not problem:
            return jsonify({'success': False, 'error': 'Not found'}), 404
        system_prompt = ('You are a coding coach. Give a helpful hint for the problem without revealing the solution. '
                         'Point to the key data structure or technique in 2-3 sentences.')
        user_msg = f"Problem: {problem['title']}\nDescription: {problem['description']}\nPre-stored hint: {problem.get('solution_hint','')}\n\nGive a hint."
        hint = ask_groq(system_prompt, user_msg)
        return jsonify({'success': True, 'hint': hint})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ASSESSMENT
@app.route('/api/questions/hr')
def get_hr_questions():
    count = request.args.get('count', 4, type=int)
    return jsonify({'success': True, 'questions': select_hr_questions(count)})

@app.route('/api/questions/coding')
def get_coding_questions():
    return jsonify({'success': True, 'questions': select_coding_questions(
        request.args.get('job_role_id', 1, type=int),
        request.args.get('score', None, type=int),
        request.args.get('count', 3, type=int))})

@app.route('/api/assess/coding', methods=['POST'])
def assess_coding():
    try:
        data = request.json or {}
        score, results = score_coding_answers(data.get('questions', []), data.get('answers', []))
        return jsonify({'success': True, 'score': score, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# LEARNING PATHS
@app.route('/api/learning/roadmaps')
def get_roadmaps():
    try:
        data = load_json(os.path.join(LEARNING_DIR, 'roadmaps.json'), {'roadmaps': []})
        summary = []
        for rm in data.get('roadmaps', []):
            all_nodes = [n for s in rm.get('sections', []) for n in s.get('nodes', [])]
            done = sum(1 for n in all_nodes if n.get('status') == 'done')
            total = len(all_nodes)
            summary.append({'id': rm['id'], 'title': rm['title'], 'description': rm['description'],
                            'icon': rm.get('icon','book'), 'color': rm.get('color','#FFA116'),
                            'total_nodes': total, 'done_nodes': done,
                            'percent': round((done/total*100) if total else 0)})
        return jsonify({'success': True, 'roadmaps': summary})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/learning/roadmaps/<roadmap_id>')
def get_roadmap_detail(roadmap_id):
    try:
        data = load_json(os.path.join(LEARNING_DIR, 'roadmaps.json'), {'roadmaps': []})
        rm = next((r for r in data.get('roadmaps', []) if r['id'] == roadmap_id), None)
        if not rm:
            return jsonify({'success': False, 'error': 'Not found'}), 404
        all_nodes = [n for s in rm.get('sections', []) for n in s.get('nodes', [])]
        done = sum(1 for n in all_nodes if n.get('status') == 'done')
        in_progress = sum(1 for n in all_nodes if n.get('status') == 'in-progress')
        todo = sum(1 for n in all_nodes if n.get('status') == 'todo')
        return jsonify({'success': True, 'roadmap': rm,
                        'stats': {'done': done, 'in_progress': in_progress, 'todo': todo, 'total': len(all_nodes)}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/learning/roadmaps/<roadmap_id>/nodes/<node_id>/progress', methods=['POST'])
def update_node_progress(roadmap_id, node_id):
    try:
        status = (request.json or {}).get('status', 'done')
        path = os.path.join(LEARNING_DIR, 'roadmaps.json')
        rm_data = load_json(path, {'roadmaps': []})
        updated = False
        for rm in rm_data.get('roadmaps', []):
            if rm['id'] == roadmap_id:
                for section in rm.get('sections', []):
                    for node in section.get('nodes', []):
                        if node['id'] == node_id:
                            node['status'] = status
                            updated = True
        if not updated:
            return jsonify({'success': False, 'error': 'Node not found'}), 404
        save_json(path, rm_data)
        return jsonify({'success': True, 'message': f'Node marked as {status}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/learning/paths')
def get_learning_paths():
    try:
        data = load_json(os.path.join(LEARNING_DIR, 'roadmaps.json'), {'roadmaps': []})
        color_map = {'#FFA116': 'primary', '#00B8A3': 'success', '#FF6B6B': 'error', '#FFC857': 'warning'}
        paths = []
        for rm in data.get('roadmaps', []):
            all_nodes = [n for s in rm.get('sections', []) for n in s.get('nodes', [])]
            done = sum(1 for n in all_nodes if n.get('status') == 'done')
            total = len(all_nodes)
            color = rm.get('color', '#FFA116')
            paths.append({'id': rm['id'], 'title': rm['title'], 'description': rm['description'],
                          'icon': rm.get('icon','book'), 'color': color_map.get(color,'primary'),
                          'bg_color': color+'22', 'level': 'Intermediate', 'completed': done,
                          'total': total, 'tag_class': 'tag-medium'})
        return jsonify({'success': True, 'paths': paths})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# INTERVIEWS
@app.route('/api/interviews')
def get_interviews():
    path = os.path.join(INTERVIEWS_DIR, 'sessions.json')
    data = load_json(path, {'upcoming': [], 'past': []})
    if not data.get('upcoming') and not data.get('past'):
        data = {'upcoming': [
            {'id': 1, 'topic': 'System Design', 'time_until': 'In 2 Days', 'date': 'June 21, 2:00 PM EST', 'interviewer': 'Senior SWE @ Google'}
        ], 'past': [
            {'id': 2, 'topic': 'Data Structures & Algo', 'date': 'June 14, 2026', 'rating': '4.5/5', 'feedback': None},
            {'id': 3, 'topic': 'Frontend Architecture',  'date': 'May 28, 2026',  'rating': '3.8/5', 'feedback': None},
            {'id': 4, 'topic': 'Behavioral',             'date': 'May 10, 2026',  'rating': '5.0/5', 'feedback': None}
        ]}
        save_json(path, data)
    return jsonify({'success': True, **data})

@app.route('/api/interviews/schedule', methods=['POST'])
def schedule_interview():
    data = request.json or {}
    path = os.path.join(INTERVIEWS_DIR, 'sessions.json')
    iv_data = load_json(path, {'upcoming': [], 'past': []})
    new_id = max([i.get('id',0) for i in iv_data.get('upcoming',[]) + iv_data.get('past',[])], default=0) + 1
    iv_data['upcoming'].append({'id': new_id, 'topic': data.get('topic','General'),
                                'date': data.get('date','TBD'), 'time_until': 'Scheduled', 'interviewer': 'TBD'})
    save_json(path, iv_data)
    return jsonify({'success': True, 'message': 'Interview scheduled!'})

@app.route('/api/interviews/<int:session_id>/feedback', methods=['POST', 'GET'])
def interview_feedback(session_id):
    path = os.path.join(INTERVIEWS_DIR, 'sessions.json')
    iv_data = load_json(path, {'upcoming': [], 'past': []})
    if request.method == 'GET':
        session = next((s for s in iv_data.get('past',[]) if s.get('id')==session_id), None)
        if not session:
            return jsonify({'success': False, 'error': 'Not found'}), 404
        return jsonify({'success': True, 'feedback': session.get('feedback'), 'score': session.get('score')})
    # POST - generate AI feedback
    data = request.json or {}
    answers = data.get('answers', [])
    topic = data.get('topic', 'General')
    if not answers:
        return jsonify({'success': False, 'error': 'No answers'}), 400
    qa_text = '\n'.join([f"Q: {a['question']}\nA: {a['answer']}" for a in answers])
    system_prompt = ('You are an expert technical interviewer. Evaluate the answers and provide structured feedback.\n'
                     'Format: SCORE: X/10\nSTRENGTHS:\n- ...\nAREAS TO IMPROVE:\n- ...\nSUMMARY: ...')
    feedback_text = ask_groq(system_prompt, f'Topic: {topic}\n\n{qa_text}', model='llama3-8b-8192')
    score_match = re.search(r'SCORE:\s*(\d+)/10', feedback_text)
    score = int(score_match.group(1)) if score_match else 7
    for session in iv_data.get('past', []):
        if session.get('id') == session_id:
            session['feedback'] = feedback_text
            session['score'] = score
            break
    save_json(path, iv_data)
    return jsonify({'success': True, 'feedback': feedback_text, 'score': score})

# RESUME
@app.route('/api/resume/scan', methods=['POST'])
def scan_resume():
    try:
        file = request.files.get('resume')
        text = request.form.get('text', '')
        if file:
            filename = secure_filename(file.filename)
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
                f'Resume:\n{text[:2000]}\n\nGive 3 specific improvement tips.')
        return jsonify({'success': True, **result, 'ai_feedback': ai_feedback})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# USER/AUTH
@app.route('/api/user/profile', methods=['GET', 'POST'])
def user_profile():
    if request.method == 'POST':
        data = request.json or {}
        user = load_json(USER_DATA_FILE, {})
        if 'profile' not in user:
            user['profile'] = {}
        user['profile'].update({k: v for k, v in data.items() if k in ['name','email','title']})
        if 'preferences' in data:
            user.setdefault('preferences', {}).update(data['preferences'])
        save_json(USER_DATA_FILE, user)
        return jsonify({'success': True, 'message': 'Profile updated'})
    user = load_json(USER_DATA_FILE, {})
    return jsonify({'success': True,
                    'profile': user.get('profile', {'name':'Placify User','email':'user@placify.dev','title':'Software Engineer'}),
                    'preferences': user.get('preferences', {'email_notifications':True,'public_profile':True,'dark_mode':True})})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json or {}
    if data.get('email') and data.get('password'):
        return jsonify({'success': True, 'token': f'mock-jwt-{uuid.uuid4().hex[:16]}'})
    return jsonify({'success': False, 'error': 'Email and password required'}), 400

if __name__ == '__main__':
    bootstrap_data()
    app.run(debug=True, port=5000)
