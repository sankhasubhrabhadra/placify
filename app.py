from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from backend.db import get_db_connection, init_db
import os
from backend.baseline_assessment import get_next_baseline_question, process_baseline_answer, compute_skill_gaps
from backend.readiness import generate_readiness_report, simulate_what_if
from backend.activities import generate_learning_content, process_learning_quiz_answer, generate_coding_challenge, submit_coding_challenge
from backend.orchestrator import replan_roadmap
from backend.placement_session import create_session, get_session, save_session
import json
from backend.resume_processor import extract_text, scan_resume_text, cross_check_skills
import requests
from dotenv import load_dotenv
load_dotenv()  # loads .env file automatically
import tempfile
import uuid
import random
import json
import re
import datetime
from werkzeug.utils import secure_filename
from backend.engine import select_hr_questions, select_coding_questions, score_coding_answers, execute_code
from backend.scoring_logic import generate_explanation, calculate_confidence_score, determine_next_stage

# --- Groq AI import (graceful fallback) ---
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default-secret-key-for-dev') # Change in production
CORS(app, supports_credentials=True)

# Initialize database
init_db()

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
GROQ_MODEL = os.environ.get('GROQ_MODEL', 'llama-3.1-8b-instant')
GROQ_FALLBACK_MODEL = os.environ.get('GROQ_FALLBACK_MODEL', 'llama-3.1-70b-versatile')
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

def ask_groq(system_prompt, user_message, model=None):
    # Hijacked to use Local LLaMA via Ollama instead of Groq
    ollama_url = "http://localhost:11434/api/chat"
    model_name = os.environ.get('OLLAMA_MODEL', 'qwen2.5:1.5b') # Default to qwen2.5:1.5b
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "stream": False,
        "options": {
            "temperature": 0.7
        }
    }
    
    try:
        response = requests.post(ollama_url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()['message']['content'].strip()
    except Exception as e:
        app.logger.error(f"Ollama local error: {e}")
        return None


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
            save_json(USER_DATA_FILE, {'candidates': {'1': data}})

@app.route('/')
def index():
    return jsonify({"status": "ok", "message": "Placify API Backend is running."})

# --- AUTHENTICATION ROUTES ---

@app.route('/api/auth/signup', methods=['POST'])
def auth_signup():
    data = request.json or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    role = data.get('role', 'candidate')

    if not name or not email or not password:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if email exists
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'error': 'Email already in use'}), 400

    password_hash = generate_password_hash(password)
    
    try:
        cursor.execute(
            'INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)',
            (name, email, password_hash, role)
        )
        conn.commit()
        user_id = cursor.lastrowid
        session['user_id'] = user_id  # Log them in automatically
        return jsonify({'success': True, 'message': 'Account created successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    data = request.json or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'success': False, 'error': 'Missing email or password'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, password_hash, name, role FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = user['id']
        return jsonify({'success': True, 'message': 'Logged in successfully', 'user': {'name': user['name'], 'role': user['role']}})
    else:
        return jsonify({'success': False, 'error': 'Invalid email or password'}), 401

@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    session.pop('user_id', None)
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/auth/me', methods=['GET'])
def auth_me():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name, email, role FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({'success': True, 'user': {'name': user['name'], 'email': user['email'], 'role': user['role']}})
    return jsonify({'success': False, 'error': 'User not found'}), 404

# --- DASHBOARD ---
@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    user = get_candidate_data(session.get('user_id', 1))
    solved = user.get('solved_problems', [])
    timestamps = user.get('solved_timestamps', [])
    sessions = load_json(os.path.join(INTERVIEWS_DIR, 'sessions.json'), [])
    
    # Calculate Streak
    streak = 0
    if timestamps:
        import datetime
        try:
            dates = sorted(list(set([datetime.datetime.fromisoformat(ts).date() for ts in timestamps])), reverse=True)
            today = datetime.date.today()
            if dates and (dates[0] == today or dates[0] == today - datetime.timedelta(days=1)):
                streak = 1
                for i in range(1, len(dates)):
                    if dates[i] == dates[i-1] - datetime.timedelta(days=1):
                        streak += 1
                    else:
                        break
        except Exception:
            pass
            
    # Calculate Rank
    # Require 5 problems to get a rank. Base rank 100,000, drops by ~1500 per problem
    if len(solved) < 5:
        rank = 'Unranked'
    else:
        rank = max(1, 100000 - (len(solved) * 1532))
        
    return jsonify({'success': True, 'stats': {'problems_solved': len(solved), 'solved_trend': 0, 'streak': streak, 'global_rank': rank, 'mock_interviews': len(sessions)}})

@app.route('/api/dashboard/chart')
def get_dashboard_chart():
    user = get_candidate_data(session.get('user_id', 1))
    timestamps = user.get('solved_timestamps', [])
    
    labels = []
    data = [0] * 7
    today = datetime.date.today()
    
    for i in range(6, -1, -1):
        d = today - datetime.timedelta(days=i)
        labels.append(d.strftime('%a'))
    
    for ts in timestamps:
        try:
            d = datetime.datetime.fromisoformat(ts).date()
            delta = (today - d).days
            if 0 <= delta <= 6:
                data[6 - delta] += 1
        except Exception:
            pass
            
    return jsonify({'success': True, 'labels': labels, 'data': data})

@app.route('/api/dashboard/progress')
def get_dashboard_progress():
    rm_data = load_json(os.path.join(LEARNING_DIR, 'roadmaps.json'), {'roadmaps': []})
    progress = []
    color_map = {'#FFA116': 'primary', '#00B8A3': 'success', '#FF6B6B': 'error', '#FFC857': 'warning'}
    for rm in rm_data.get('roadmaps', []):
        total = 0
        done = 0
        for section in rm.get('sections', []):
            for node in section.get('nodes', []):
                total += 1
                if node.get('status') == 'done':
                    done += 1
        progress.append({
            'title': rm.get('title'),
            'completed': done,
            'total': total,
            'color': color_map.get(rm.get('color', '#FFA116'), 'primary'),
            'color_hex': rm.get('color', '#FFA116')
        })
    return jsonify({'success': True, 'progress': progress, 'top_skills': ['DSA', 'Web Dev', 'Algorithms', 'Python']})

@app.route('/api/dashboard/activity')
def get_dashboard_activity():
    user = get_candidate_data(session.get('user_id', 1))
    activities = user.get('activities', [])
    if not activities:
        activities = [{'title': 'Joined Placify', 'time': 'Recently', 'icon': 'user', 'color': 'primary'}]
    return jsonify({'success': True, 'activities': activities})

# AI CHAT
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json or {}
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'success': False, 'error': 'Empty message'}), 400
    system_prompt = ('You are Placify AI Coach, an expert computer science tutor specialising in DSA and interview prep. '
                     'Be concise, encouraging, and practical. Keep responses under 150 words.')
    user = get_candidate_data(session.get('user_id', 1))
    chat_hist = user.get('chat_history', [])
    
    # Format history for the AI
    history_text = ""
    if chat_hist:
        history_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in chat_hist[-6:]])
    
    chat_hist.append({'role': 'user', 'content': message})
    
    full_message = message
    if history_text:
        full_message = f"Previous conversation context:\n{history_text}\n\nCurrent Question: {message}"
        
    response_text = ask_groq(system_prompt, full_message)
    if response_text is None:
        return jsonify({'success': False, 'error': 'AI service is temporarily unavailable.'}), 503
    chat_hist.append({'role': 'assistant', 'content': response_text})
    user['chat_history'] = chat_hist[-50:]
    save_candidate_data(session.get('user_id', 1), user)
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
            user = get_candidate_data(session.get('user_id', 1))
            solved = user.get('solved_problems', [])
            if problem_id not in solved:
                solved.append(problem_id)
                
                timestamps = user.get('solved_timestamps', [])
                timestamps.append(datetime.datetime.now().isoformat())
                user['solved_timestamps'] = timestamps
                
                activities = user.get('activities', [])
                activities.insert(0, {'title': f"Solved: {problem.get('title')}", 'time': 'Just now', 'icon': 'check-circle-2', 'color': 'success'})
                user['activities'] = activities[:10]
                
            user['solved_problems'] = solved
            save_candidate_data(session.get('user_id', 1), user)
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
        if hint is None:
            return jsonify({'success': False, 'error': 'AI service is temporarily unavailable.'}), 503
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
    feedback_text = ask_groq(system_prompt, f'Topic: {topic}\n\n{qa_text}')
    if feedback_text is None:
        return jsonify({'success': False, 'error': 'AI service is temporarily unavailable.'}), 503
    score_match = re.search(r'SCORE:\s*(\d+)/10', feedback_text)
    score = int(score_match.group(1)) if score_match else 7
    for session in iv_data.get('past', []):
        if session.get('id') == session_id:
            session['feedback'] = feedback_text
            session['score'] = score
            break
    save_json(path, iv_data)
    return jsonify({'success': True, 'feedback': feedback_text, 'score': score})

@app.route('/api/interviews/session/chat', methods=['POST'])
def interview_session_chat():
    data = request.json or {}
    messages = data.get('messages', [])
    code = data.get('code', '')
    topic = data.get('topic', 'General Coding')
    
    if not messages:
        return jsonify({'success': False, 'error': 'No messages'}), 400
        
    if code.strip():
        system_prompt = (
            f"You are a technical interviewer at a top tech company conducting a pair-programming interview on the topic: {topic}. "
            "The candidate is writing code in an editor. Be concise, act like a real interviewer, ask them to explain their approach, "
            "and provide subtle hints if they are stuck. Do not give them the exact code solution. Keep your responses under 150 words.\n\n"
            f"Here is the candidate's current code in the editor:\n```python\n{code}\n```"
        )
    else:
        system_prompt = (
            f"You are a strict, professional interviewer at a top tech company conducting an interview on: {topic}. "
            "CRITICAL RULES: "
            "1. YOU ARE THE INTERVIEWER, the user is the candidate. "
            "2. YOU MUST ASK THE QUESTIONS. Never ask the candidate to ask you a question. "
            "3. Ask one question at a time, wait for the candidate to answer, then evaluate or ask a follow-up. "
            "4. Keep your responses under 100 words. Be concise."
        )
        

    vision_context = data.get('vision_context', '')
    final_prompt = system_prompt
    if vision_context:
        final_prompt += f"\n\n[SYSTEM OBSERVATION: {vision_context} - If they look unprofessional, nervous, or distracted, subtly call it out as a real interviewer would.]"
        
    # Directly format messages for Ollama API to avoid role confusion
    ollama_messages = [{"role": "system", "content": final_prompt}]
    
    # Pass actual message array
    for m in messages:
        # Ensure roles map to what Ollama expects: 'user' or 'assistant'
        role = 'assistant' if m['role'] == 'assistant' else 'user'
        ollama_messages.append({"role": role, "content": m['content']})
        
    payload = {
        "model": os.environ.get('OLLAMA_MODEL', 'qwen2.5:1.5b'),
        "messages": ollama_messages,
        "stream": False,
        "options": {
            "temperature": 0.7
        }
    }
    
    try:
        response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=60)
        response.raise_for_status()
        response_text = response.json()['message']['content'].strip()
        return jsonify({'success': True, 'response': response_text})
    except Exception as e:
        app.logger.error(f"Chat error: {e}")
        return jsonify({'success': False, 'error': 'AI service is temporarily unavailable.'}), 503



# USER/AUTH
@app.route('/api/user/profile', methods=['GET', 'POST'])
def user_profile():
    if request.method == 'POST':
        data = request.json or {}
        user = get_candidate_data(session.get('user_id', 1))
        if 'profile' not in user:
            user['profile'] = {}
        user['profile'].update({k: v for k, v in data.items() if k in ['name','email','title']})
        if 'preferences' in data:
            user.setdefault('preferences', {}).update(data['preferences'])
        save_candidate_data(session.get('user_id', 1), user)
        return jsonify({'success': True, 'message': 'Profile updated'})
    user = get_candidate_data(session.get('user_id', 1))
    return jsonify({'success': True,
                    'profile': user.get('profile', {'name':'Placify User','email':'user@placify.dev','title':'Software Engineer'}),
                    'preferences': user.get('preferences', {'email_notifications':True,'public_profile':True,'dark_mode':True})})




@app.route('/api/candidates/<int:candidate_id>/explanation', methods=['GET'])
def get_candidate_explanation(candidate_id):
    user = get_candidate_data(candidate_id)
    
    # Extract persisted scores
    resume_score = user.get('resume_score', 0)
    solved = user.get('solved_problems', [])
    coding_score = min(100, len(solved) * 20)  # simple scoring
    sql_score = None  # Implement later if we add SQL specific problems
    
    scores = {"resume": resume_score, "coding": coding_score, "sql": sql_score}
    candidate_skills = user.get('candidate_skills', [])
    
    # Load required skills from job_roles.json
    job_roles = load_json(os.path.join(BASE_DIR, 'data', 'job_roles.json'), {})
    targeted_role = user.get('targeted_role', 'backend_engineer')
    role_data = job_roles.get(targeted_role, {})
    required_skills = role_data.get('required_skills', ['python', 'sql'])
    
    # Default behavior metrics
    fraud_score = 0
    timing_anomalies = 0
    
    # Cross-check skills
    all_questions = load_json(os.path.join(ASSESSMENT_DIR, 'questions.json'), [])
    solved_objs = [q for q in all_questions if q.get('id') in solved]
    cross_check = cross_check_skills(candidate_skills, solved_objs)
    
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
    
    explanation['verified_skills'] = cross_check['verified_skills']
    explanation['unverified_skills'] = cross_check['unverified_skills']
    explanation['opportunities'] = cross_check['opportunities']
    
    return jsonify({'success': True, 'explanation': explanation})


@app.route('/api/candidates/<int:candidate_id>/simulate', methods=['POST'])
def simulate_skill_impact(candidate_id):
    data = request.json or {}
    hypothetical_skills = data.get('skills', [])
    
    user = get_candidate_data(candidate_id)
    
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
    
    all_questions = load_json(os.path.join(ASSESSMENT_DIR, 'questions.json'), [])
    solved_objs = [q for q in all_questions if q.get('id') in solved]
    
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
            
        expl = generate_explanation(
            candidate_id=candidate_id, decision=dec, final_score=f_score, scores=scores,
            confidence_score=conf_score, fraud_score=fraud_score, candidate_skills=c_skills,
            required_skills=required_skills, timing_anomalies=timing_anomalies,
            consistency_score=conf_res.get("consistency_confidence", 100.0)
        )
        cross_c = cross_check_skills(c_skills, solved_objs)
        expl['verified_skills'] = cross_c['verified_skills']
        expl['unverified_skills'] = cross_c['unverified_skills']
        expl['opportunities'] = cross_c['opportunities']
        return expl
        
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




@app.route('/api/interviews/session/analyze_frame', methods=['POST'])
def analyze_frame():
    data = request.json or {}
    image_b64 = data.get('image', '')
    if not image_b64:
        return jsonify({'success': False, 'error': 'No image provided'}), 400
        
    image_b64 = image_b64.split(',')[-1] # Remove data URI prefix if present
    
    ollama_url = "http://localhost:11434/api/generate"
    payload = {
        "model": "moondream",
        "prompt": "Describe the person's dress, body posture, and facial expression. Are they professional, confident, or nervous? Keep it to one short sentence.",
        "images": [image_b64],
        "stream": False
    }
    try:
        response = requests.post(ollama_url, json=payload, timeout=30)
        response.raise_for_status()
        observation = response.json().get('response', '').strip()
        return jsonify({'success': True, 'observation': observation})
    except Exception as e:
        app.logger.error(f"Vision error: {e}")
        return jsonify({'success': False, 'error': 'Vision analysis failed'}), 500

@app.route('/api/interviews/session/end', methods=['POST'])
def end_interview():
    data = request.json or {}
    messages = data.get('messages', [])
    topic = data.get('topic', 'General')
    vision_context = data.get('vision_context', '')
    if not messages:
        return jsonify({'success': False, 'error': 'No messages'}), 400
        
    history_text = ""
    for m in messages:
        role = "Interviewer" if m['role'] == 'assistant' else "Candidate"
        history_text += f"{role}: {m['content']}\n"
        
    prompt = (
        "You are a strict technical evaluator. Review the mock interview transcript provided below.\n\n"
        "CRITICAL RULES:\n"
        "1. DO NOT make up or hallucinate any questions, answers, or topics that are not explicitly written in the Chat History.\n"
        "2. If the Chat History is very short (e.g. just a 'hello'), clearly state that the interview was too short or abandoned, and give a score of N/A.\n"
        "3. Otherwise, provide feedback based ONLY on the actual questions asked and the candidate's actual answers.\n\n"
        "Format your review with:\n"
        "- Posture & Presentation (Based only on [SYSTEM OBSERVATION] notes)\n"
        "- Technical Areas to Improve\n"
        "- Overall Summary\n\n"
        f"Chat History:\n{history_text}\n"
        f"[SYSTEM OBSERVATION OF CANDIDATE]: {vision_context}\n"
    )
    
    response_text = ask_groq(prompt, "Please generate the review.")
    if response_text is None:
        return jsonify({'success': False, 'error': 'AI service is temporarily unavailable.'}), 503
        
    # Save the generated review
    import datetime
    path = os.path.join(INTERVIEWS_DIR, 'sessions.json')
    iv_data = load_json(path, {'upcoming': [], 'past': []})
    new_id = max([i.get('id',0) for i in iv_data.get('upcoming',[]) + iv_data.get('past',[])], default=0) + 1
    iv_data['past'].insert(0, {
        'id': new_id, 
        'topic': topic, 
        'date': datetime.datetime.now().strftime('%B %d, %Y'), 
        'rating': 'N/A', 
        'feedback': response_text
    })
    save_json(path, iv_data)
    
    return jsonify({'success': True, 'review': response_text})


# RESUME
@app.route('/api/resume/scan', methods=['POST'])
def scan_resume():
    try:
        file = None
        text = ''
        
        if request.is_json:
            data = request.get_json()
            text = data.get('text', '')
            base64_data = data.get('resume_base64')
            if base64_data:
                import tempfile, uuid, base64
                filename = data.get('filename', 'resume.pdf')
                temp_path = os.path.join(tempfile.gettempdir(), f'{uuid.uuid4()}_{filename}')
                with open(temp_path, 'wb') as f:
                    f.write(base64.b64decode(base64_data))
                try:
                    text = extract_text(temp_path)
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
        else:
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
                f'Resume:\n{text[:2000]}\n\nGive 3 specific improvement tips.')
            if ai_feedback is None:
                return jsonify({'success': False, 'error': 'AI service is temporarily unavailable.'}), 503
        
        user = get_candidate_data(session.get('user_id', 1))
        user['candidate_skills'] = result.get('skills_found', [])
        user['resume_score'] = result.get('match_score', 0)
        save_candidate_data(session.get('user_id', 1), user)
        
        response_text = f"<h3>Resume Scan Complete</h3><p>Match Score: {result.get('match_score')}%</p>"
        if result.get('skills_found'):
            response_text += f"<p>Skills found: {', '.join(result.get('skills_found'))}</p>"
        if ai_feedback:
            response_text += f"<h4>AI Recruiter Feedback:</h4><div>{ai_feedback.replace('*', '')}</div>"
        
        return jsonify({'success': True, 'result': response_text})
    except Exception as e:
        app.logger.error(f"Error scanning resume: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500



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
        user_prompt = f"Company: {company}\nRole: {role}\n"
        if study_text:
            user_prompt += f"Study Material/JD:\n{study_text[:3000]}\n"
            
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


# PLACEMENT SESSION PHASE 5 (ACTIVITIES)
@app.route('/api/placement-session/<session_id>/learning', methods=['GET'])
def api_placement_session_learning(session_id):
    topic = request.args.get('topic', 'General')
    try:
        content = generate_learning_content(session_id, topic, ask_groq)
        if "error" in content:
            return jsonify({"success": False, "error": content["error"]}), 500
        return jsonify({"success": True, "content": content})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/placement-session/<session_id>/learning/answer', methods=['POST'])
def api_placement_session_learning_answer(session_id):
    data = request.json
    topic = data.get("topic")
    is_correct = data.get("is_correct")
    gaps = process_learning_quiz_answer(session_id, topic, is_correct, ask_groq)
    return jsonify({"success": True, "skill_gaps": gaps})

@app.route('/api/placement-session/<session_id>/coding', methods=['GET'])
def api_placement_session_coding(session_id):
    topic = request.args.get('topic', 'General')
    question = generate_coding_challenge(topic)
    return jsonify({"success": True, "question": question})

@app.route('/api/placement-session/<session_id>/coding/submit', methods=['POST'])
def api_placement_session_coding_submit(session_id):
    data = request.json
    topic = data.get("topic")
    code_text = data.get("code")
    feedback = submit_coding_challenge(session_id, topic, code_text, ask_groq)
    # Give candidate a score bump for coding
    process_baseline_answer(session_id, topic, "hard", True, [], ask_groq)
    return jsonify({"success": True, "feedback": feedback})


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

if __name__ == '__main__':
    bootstrap_data()
    app.run(debug=True, port=5000)