"""
Scoring and Decision Logic Module

This module combines several scoring and logic engines:
1. Decision Explanation Generator - Generates human-readable explanations for hiring decisions.
2. Confidence Scoring System - Calculates multi-dimensional confidence scores (technical, consistency, behavior).
3. Skip Logic Engine - Determines intelligent assessment flow based on candidate performance.

Merged from:
- explanation/explainer.py
- scoring/confidence_scorer.py
- scoring/skip_logic.py
"""

import statistics
from typing import Dict, List, Optional


# =============================================================================
# 1. DECISION EXPLANATION GENERATOR
# =============================================================================

def generate_decision_summary(decision: str, final_score: float) -> str:
    """Generate one-line decision summary"""
    if decision == "shortlist":
        return f"Candidate shortlisted with strong performance (Score: {final_score}/100)"
    elif decision == "interview":
        return f"Candidate recommended for interview (Score: {final_score}/100)"
    elif decision == "reject":
        return f"Candidate not recommended (Score: {final_score}/100)"
    else:
        return f"Decision pending (Score: {final_score}/100)"


def generate_reasons(
    scores: Dict[str, Optional[int]],
    decision: str,
    confidence_score: float
) -> List[str]:
    """Generate list of reasons for the decision"""
    reasons = []
    
    resume_score = scores.get("resume", 0)
    coding_score = scores.get("coding", 0)
    sql_score = scores.get("sql", 0)
    
    if decision in ["shortlist", "interview"]:
        if resume_score >= 80:
            reasons.append(f"Strong resume match ({resume_score}% skill alignment)")
        if coding_score >= 85:
            reasons.append(f"Excellent coding performance (passed {coding_score}% of test cases)")
        elif coding_score >= 70:
            reasons.append(f"Good coding skills (passed {coding_score}% of test cases)")
        if sql_score and sql_score >= 80:
            reasons.append(f"Proficient in SQL ({sql_score}% accuracy)")
        if confidence_score >= 80:
            reasons.append(f"High confidence in assessment (confidence: {confidence_score}%)")
    else:  # reject
        if resume_score < 50:
            reasons.append(f"Insufficient skill match (only {resume_score}% alignment)")
        if coding_score < 60:
            reasons.append(f"Below average coding performance ({coding_score}% pass rate)")
        if sql_score and sql_score < 50:
            reasons.append(f"Weak SQL skills ({sql_score}% accuracy)")
        if confidence_score < 40:
            reasons.append(f"Low confidence in assessment (confidence: {confidence_score}%)")
    
    return reasons


def identify_skill_gaps(candidate_skills: List[str], required_skills: List[str]) -> List[str]:
    """Identify missing skills"""
    candidate_set = set(s.lower() for s in candidate_skills)
    required_set = set(s.lower() for s in required_skills)
    gaps = list(required_set - candidate_set)
    return sorted(gaps)


def identify_strengths(
    candidate_skills: List[str],
    required_skills: List[str],
    scores: Dict[str, Optional[int]]
) -> List[str]:
    """Identify candidate strengths"""
    strengths = []
    candidate_set = set(s.lower() for s in candidate_skills)
    required_set = set(s.lower() for s in required_skills)
    matched_skills = list(candidate_set & required_set)
    
    if matched_skills:
        strengths.extend(matched_skills)
    
    if scores.get("coding", 0) >= 85:
        strengths.append("strong problem-solving")
    if scores.get("sql", 0) and scores.get("sql", 0) >= 80:
        strengths.append("database expertise")
    
    return strengths


def generate_concerns(fraud_score: int, timing_anomalies: int, consistency_score: float) -> List[str]:
    """Generate list of concerns/red flags"""
    concerns = []
    if fraud_score > 60:
        concerns.append(f"High fraud risk detected (risk score: {fraud_score}/100)")
    elif fraud_score > 40:
        concerns.append(f"Moderate fraud risk (risk score: {fraud_score}/100)")
    if timing_anomalies > 2:
        concerns.append(f"Multiple timing anomalies detected ({timing_anomalies} instances)")
    elif timing_anomalies > 0:
        concerns.append(f"Timing anomaly detected in assessment")
    if consistency_score < 50:
        concerns.append(f"Inconsistent performance across assessments (consistency: {consistency_score}%)")
    return concerns


def generate_recommendation(decision: str, confidence_score: float) -> str:
    """Generate next step recommendation"""
    if decision == "shortlist":
        return "Proceed directly to final interview" if confidence_score >= 85 else "Proceed to technical interview"
    elif decision == "interview":
        return "Schedule technical interview to assess further"
    elif decision == "reject":
        return "Not recommended for this role"
    else:
        return "Awaiting manual review"


def generate_explanation(
    candidate_id: int,
    decision: str,
    final_score: float,
    scores: Dict[str, Optional[int]],
    confidence_score: float,
    fraud_score: int,
    candidate_skills: List[str],
    required_skills: List[str],
    timing_anomalies: int = 0,
    consistency_score: float = 100.0
) -> Dict:
    """Generate complete explanation for hiring decision"""
    return {
        "candidate_id": candidate_id,
        "decision": decision,
        "summary": generate_decision_summary(decision, final_score),
        "final_score": final_score,
        "confidence_score": confidence_score,
        "reasons": generate_reasons(scores, decision, confidence_score),
        "concerns": generate_concerns(fraud_score, timing_anomalies, consistency_score) or ["No major concerns identified"],
        "skill_gaps": identify_skill_gaps(candidate_skills, required_skills) or ["No significant skill gaps"],
        "strengths": identify_strengths(candidate_skills, required_skills, scores),
        "recommendation": generate_recommendation(decision, confidence_score)
    }


# =============================================================================
# 2. CONFIDENCE SCORING SYSTEM
# =============================================================================

def calculate_technical_confidence(scores: Dict[str, Optional[int]]) -> float:
    """Calculate technical confidence based on assessment scores"""
    valid_scores = [s for s in scores.values() if s is not None]
    if not valid_scores: return 0.0
    avg_score = sum(valid_scores) / len(valid_scores)
    bonus = sum(1 for s in valid_scores if s >= 80) * 5
    penalty = sum(1 for s in valid_scores if s < 50) * 10
    return round(min(100, max(0, avg_score + bonus - penalty)), 2)


def calculate_consistency_confidence(scores: List[int]) -> float:
    """Calculate consistency confidence based on score variance"""
    if len(scores) < 2: return 100.0
    std_dev = statistics.stdev(scores)
    return round(max(0, 100 - (std_dev * 3.33)), 2)


def calculate_behavior_confidence(fraud_score: int, timing_anomalies: int = 0) -> float:
    """Calculate behavior confidence based on fraud signals"""
    return round(max(0, (100 - fraud_score) - (timing_anomalies * 10)), 2)


def calculate_overall_confidence(
    technical_score: float,
    consistency_score: float,
    behavior_score: float,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """Calculate weighted overall confidence score"""
    w = weights or {"technical": 0.6, "consistency": 0.2, "behavior": 0.2}
    overall = (technical_score * w["technical"] + consistency_score * w["consistency"] + behavior_score * w["behavior"])
    return round(overall, 2)


def calculate_confidence_score(candidate_data: Dict) -> Dict:
    """Main function to calculate complete confidence analysis"""
    scores = candidate_data.get("scores", {})
    fraud_score = candidate_data.get("fraud_score", 0)
    timing_anomalies = candidate_data.get("timing_anomalies", 0)
    
    tech = calculate_technical_confidence(scores)
    consistency = calculate_consistency_confidence([s for s in scores.values() if s is not None])
    behavior = calculate_behavior_confidence(fraud_score, timing_anomalies)
    overall = calculate_overall_confidence(tech, consistency, behavior)
    
    return {
        "overall_confidence": overall,
        "technical_confidence": tech,
        "consistency_confidence": consistency,
        "behavior_confidence": behavior,
        "recommendation": "high" if overall >= 75 else "medium" if overall >= 50 else "low",
        "breakdown": {"technical_weight": 0.6, "consistency_weight": 0.2, "behavior_weight": 0.2}
    }


# =============================================================================
# 3. SKIP LOGIC ENGINE
# =============================================================================

def should_skip_easy_round(resume_score: int, coding_score: Optional[int] = None) -> bool:
    """Determine if candidate should skip easy coding round"""
    return resume_score > 85 or (coding_score is not None and coding_score > 90)


def should_add_verification_round(consistency_score: float, fraud_score: int) -> bool:
    """Determine if additional verification round is needed"""
    return consistency_score < 50 or fraud_score > 60


def should_fast_track(confidence_score: float, fraud_score: int) -> bool:
    """Determine if candidate should be fast-tracked"""
    return confidence_score > 85 and fraud_score < 20


def determine_next_stage(
    candidate_id: int,
    current_stage: str,
    scores: Dict[str, Optional[int]],
    confidence_score: float,
    fraud_score: int,
    consistency_score: float
) -> Dict:
    """Determine next assessment stage with skip logic"""
    resume_score = scores.get("resume", 0)
    skip_stages, add_stages, reason, fast_track = [], [], "", False
    
    if current_stage == "resume":
        if should_skip_easy_round(resume_score):
            skip_stages.append("easy_coding")
            next_stage, reason = "coding_medium", "High resume score, skipping easy coding round"
        else:
            next_stage, reason = "coding", "Proceeding to coding assessment"
    elif current_stage == "coding":
        if should_add_verification_round(consistency_score, fraud_score):
            add_stages.append("verification")
            next_stage, reason = "verification", "Inconsistent performance or fraud signals detected, adding verification"
        else:
            next_stage, reason = "sql", "Proceeding to SQL assessment"
    elif current_stage == "sql":
        if should_fast_track(confidence_score, fraud_score):
            next_stage, fast_track, reason = "interview", True, "High confidence candidate, fast-tracking to interview"
        else:
            next_stage, reason = "complete", "Assessment complete, awaiting decision"
    elif current_stage == "verification":
        next_stage, reason = "complete", "Verification complete, awaiting manual review"
    else:
        next_stage, reason = "complete", "Assessment pipeline complete"
    
    return {
        "next_stage": next_stage,
        "skip_stages": skip_stages,
        "add_stages": add_stages,
        "reason": reason,
        "fast_track": fast_track
    }
