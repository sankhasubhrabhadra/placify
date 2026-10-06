from backend.baseline_assessment import compute_skill_gaps

def get_next_activity(session):
    """
    Determines the next best activity for the candidate.
    Returns: {activity_type, topic, reason, expected_impact, estimated_minutes}
    """
    time_remaining = session.get("session_metrics", {}).get("time_remaining_minutes", 0)
    
    if time_remaining <= 5:
        return {
            "activity_type": "readiness_report",
            "topic": "Final Review",
            "reason": "Less than 5 minutes remain in your time budget.",
            "expected_impact": "Consolidate results and provide a final Go/No-Go readiness score.",
            "estimated_minutes": 5
        }
        
    history = session.get("assessment_history", [])
    if len(history) < 8:
        return {
            "activity_type": "baseline_quiz",
            "topic": "General Assessment",
            "reason": "We need to complete your baseline assessment to accurately map your skill gaps.",
            "expected_impact": "Identifies which topics to prioritize for the remainder of the session.",
            "estimated_minutes": 15
        }
        
    time_budget = session.get("target", {}).get("time_budget_minutes", 120)
    time_spent = time_budget - time_remaining
    completed_activities = [act for act in session.get("current_plan", {}).get("activities", []) if act.get("status") == "completed"]
    breaks_taken = len([a for a in completed_activities if a.get("type") == "break"])
    
    if time_spent > (breaks_taken + 1) * 45:
        return {
            "activity_type": "break",
            "topic": "Rest",
            "reason": "You've been studying for 45 minutes straight. A short break improves retention.",
            "expected_impact": "Cognitive refresh before the next intensive module.",
            "estimated_minutes": 5
        }

    gaps = compute_skill_gaps(session)
    if not gaps:
        return {
            "activity_type": "mock_interview",
            "topic": "Comprehensive",
            "reason": "No major skill gaps detected. You are ready for a full mock interview.",
            "expected_impact": "Synthesize all skills under interview pressure.",
            "estimated_minutes": min(time_remaining, 45)
        }
        
    top_gap = gaps[0]
    topic = top_gap["skill"]
    
    recent_topic_activities = [a for a in completed_activities if a.get("topic") == topic]
    if not recent_topic_activities:
        return {
            "activity_type": "learning_mode",
            "topic": topic,
            "reason": f"'{topic}' is a high-priority requirement (Gap size: {top_gap['gap_size']}) where you scored below the target threshold.",
            "expected_impact": f"Provides foundational understanding of {topic} before assessment.",
            "estimated_minutes": 10
        }
    else:
        last_act_type = recent_topic_activities[-1].get("type")
        if last_act_type == "learning_mode":
            return {
                "activity_type": "quiz_mode",
                "topic": topic,
                "reason": f"You just reviewed {topic}. Let's verify your understanding with a quick adaptive quiz.",
                "expected_impact": f"Validates {topic} comprehension and increases candidate skill confidence.",
                "estimated_minutes": 10
            }
        elif last_act_type == "quiz_mode":
            return {
                "activity_type": "coding_mode",
                "topic": topic,
                "reason": f"You passed the conceptual quiz for {topic}. Now it's time to apply it in a sandboxed coding environment.",
                "expected_impact": f"Proves execution capability for {topic}, turning claimed skills into demonstrated skills.",
                "estimated_minutes": 20
            }
        else:
            if len(gaps) > 1:
                alt_gap = gaps[1]
                return {
                    "activity_type": "learning_mode",
                    "topic": alt_gap["skill"],
                    "reason": f"You struggled with {topic}. We're pivoting to {alt_gap['skill']} to maintain momentum and capture other points.",
                    "expected_impact": f"Secures points in {alt_gap['skill']} while giving your brain a break from {topic}.",
                    "estimated_minutes": 10
                }
            else:
                return {
                    "activity_type": "mock_interview",
                    "topic": "Comprehensive",
                    "reason": "We've exhausted targeted practice. Time for the final mock interview.",
                    "expected_impact": "Final assessment of readiness.",
                    "estimated_minutes": min(time_remaining, 45)
                }

def replan_roadmap(session):
    """
    Called after an assessment result. Recalculates the remaining roadmap based on the orchestrator.
    Returns the new plan and a top-level explanation.
    """
    if "current_plan" not in session:
        session["current_plan"] = {"activities": []}
        
    # Mark previous active as completed BEFORE running the orchestrator
    for act in session["current_plan"]["activities"]:
        if act.get("status") == "active":
            act["status"] = "completed"

    next_act = get_next_activity(session)
    
    current_activity = {
        "id": len(session["current_plan"]["activities"]) + 1,
        "type": next_act["activity_type"],
        "topic": next_act["topic"],
        "status": "active",
        "reason": next_act["reason"]
    }
            
    session["current_plan"]["activities"].append(current_activity)
    
    return session["current_plan"], next_act["reason"]
