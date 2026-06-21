"""
Modern ATS-style resume screening.

Parses PDF/DOCX/plain text resumes, extracts structured signals, and scores
candidates against a job profile using keyword matching, semantic similarity,
experience fit, education alignment, and profile completeness.
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import docx
import pdfplumber
import os
import json

logger = logging.getLogger(__name__)

SKILL_TAXONOMY: Dict[str, List[str]] = {
    "python": ["python", "python3", "py"],
    "javascript": ["javascript", "js", "ecmascript"],
    "typescript": ["typescript", "ts"],
    "java": ["java", "jvm"],
    "go": ["golang", " go ", "go language"],
    "rust": ["rust", "rustlang"],
    "c++": ["c++", "cpp"],
    "c#": ["c#", "csharp", ".net"],
    "sql": ["sql", "structured query language"],
    "postgresql": ["postgresql", "postgres", "psql"],
    "mysql": ["mysql", "mariadb"],
    "mongodb": ["mongodb", "mongo"],
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi"],
    "react": ["react", "reactjs", "react.js"],
    "node": ["node.js", "nodejs", "node "],
    "api": ["api", "apis"],
    "rest": ["rest", "restful", "rest api"],
    "docker": ["docker", "containerization", "containers"],
    "kubernetes": ["kubernetes", "k8s"],
    "aws": ["aws", "amazon web services", "ec2", "s3", "lambda"],
    "gcp": ["gcp", "google cloud"],
    "azure": ["azure", "microsoft azure"],
    "machine learning": ["machine learning", "ml ", " deep learning", "neural network"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "spark": ["spark", "pyspark", "apache spark"],
    "airflow": ["airflow", "apache airflow"],
    "terraform": ["terraform"],
    "jenkins": ["jenkins", "ci/cd", "cicd", "continuous integration"],
    "spring": ["spring", "spring boot"],
    "etl": ["etl", "data pipeline", "data pipelines"],
}

SECTION_HEADERS = [
    "experience", "work experience", "professional experience", "employment",
    "skills", "technical skills", "core competencies",
    "education", "academic", "qualification",
    "projects", "personal projects", "key projects",
    "summary", "profile", "objective",
    "certifications", "achievements",
]

ATS_WEIGHTS = {
    "required_skills": 35,
    "preferred_skills": 10,
    "semantic_skills": 15,
    "experience": 20,
    "education": 10,
    "profile_completeness": 5,
    "achievements": 5,
}

SHORTLIST_THRESHOLD = 65


@dataclass
class ParsedResume:
    raw_text: str
    normalized_text: str
    skills: List[str] = field(default_factory=list)
    experience_years: float = 0.0
    projects: int = 0
    education_hits: List[str] = field(default_factory=list)
    sections_found: List[str] = field(default_factory=list)
    contact: Dict[str, Optional[str]] = field(default_factory=dict)
    achievement_signals: int = 0
    keyword_density: float = 0.0


def extract_text(file_path: Union[str, Path]) -> str:
    """Extract raw text from PDF or DOCX resume files."""
    path = Path(file_path)
    if path.suffix.lower() == ".pdf":
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
        return text
    if path.suffix.lower() in [".docx", ".doc"]:
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")
    raise ValueError(f"Unsupported file type: {path.suffix}")


def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[\u2022\u2023\u25E6\u2043\u2219]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return f" {text} "


def _match_skill(normalized_text: str, skill: str, aliases: List[str]) -> bool:
    for term in [skill, *aliases]:
        term = term.strip().lower()
        if len(term) <= 3:
            pattern = rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])"
        else:
            pattern = re.escape(term)
        if re.search(pattern, normalized_text):
            return True
    return False


def extract_skills(text: str) -> List[str]:
    """Detect technical skills using taxonomy aliases and word boundaries."""
    normalized = _normalize(text)
    found = []
    for skill, aliases in SKILL_TAXONOMY.items():
        if _match_skill(normalized, skill, aliases):
            found.append(skill)
    return sorted(set(found))


def extract_contact(text: str) -> Dict[str, Optional[str]]:
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    phone_match = re.search(
        r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3}[\s.-]?\d{4,}",
        text,
    )
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    name = lines[0] if lines and len(lines[0].split()) <= 5 and "@" not in lines[0] else None
    return {
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0).strip() if phone_match else None,
        "name": name,
    }


def detect_sections(normalized_text: str) -> List[str]:
    found = []
    for header in SECTION_HEADERS:
        pattern = rf"(?<![a-z]){re.escape(header)}(?![a-z])"
        if re.search(pattern, normalized_text):
            found.append(header)
    return found


def extract_experience_years(text: str) -> float:
    """Estimate total experience from explicit years and employment date ranges."""
    normalized = _normalize(text)
    explicit = re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs)(?:\s+of\s+experience)?", normalized)
    explicit_years = max((float(v) for v in explicit), default=0.0)

    range_years = 0.0
    month_map = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }

    range_pattern = re.compile(
        r"(?:(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s,./-]*)?"
        r"(\d{4})\s*[-–—to]+\s*(?:(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s,./-]*)?"
        r"(present|current|\d{4})",
        re.IGNORECASE,
    )

    for match in range_pattern.finditer(text):
        start_year = int(match.group(2))
        end_token = match.group(4).lower()
        end_year = 2026 if end_token in {"present", "current"} else int(end_token)
        years = max(end_year - start_year, 0)
        if years <= 45:
            range_years += years

    if range_years:
        return round(max(explicit_years, min(range_years, 40)), 1)
    return round(explicit_years, 1)


def count_projects(text: str) -> int:
    normalized = _normalize(text)
    project_headers = len(re.findall(r"(?<![a-z])(project|portfolio)(?![a-z])", normalized))
    bullet_projects = len(re.findall(r"(built|developed|created|implemented|designed|architected)", normalized))
    return max(project_headers, min(bullet_projects // 2, 20))


def extract_education_hits(text: str, keywords: List[str]) -> List[str]:
    normalized = _normalize(text)
    hits = []
    for keyword in keywords:
        if keyword.lower() in normalized:
            hits.append(keyword.lower())
    degree_patterns = ["bachelor", "master", "phd", "b.tech", "m.tech", "b.e.", "m.e.", "mba", "bsc", "msc"]
    for degree in degree_patterns:
        if degree in normalized:
            hits.append(degree)
    return sorted(set(hits))


def count_achievement_signals(text: str) -> int:
    patterns = [
        r"\d+\s*%",
        r"\$\d+",
        r"\d+\s*(users|customers|requests|transactions|team members|engineers)",
        r"(increased|decreased|reduced|improved|scaled|optimized)",
    ]
    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, text.lower()))
    return count


def compute_keyword_density(normalized_text: str, keywords: List[str]) -> float:
    if not keywords:
        return 0.0
    words = [w for w in normalized_text.split() if w.strip()]
    if not words:
        return 0.0
    hits = sum(1 for word in words if any(k in word or word in k for k in keywords))
    return round(hits / len(words), 4)


def parse_resume(text: str) -> ParsedResume:
    normalized = _normalize(text)
    skills = extract_skills(text)
    all_keywords = list(SKILL_TAXONOMY.keys())
    return ParsedResume(
        raw_text=text,
        normalized_text=normalized,
        skills=skills,
        experience_years=extract_experience_years(text),
        projects=count_projects(text),
        education_hits=[],
        sections_found=detect_sections(normalized),
        contact=extract_contact(text),
        achievement_signals=count_achievement_signals(text),
        keyword_density=compute_keyword_density(normalized, all_keywords),
    )


def _semantic_skill_coverage(resume: ParsedResume, required_skills: List[str]) -> Tuple[float, List[str]]:
    """Score how well unmatched required skills appear semantically in the resume using Groq."""
    if not required_skills:
        return 1.0, []

    exact = set(resume.skills)
    missing = [skill for skill in required_skills if skill not in exact]
    if not missing:
        return 1.0, []

    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        logger.warning("GROQ_API_KEY not set. Skipping semantic skill check.")
        return 0.0, []

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        prompt = (
            f"Resume excerpt:\n{resume.raw_text[:4000]}\n\n"
            f"Missing required skills: {', '.join(missing)}\n\n"
            "Analyze the resume excerpt and determine if any of the 'Missing required skills' "
            "are implicitly mentioned or proven by the candidate's experience. "
            "Return ONLY a valid JSON list of strings (e.g. [\"python\", \"react\"]). "
            "If none are found, return []."
        )
        resp = client.chat.completions.create(
            model='llama3-8b-8192',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=200,
            temperature=0.0
        )
        content = resp.choices[0].message.content.strip()
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            found = json.loads(match.group(0))
            near_matches = [s.lower() for s in found if isinstance(s, str) and s.lower() in missing]
            score = len(near_matches) / len(missing) if missing else 0.0
            return (score, near_matches)
    except Exception as exc:
        logger.error("Semantic skill scoring failed via Groq: %s", exc)
        
    return 0.0, []


def _score_bucket(actual: float, target: float, weight: float) -> float:
    if target <= 0:
        return weight
    ratio = min(actual / target, 1.0)
    return ratio * weight


def _score_skill_match(resume: ParsedResume, skills: List[str], weight: float) -> Tuple[float, List[str], List[str]]:
    if not skills:
        return weight, [], []
    matched = [skill for skill in skills if skill in resume.skills]
    ratio = len(matched) / len(skills)
    return ratio * weight, matched, [skill for skill in skills if skill not in matched]


def score_resume(resume: ParsedResume, job_config: Dict) -> Dict:
    """
    Modern ATS composite score (0-100) with transparent breakdown.
    """
    required = [s.lower() for s in job_config.get("required_skills", job_config.get("skills", []))]
    preferred = [s.lower() for s in job_config.get("preferred_skills", [])]
    min_exp = float(job_config.get("min_exp", 0))
    education_keywords = [k.lower() for k in job_config.get("education_keywords", [])]

    resume.education_hits = extract_education_hits(resume.raw_text, education_keywords)

    req_points, matched_required, missing_required = _score_skill_match(resume, required, ATS_WEIGHTS["required_skills"])
    pref_points, matched_preferred, missing_preferred = _score_skill_match(resume, preferred, ATS_WEIGHTS["preferred_skills"])

    semantic_ratio, semantic_hits = _semantic_skill_coverage(resume, missing_required)
    semantic_points = semantic_ratio * ATS_WEIGHTS["semantic_skills"]

    experience_points = _score_bucket(resume.experience_years, min_exp, ATS_WEIGHTS["experience"])

    education_points = 0.0
    if education_keywords:
        education_points = min(len(resume.education_hits) / max(len(education_keywords), 1), 1.0) * ATS_WEIGHTS["education"]
    else:
        education_points = ATS_WEIGHTS["education"] if resume.sections_found else ATS_WEIGHTS["education"] * 0.5

    completeness_checks = [
        bool(resume.contact.get("email")),
        bool(resume.contact.get("phone")),
        any("experience" in s or "employment" in s for s in resume.sections_found),
        any("skill" in s for s in resume.sections_found),
        any("education" in s or "academic" in s for s in resume.sections_found),
    ]
    completeness_ratio = sum(completeness_checks) / len(completeness_checks)
    completeness_points = completeness_ratio * ATS_WEIGHTS["profile_completeness"]

    achievement_target = 3
    achievement_points = min(resume.achievement_signals / achievement_target, 1.0) * ATS_WEIGHTS["achievements"]

    total = round(
        req_points + pref_points + semantic_points + experience_points +
        education_points + completeness_points + achievement_points,
        2,
    )

    return {
        "total_score": min(total, 100.0),
        "breakdown": {
            "required_skills": round(req_points, 2),
            "preferred_skills": round(pref_points, 2),
            "semantic_skills": round(semantic_points, 2),
            "experience": round(experience_points, 2),
            "education": round(education_points, 2),
            "profile_completeness": round(completeness_points, 2),
            "achievements": round(achievement_points, 2),
        },
        "matched_required": matched_required,
        "missing_required": missing_required,
        "matched_preferred": matched_preferred,
        "missing_preferred": missing_preferred,
        "semantic_hits": semantic_hits,
    }


def generate_resume_explanation(score_payload: Dict, resume: ParsedResume, job_config: Dict) -> Dict:
    """Build ATS-style decision output for the frontend."""
    score = score_payload["total_score"]
    matched_required = score_payload["matched_required"]
    missing_required = score_payload["missing_required"]
    matched_preferred = score_payload["matched_preferred"]
    semantic_hits = score_payload["semantic_hits"]
    breakdown = score_payload["breakdown"]

    reasons = []

    if matched_required:
        reasons.append(f"Matched required skills: {', '.join(matched_required)}")
    if missing_required:
        reasons.append(f"Missing required skills: {', '.join(missing_required)}")
    if semantic_hits:
        reasons.append(f"Semantically related skills detected: {', '.join(semantic_hits)}")
    if matched_preferred:
        reasons.append(f"Preferred skills found: {', '.join(matched_preferred)}")

    min_exp = job_config.get("min_exp", 0)
    if resume.experience_years >= min_exp:
        reasons.append(f"Experience meets requirement ({resume.experience_years} yrs vs {min_exp} yrs minimum)")
    else:
        reasons.append(f"Experience below requirement ({resume.experience_years} yrs vs {min_exp} yrs minimum)")

    if resume.education_hits:
        reasons.append(f"Education signals: {', '.join(resume.education_hits[:4])}")

    if resume.contact.get("email"):
        reasons.append("Contact email detected")
    else:
        reasons.append("No email found — ATS parse warning")

    if resume.achievement_signals:
        reasons.append(f"Quantified achievements detected ({resume.achievement_signals} signals)")

    reasons.append(
        "Score breakdown — "
        + ", ".join(f"{key.replace('_', ' ')}: {value}" for key, value in breakdown.items())
    )

    decision = "SHORTLISTED" if score >= SHORTLIST_THRESHOLD else "REJECTED"
    if score >= SHORTLIST_THRESHOLD and missing_required and not semantic_hits:
        reasons.append("Shortlisted with caution: some required skills still missing")

    return {
        "decision": decision,
        "score": score,
        "reasons": reasons,
        "threshold": SHORTLIST_THRESHOLD,
        "job_title": job_config.get("title", "Role"),
    }


def scan_resume_text(text: str, job_config: Dict) -> Dict:
    """End-to-end ATS scan used by the Flask route."""
    if not text or not text.strip():
        raise ValueError("Resume text is empty")

    resume = parse_resume(text)
    score_payload = score_resume(resume, job_config)
    explanation = generate_resume_explanation(score_payload, resume, job_config)

    return {
        "skills": resume.skills,
        "experience": resume.experience_years,
        "projects": resume.projects,
        "score": score_payload["total_score"],
        "explanation": explanation,
        "contact": resume.contact,
        "sections_found": resume.sections_found,
        "breakdown": score_payload["breakdown"],
    }
