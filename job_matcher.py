import os
import sys

# Ensure current directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import re
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from text_cleaner import preprocess_text
from skill_extractor import extract_skills, load_skills_db

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Try loading SentenceTransformers for optional semantic matching
try:
    from sentence_transformers import SentenceTransformer
    # Cache model locally to avoid repeated downloads
    EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    HAS_SENTENCE_TRANSFORMERS = True
except Exception:
    HAS_SENTENCE_TRANSFORMERS = False
    EMBEDDING_MODEL = None

def load_job_roles() -> List[Dict[str, Any]]:
    """Load all 10 predefined job roles from CSV dataset."""
    roles_csv = os.path.join(DATA_DIR, "job_roles.csv")
    roles = []
    if os.path.exists(roles_csv):
        df = pd.read_csv(roles_csv)
        for _, row in df.iterrows():
            roles.append({
                "role_id": int(row["role_id"]),
                "role_name": str(row["role_name"]).strip(),
                "category": str(row["category"]).strip(),
                "required_skills": str(row["required_skills"]).strip(),
                "description": str(row["description"]).strip(),
                "experience_level": str(row["experience_level"]).strip(),
                "min_experience_years": int(row["min_experience_years"])
            })
    return roles

def calculate_tfidf_similarity(resume_text: str, job_description: str) -> float:
    """Calculate TF-IDF + Cosine Similarity score between resume and job role text."""
    clean_resume = preprocess_text(resume_text)
    clean_job = preprocess_text(job_description)

    if not clean_resume.strip() or not clean_job.strip():
        return 0.0

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform([clean_resume, clean_job])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(similarity * 100)
    except Exception:
        return 0.0

def calculate_semantic_similarity(resume_text: str, job_description: str) -> float:
    """Calculate optional semantic similarity using Sentence Transformers."""
    if not HAS_SENTENCE_TRANSFORMERS or EMBEDDING_MODEL is None:
        return 0.0
    
    clean_resume = preprocess_text(resume_text, lemmatize=False)
    clean_job = preprocess_text(job_description, lemmatize=False)

    try:
        embeddings = EMBEDDING_MODEL.encode([clean_resume, clean_job])
        sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        return float(max(0.0, sim) * 100)
    except Exception:
        return 0.0

def match_resume_with_job(resume_text: str, target_role_name: str, use_semantic: bool = False) -> Dict[str, Any]:
    """
    Match candidate resume against a specific target job role.
    Computes TF-IDF similarity, skill overlap score, missing skills, and composite match score.
    """
    roles = load_job_roles()
    target_role = next((r for r in roles if r["role_name"].lower() == target_role_name.lower()), None)
    
    if not target_role:
        target_role = roles[0] # Default to first role if specified role not found

    req_skills_list = [s.strip() for s in target_role["required_skills"].split(",") if s.strip()]
    extracted = extract_skills(resume_text)
    found_skills_list = extracted["found_skills"]

    # Skill match score calculation
    found_set = set(s.lower() for s in found_skills_list)
    req_set = set(s.lower() for s in req_skills_list)
    
    matching_skills = [s for s in req_skills_list if s.lower() in found_set]
    missing_skills = [s for s in req_skills_list if s.lower() not in found_set]

    skill_overlap_score = (len(matching_skills) / len(req_skills_list) * 100) if req_skills_list else 0.0

    # Combine description & required skills for text matching
    job_full_text = f"{target_role['role_name']} {target_role['description']} {target_role['required_skills']}"
    
    tfidf_score = calculate_tfidf_similarity(resume_text, job_full_text)

    if use_semantic and HAS_SENTENCE_TRANSFORMERS:
        semantic_score = calculate_semantic_similarity(resume_text, job_full_text)
        # Weighted combination: 40% TF-IDF, 30% Semantic, 30% Skill Overlap
        composite_score = (0.4 * tfidf_score) + (0.3 * semantic_score) + (0.3 * skill_overlap_score)
    else:
        # Standard combination: 60% TF-IDF Cosine Similarity, 40% Direct Skill Overlap
        composite_score = (0.6 * tfidf_score) + (0.4 * skill_overlap_score)

    final_match_score = round(min(100.0, max(0.0, composite_score)), 2)

    return {
        "target_role": target_role["role_name"],
        "category": target_role["category"],
        "match_score": final_match_score,
        "tfidf_score": round(tfidf_score, 2),
        "skill_overlap_score": round(skill_overlap_score, 2),
        "found_skills": found_skills_list,
        "matching_role_skills": matching_skills,
        "missing_skills": missing_skills,
        "required_skills": req_skills_list,
        "description": target_role["description"]
    }

def recommend_top_job_roles(resume_text: str, top_n: int = 3, use_semantic: bool = False) -> List[Dict[str, Any]]:
    """Compare resume against all 10 predefined job roles and return top N recommendations."""
    roles = load_job_roles()
    results = []
    
    for r in roles:
        res = match_resume_with_job(resume_text, r["role_name"], use_semantic=use_semantic)
        results.append(res)
    
    # Sort by match score descending
    sorted_results = sorted(results, key=lambda x: x["match_score"], reverse=True)
    return sorted_results[:top_n]

def analyze_resume_strength(raw_text: str, sections_detected: Dict[str, str], found_skills: List[str]) -> Dict[str, Any]:
    """
    Analyze resume strength across formatting, action verbs, skill diversity, experience depth, and impact metrics.
    """
    words = raw_text.split()
    word_count = len(words)

    # 1. Length & Readability Score (0-20)
    if 300 <= word_count <= 1000:
        readability_score = 20
    elif 150 <= word_count < 300 or 1000 < word_count <= 1500:
        readability_score = 15
    else:
        readability_score = 10

    # 2. Section Coverage Score (0-20)
    essential_sections = ["Education", "Experience", "Projects", "Skills"]
    present_sections = [sec for sec in essential_sections if sections_detected.get(sec, "").strip()]
    section_score = (len(present_sections) / len(essential_sections)) * 20

    # 3. Action Verbs & Impact Score (0-20)
    action_verbs = [
        "developed", "built", "engineered", "designed", "implemented", "optimized", "managed",
        "led", "architected", "deployed", "scaled", "reduced", "increased", "created", "spearheaded"
    ]
    raw_lower = raw_text.lower()
    verb_matches = [v for v in action_verbs if v in raw_lower]
    impact_score = min(20, len(verb_matches) * 4)

    # 4. Quantifiable Achievements (0-20)
    metrics_matches = re.findall(r'\b(\d+%\b|\$\d+|\d+\+|\d+x\b|increased|decreased|improved|reduced)', raw_lower)
    quantifiable_score = min(20, len(metrics_matches) * 5)

    # 5. Technical Skill Depth (0-20)
    skill_depth_score = min(20, len(found_skills) * 2)

    total_strength = round(readability_score + section_score + impact_score + quantifiable_score + skill_depth_score, 1)

    return {
        "total_strength_score": total_strength,
        "readability_score": readability_score,
        "section_score": section_score,
        "impact_score": impact_score,
        "quantifiable_score": quantifiable_score,
        "skill_depth_score": skill_depth_score,
        "word_count": word_count
    }

def generate_ai_suggestions(strength: Dict[str, Any], missing_skills: List[str], target_role: str) -> List[str]:
    """Generate intelligent resume improvement recommendations."""
    suggestions = []

    if strength["word_count"] < 300:
        suggestions.append("Length Warning: Your resume is concise (<300 words). Add key projects and detailed work responsibilities.")
    elif strength["word_count"] > 1000:
        suggestions.append("Format Optimization: Your resume is longer than 1000 words. Condense descriptions into punchy bullet points.")

    if strength["quantifiable_score"] < 15:
        suggestions.append("Add Metrics & Results: Quantify your achievements using numbers (e.g. 'Improved API latency by 35%').")

    if strength["impact_score"] < 12:
        suggestions.append("Use Strong Action Verbs: Start bullet points with impact verbs like Engineered, Optimized, Architected, and Spearheaded.")

    if missing_skills:
        top_missing = ", ".join(missing_skills[:5])
        suggestions.append(f"Keyword Gap: Add these high-demand skills for {target_role}: {top_missing}.")

    if strength["section_score"] < 20:
        suggestions.append("Missing Sections: Ensure explicit headers for Education, Work Experience, Key Projects, and Technical Skills.")

    if not suggestions:
        suggestions.append("Great job! Your resume demonstrates strong formatting, impact metrics, and relevant technical alignment.")

    return suggestions
