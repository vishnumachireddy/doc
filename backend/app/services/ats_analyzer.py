import re
from typing import Dict, Any, List, Tuple

# List of strong action verbs
ACTION_VERBS = [
    "spearheaded", "designed", "engineered", "implemented", "managed", "led", 
    "developed", "built", "optimized", "launched", "coordinated", "accomplished",
    "achieved", "executed", "formulated", "initiated", "pioneered", "restructured",
    "supervised", "directed", "constructed", "established", "increased"
]

def count_syllables(word: str) -> int:
    """Estimates the number of syllables in a word."""
    word = word.lower().strip()
    if not word:
        return 0
    # Simple syllable counting heuristic
    vowels = "aeiouy"
    count = 0
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
    if word.endswith("e"):
        count -= 1
    if count == 0:
        count = 1
    return count

def calculate_flesch_readability(text: str) -> float:
    """
    Calculates the Flesch Reading Ease score.
    Formula: 206.835 - 1.015 * (ASL) - 84.6 * (ASW)
    ASL = Average Sentence Length (words / sentences)
    ASW = Average Syllables per Word (syllables / words)
    """
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = re.findall(r"\b\w+\b", text)
    
    total_sentences = len(sentences)
    total_words = len(words)
    
    if total_sentences == 0 or total_words == 0:
        return 60.0 # standard average readability
        
    total_syllables = sum(count_syllables(w) for w in words)
    
    asl = total_words / total_sentences
    asw = total_syllables / total_words
    
    score = 206.835 - (1.015 * asl) - (84.6 * asw)
    return max(0.0, min(100.0, score))

def analyze_ats_compliance(extracted_data: Dict[str, Any], raw_text: str) -> Tuple[int, Dict[str, List[str]]]:
    """
    Scores the resume and builds a suggestions dictionary.
    """
    score = 100
    suggestions = {
        "project_descriptions": [],
        "skills_ordering": [],
        "bullet_points": [],
        "action_verbs": [],
        "missing_keywords": [],
        "summary_improvements": [],
        "ats_formatting": []
    }
    
    # 1. Check Missing Sections
    # experience, education, projects, skills, certifications
    exp = extracted_data.get("experience", [])
    edu = extracted_data.get("education", [])
    proj = extracted_data.get("projects", [])
    skills = extracted_data.get("skills", [])
    contact = extracted_data.get("contact", {})
    
    if not exp:
        score -= 15
        suggestions["ats_formatting"].append("Missing 'Experience' or 'Work History' section. Recruiters prioritize work record.")
    if not edu:
        score -= 10
        suggestions["ats_formatting"].append("Missing 'Education' section. Include degrees, university names, and graduation years.")
    if not proj:
        score -= 10
        suggestions["ats_formatting"].append("Missing 'Projects' section. Show practical applications of your technical skills.")
    if not skills:
        score -= 15
        suggestions["ats_formatting"].append("Missing 'Skills' section. Compile technical competencies in a visible list.")
        
    # 2. Check Contact details
    if not contact.get("email"):
        score -= 10
        suggestions["ats_formatting"].append("Missing email address. Make sure contact info is in the header.")
    if not contact.get("phone"):
        score -= 10
        suggestions["ats_formatting"].append("Missing phone number. Ensure recruiters can reach you easily.")

    # 3. Check Bullet Point Consistency
    # Look for bullet characters (-, *, •) in Experience and Projects
    bullet_patterns = [r"^\s*[-*•]\s", r"^\s*\d+\.\s"]
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    has_bullets = any(any(re.match(pat, line) for pat in bullet_patterns) for line in lines)
    if not has_bullets:
        score -= 5
        suggestions["bullet_points"].append("Format work descriptions using clean, single-character bullet points (-, *, or •) instead of paragraphs.")

    # 4. Check Action Verbs
    found_verbs = []
    text_lower = raw_text.lower()
    for verb in ACTION_VERBS:
        if re.search(rf"\b{verb}\b", text_lower):
            found_verbs.append(verb)
            
    if len(found_verbs) < 5:
        score -= 10
        suggestions["action_verbs"].append(f"Found only {len(found_verbs)} active verbs. Incorporate strong actions like: 'spearheaded', 'designed', 'optimized'.")
    else:
        suggestions["action_verbs"].append("Excellent use of active verbs! Your sentences convey ownership.")

    # 5. Check Readability
    readability = calculate_flesch_readability(raw_text)
    if readability < 30.0:
        score -= 5
        suggestions["ats_formatting"].append("Low Readability Ease (Very Difficult). Use simpler sentences and avoid overly academic phrasing.")
    elif readability > 80.0:
        # Too simple might indicate lack of technical vocabulary
        suggestions["summary_improvements"].append("Readability is highly casual. Ensure technical terms are properly defined.")
    else:
        suggestions["ats_formatting"].append("Readability is in the optimal professional range (30-70).")

    # 6. Check Keyword / Skill Density
    if len(skills) < 6:
        score -= 10
        suggestions["missing_keywords"].append("Fewer than 6 technical skills detected. List core technologies and tools.")
    elif len(skills) > 25:
        score -= 5
        suggestions["skills_ordering"].append("More than 25 skills listed. Group and order them by proficiency to avoid cluttering.")

    # 7. Suggestions for Project Descriptions
    for pr in proj:
        desc = pr.get("description", "")
        if len(desc) < 80:
            suggestions["project_descriptions"].append(f"Project '{pr.get('title')}' description is too short. Describe the technologies used, challenges solved, and your individual contribution.")

    # Bound score
    score = max(0, min(100, score))
    return score, suggestions

def calculate_readiness_score(ats_score: int, skill_durations: Dict[str, float]) -> int:
    """
    Computes a Recruiter Readiness Score based on ATS score, number of skills, 
    and total accumulated years of experience.
    """
    total_exp_years = sum(skill_durations.values())
    # Experience factor: 3 points per year of experience (max 30)
    exp_factor = min(30, total_exp_years * 3)
    
    # Base weight: 70% of ATS score + experience factor
    readiness = int(ats_score * 0.7 + exp_factor)
    return max(0, min(100, readiness))
