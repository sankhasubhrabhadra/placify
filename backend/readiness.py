import os
import json
from backend.placement_session import get_session
from backend.baseline_assessment import compute_skill_gaps

def generate_readiness_report(session_id):
    session = get_session(session_id)
    if not session:
        return {"error": "Session not found"}
        
    gaps = compute_skill_gaps(session)
    skill_scores = {s["skill"]: s["score"] for s in session.get("candidate", {}).get("skill_scores", [])}
    
    # Calculate overall readiness
    # Weighted average of skills vs importance
    total_weight = 0
    total_score = 0
    
    reqs = session.get("company_role_intelligence", {}).get("extracted_requirements", [])
    
    strongest_areas = []
    remaining_risks = []
    
    for req in reqs:
        skill = req["skill"]
        conf = req["confidence"]
        score = skill_scores.get(skill, 50)
        
        weight = 3 if conf == "HIGH" else (2 if conf == "MEDIUM" else 1)
        total_weight += weight
        total_score += score * weight
        
        if score >= 80:
            strongest_areas.append({"skill": skill, "score": score})
        elif score < 60 and conf == "HIGH":
            remaining_risks.append({"skill": skill, "score": score})
            
    overall_readiness = (total_score / total_weight) if total_weight > 0 else 50
    session["session_metrics"]["readiness_percent"] = round(overall_readiness, 1)
    
    # Recommended final action
    time_remaining = session.get("session_metrics", {}).get("time_remaining_minutes", 0)
    if time_remaining > 30 and remaining_risks:
        final_action = f"Spend your remaining {time_remaining} mins doing coding practice for {remaining_risks[0]['skill']}."
    elif remaining_risks:
        final_action = f"Review high-level concepts for {remaining_risks[0]['skill']} before your interview."
    else:
        final_action = "Rest and hydrate. You are fully prepared."
        
    # generate_explanation style evidence
    evidence = []
    for h in session.get("assessment_history", []):
        evidence.append(f"Scored {h.get('score_delta', 0):+d} on {h.get('difficulty', 'unknown')} {h.get('topic', 'unknown')} quiz")
        
    return {
        "readiness_percent": round(overall_readiness, 1),
        "strongest_areas": sorted(strongest_areas, key=lambda x: x["score"], reverse=True)[:3],
        "remaining_risks": remaining_risks[:3],
        "recommended_final_action": final_action,
        "evidence_log": evidence[-5:] # Last 5 events
    }

def simulate_what_if(session_id, skill_to_improve):
    # What if they got this skill to 100?
    session = get_session(session_id)
    if not session:
        return {"error": "Session not found"}
        
    # Modify in memory (do not save)
    skill_scores = session.get("candidate", {}).get("skill_scores", [])
    found = False
    for ss in skill_scores:
        if ss["skill"].lower() == skill_to_improve.lower():
            ss["score"] = 100
            found = True
            break
            
    if not found:
        skill_scores.append({"skill": skill_to_improve, "score": 100})
        
    # Recompute gaps and readiness
    reqs = session.get("company_role_intelligence", {}).get("extracted_requirements", [])
    total_weight = 0
    total_score = 0
    skill_scores_dict = {s["skill"]: s["score"] for s in skill_scores}
    
    for req in reqs:
        skill = req["skill"]
        conf = req["confidence"]
        score = skill_scores_dict.get(skill, 50)
        weight = 3 if conf == "HIGH" else (2 if conf == "MEDIUM" else 1)
        total_weight += weight
        total_score += score * weight
        
    projected_readiness = (total_score / total_weight) if total_weight > 0 else 50
    return {
        "projected_readiness": round(projected_readiness, 1)
    }
