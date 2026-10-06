import os
import json
from backend.placement_session import get_session, save_session

def get_next_baseline_question(session_id, ask_groq_func):
    """
    Determines the next baseline question topic/difficulty and asks the LLM to generate it.
    """
    session = get_session(session_id)
    if not session:
        raise ValueError("Session not found")
        
    history = session.get("assessment_history", [])
    if len(history) >= 8:
        # Done with baseline
        return {"done": True, "skill_gaps": compute_skill_gaps(session)}
        
    # Pick a topic
    # For a baseline, we want to survey the top requirements
    reqs = session.get("company_role_intelligence", {}).get("extracted_requirements", [])
    if not reqs:
        # Fallback
        reqs = [{"skill": "General Software Engineering", "confidence": "HIGH"}]
        
    # Find a requirement we haven't asked many questions about, or one they scored poorly on
    # Simple logic: cycle through requirements
    req_index = len(history) % len(reqs)
    target_skill = reqs[req_index]["skill"]
    
    # Determine difficulty
    # Look at last question for this skill if any
    skill_history = [h for h in history if h.get("topic") == target_skill]
    difficulty = "medium"
    if skill_history:
        last_q = skill_history[-1]
        if last_q.get("score", 0) >= 80:
            difficulty = "hard"
        else:
            difficulty = "easy"
            
    # Generate question via LLM
    system_prompt = '''You are an expert technical interviewer.
Generate a multiple-choice conceptual question to test the candidate's knowledge.
Return ONLY valid JSON in this exact format:
{
  "question": "The question text",
  "options": ["A", "B", "C", "D"],
  "correct_index": 1,
  "explanation": "Why option B is correct."
}'''
    
    user_prompt = f"Topic: {target_skill}\\nDifficulty: {difficulty}"
    
    ai_response = ask_groq_func(system_prompt, user_prompt)
    if not ai_response:
        return {"error": "Failed to generate question"}
        
    try:
        if "```json" in ai_response:
            json_str = ai_response.split("```json")[1].split("```")[0].strip()
        else:
            json_str = ai_response.strip()
        q_data = json.loads(json_str)
        q_data["topic"] = target_skill
        q_data["difficulty"] = difficulty
        return {"done": False, "question": q_data}
    except Exception as e:
        return {"error": f"Failed to parse question JSON: {str(e)}"}

def process_baseline_answer(session_id, topic, difficulty, is_correct, mistakes, ask_groq_func=None):
    """
    Records an answer, updates skill scores.
    """
    session = get_session(session_id)
    if not session:
        raise ValueError("Session not found")
        
    # Calculate score bump
    score_change = 0
    if is_correct:
        if difficulty == "hard": score_change = +15
        elif difficulty == "medium": score_change = +10
        else: score_change = +5
    else:
        if difficulty == "hard": score_change = -5
        elif difficulty == "medium": score_change = -10
        else: score_change = -15
        
    # Update history
    import datetime
    session["assessment_history"].append({
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "type": "baseline_quiz",
        "topic": topic,
        "difficulty": difficulty,
        "is_correct": is_correct,
        "score_delta": score_change,
        "mistakes": mistakes
    })
    
    # Update candidate skill score
    skill_scores = session["candidate"].setdefault("skill_scores", [])
    found = False
    for ss in skill_scores:
        if ss["skill"] == topic:
            ss["score"] = max(0, min(100, ss.get("score", 50) + score_change))
            # Bump confidence since we have more evidence
            ss["confidence"] = "HIGH" if len([h for h in session["assessment_history"] if h.get("topic") == topic]) >= 2 else "MEDIUM"
            found = True
            break
            
    if not found:
        # Initialize
        new_score = max(0, min(100, 50 + score_change))
        skill_scores.append({
            "skill": topic,
            "score": new_score,
            "confidence": "LOW" # Starts low until more evidence
        })
        
    save_session(session_id, session)
    return compute_skill_gaps(session) # Return gaps for UI debugging

def compute_skill_gaps(session):
    """
    Compares candidate skill scores against the role's required skills.
    Ranked by gap size * role importance (confidence).
    """
    reqs = session.get("company_role_intelligence", {}).get("extracted_requirements", [])
    skill_scores = {s["skill"]: s["score"] for s in session.get("candidate", {}).get("skill_scores", [])}
    
    gaps = []
    for req in reqs:
        skill = req["skill"]
        conf = req["confidence"]
        
        # Determine importance multiplier based on confidence
        importance = 3 if conf == "HIGH" else (2 if conf == "MEDIUM" else 1)
        
        # If candidate hasn't been tested, assume score is 50
        candidate_score = skill_scores.get(skill, 50)
        
        # Gap = Target (100) - Candidate Score
        gap_size = 100 - candidate_score
        weighted_gap = gap_size * importance
        
        if gap_size > 0:
            gaps.append({
                "skill": skill,
                "candidate_score": candidate_score,
                "importance": conf,
                "gap_size": gap_size,
                "weighted_gap": weighted_gap
            })
            
    # Sort by weighted_gap descending
    gaps.sort(key=lambda x: x["weighted_gap"], reverse=True)
    return gaps
