import re
from typing import Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.app.services.resume_parser import SKILL_TAXONOMY

def extract_jd_skills(jd_text: str) -> List[str]:
    """Scans the job description text for technical and soft skills in our taxonomy."""
    jd_lower = jd_text.lower()
    skills_found = []
    for keyword, clean_skill in SKILL_TAXONOMY.items():
        pattern = rf"\b{re.escape(keyword)}\b"
        if re.search(pattern, jd_lower) and clean_skill not in skills_found:
            skills_found.append(clean_skill)
    return skills_found

def match_resume_to_jd(resume_text: str, jd_text: str, resume_skills: List[str]) -> Dict[str, Any]:
    """
    Computes semantic similarity and skill overlap between resume and JD.
    """
    if not resume_text or not jd_text:
        return {
            "skill_match_percentage": 0,
            "missing_skills": [],
            "missing_keywords": [],
            "improvement_suggestions": ["Ensure both resume and job description are fully populated."]
        }

    # 1. Cosine Similarity via TF-IDF
    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf_matrices = vectorizer.fit_transform([resume_text, jd_text])
        similarity = cosine_similarity(tfidf_matrices[0:1], tfidf_matrices[1:2])[0][0]
    except Exception as e:
        print(f"Error calculating TF-IDF cosine similarity: {e}")
        similarity = 0.2

    # 2. Skill overlap calculation
    jd_skills = extract_jd_skills(jd_text)
    
    missing_skills = []
    matched_skills = []
    
    for skill in jd_skills:
        # Check case-insensitive presence in resume_skills or raw text
        if skill in resume_skills:
            matched_skills.append(skill)
        elif re.search(rf"\b{re.escape(skill.lower())}\b", resume_text.lower()):
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    # 3. Keyword Analysis (find high-frequency terms in JD that are absent in Resume)
    stop_words = ["and", "the", "with", "for", "to", "in", "of", "a", "an", "is", "are", "on", "as", "by", "at", "be", "we", "our", "you", "your", "will", "required", "experience", "role", "team", "work", "job", "candidate", "position"]
    
    jd_words = re.findall(r"\b\w{3,15}\b", jd_text.lower())
    jd_word_counts = {}
    for w in jd_words:
        if w not in stop_words and w not in [s.lower() for s in SKILL_TAXONOMY]:
            jd_word_counts[w] = jd_word_counts.get(w, 0) + 1
            
    # Get top keywords in JD
    sorted_keywords = sorted(jd_word_counts.keys(), key=lambda w: jd_word_counts[w], reverse=True)[:10]
    
    missing_keywords = []
    resume_lower = resume_text.lower()
    for kw in sorted_keywords:
        if not re.search(rf"\b{re.escape(kw)}\b", resume_lower):
            missing_keywords.append(kw)

    # 4. Compile overall match percentage
    # Combine TF-IDF similarity (40% weight) and Skill Match Ratio (60% weight)
    skill_ratio = len(matched_skills) / len(jd_skills) if jd_skills else 1.0
    
    raw_match_pct = (similarity * 0.4 + skill_ratio * 0.6) * 100
    match_pct = max(0, min(100, int(raw_match_pct)))
    
    # 5. Build improvement suggestions
    suggestions = []
    if missing_skills:
        suggestions.append(f"Incorporate the following required skills into your skills list or work descriptions: {', '.join(missing_skills[:5])}.")
    if missing_keywords:
        suggestions.append(f"Add key contextual terms from the job posting to align with recruiter search criteria: {', '.join(missing_keywords[:5])}.")
        
    if match_pct < 50:
        suggestions.append("The similarity score is low. Tailor your professional summary and experience bullet points to match the primary goals outlined in the job description.")
    elif match_pct < 80:
        suggestions.append("Solid alignment. Optimize your project descriptions by adding concrete examples of how you applied the missing skills.")
    else:
        suggestions.append("Excellent match! Your resume is highly aligned with the target job profile.")

    return {
        "skill_match_percentage": match_pct,
        "missing_skills": missing_skills,
        "missing_keywords": missing_keywords[:8],
        "improvement_suggestions": suggestions
    }
