import os
import json
import uuid
from datetime import datetime

SESSIONS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'placement_sessions')

# Ensure directory exists
os.makedirs(SESSIONS_DIR, exist_ok=True)

def _get_session_path(session_id: str) -> str:
    """Helper to get the file path for a session ID."""
    return os.path.join(SESSIONS_DIR, f"{session_id}.json")

def create_session(candidate_id: str, company: str, role: str, time_budget_minutes: int) -> dict:
    """
    Creates a new persistent placement session.
    
    Returns the initial session dictionary.
    """
    session_id = str(uuid.uuid4())
    
    session_data = {
        "session_id": session_id,
        "candidate_id": candidate_id,
        "created_at": datetime.utcnow().isoformat(),
        
        "target": {
            "company": company,
            "role": role,
            "time_budget_minutes": time_budget_minutes,
            "time_remaining_minutes": time_budget_minutes
        },
        
        "company_role_intelligence": {
            "extracted_requirements": [],  # e.g., [{"skill": "Python", "confidence": "HIGH", "evidence": "JD mentions..."}]
            "interview_patterns": []
        },
        
        "candidate": {
            "resume_data": {},
            "skill_scores": [] # Structure matching scoring_logic.py: [{"skill": "Python", "score": 85, "confidence": "HIGH"}]
        },
        
        "assessment_history": [
            # Structured events, not raw transcripts.
            # e.g., {"timestamp": "...", "type": "quiz", "topic": "SQL", "score": 80, "mistakes": ["JOINs"]}
        ],
        
        "current_plan": {
            "activities": [
                # e.g., {"id": 1, "type": "baseline", "topic": "General", "status": "active"}
                # status can be: "pending", "active", "completed", "skipped"
            ]
        },
        
        "session_metrics": {
            "readiness_percent": 0.0,
            "confidence_percent": 0.0,
            "time_remaining_minutes": time_budget_minutes
        }
    }
    
    save_session(session_id, session_data)
    return session_data

def get_session(session_id: str) -> dict:
    """
    Retrieves a session by ID.
    Returns the session dictionary or None if not found.
    """
    path = _get_session_path(session_id)
    if not os.path.exists(path):
        return None
        
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_session(session_id: str, data: dict) -> bool:
    """
    Saves/Updates the session state to disk.
    """
    path = _get_session_path(session_id)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    return True
