import re
import os
from datetime import datetime
from typing import Dict, Any, List, Tuple
from backend.app.core.config import settings

# Comprehensive skill taxonomy (Technical & Soft Skills)
SKILL_TAXONOMY = {
    "python": "Python", "javascript": "JavaScript", "typescript": "TypeScript",
    "react": "React", "node": "Node.js", "django": "Django", "flask": "Flask",
    "fastapi": "FastAPI", "sql": "SQL", "postgresql": "PostgreSQL", "mysql": "MySQL",
    "mongodb": "MongoDB", "redis": "Redis", "docker": "Docker", "kubernetes": "Kubernetes",
    "aws": "AWS", "azure": "Azure", "gcp": "GCP", "git": "Git", "machine learning": "Machine Learning",
    "deep learning": "Deep Learning", "nlp": "NLP", "tensorflow": "TensorFlow", "pytorch": "PyTorch",
    "scikit-learn": "scikit-learn", "html": "HTML", "css": "CSS", "tailwind": "Tailwind CSS",
    "angular": "Angular", "vue": "Vue.js", "java": "Java", "c++": "C++", "c#": "C#",
    "php": "PHP", "ruby": "Ruby", "go": "Go", "rust": "Rust", "agile": "Agile",
    "scrum": "Scrum", "project management": "Project Management", "communication": "Communication",
    "leadership": "Leadership", "teamwork": "Teamwork", "problem solving": "Problem Solving"
}

# Months lookup for date parsing
MONTHS_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    "january": 1, "february": 2, "march": 3, "april": 4, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
}

def parse_dates_and_calculate_duration(text: str) -> float:
    """
    Finds date ranges (e.g., 'Jan 2018 - Dec 2020', '2019 to Present', '06/2015 - 12/2019')
    in text and returns duration in years. Defaults to 1.0 year if none found.
    """
    text_lower = text.lower()
    
    # 1. Match full date patterns (Month Year - Month Year)
    # e.g., 'Jan 2018 - Dec 2020', '06/2015 to 12/2019'
    month_regex = r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?|\d{1,2})"
    year_regex = r"(\d{4})"
    range_separator = r"(?:\s+(?:to|-|until)\s+|\s*-\s*)"
    
    pattern = rf"{month_regex}[\s/,-]*{year_regex}{range_separator}(?:{month_regex}[\s/,-]*{year_regex}|(present|current|now))"
    match = re.search(pattern, text_lower)
    
    if match:
        groups = match.groups()
        start_month_str = groups[0]
        start_year_str = groups[1]
        end_month_str = groups[2]
        end_year_str = groups[3]
        present_str = groups[4]
        
        try:
            # Parse start date
            start_year = int(start_year_str)
            start_month = 1
            if start_month_str.isdigit():
                start_month = int(start_month_str)
            elif start_month_str in MONTHS_MAP:
                start_month = MONTHS_MAP[start_month_str]
                
            # Parse end date
            if present_str:
                end_year = datetime.now().year
                end_month = datetime.now().month
            else:
                end_year = int(end_year_str)
                end_month = 1
                if end_month_str.isdigit():
                    end_month = int(end_month_str)
                elif end_month_str in MONTHS_MAP:
                    end_month = MONTHS_MAP[end_month_str]
                    
            months = (end_year - start_year) * 12 + (end_month - start_month)
            return max(0.5, round(months / 12.0, 2))
        except Exception:
            pass
            
    # 2. Fallback to year-only ranges (e.g. 2018 - 2020)
    year_range_pattern = r"\b(\d{4})\s*-\s*(\d{4}|present|current)\b"
    match_years = re.search(year_range_pattern, text_lower)
    if match_years:
        try:
            start_year = int(match_years.group(1))
            end_val = match_years.group(2)
            if end_val in ["present", "current"]:
                end_year = datetime.now().year
            else:
                end_year = int(end_val)
            return max(0.5, float(end_year - start_year))
        except Exception:
            pass
            
    return 1.0 # Default fallback duration for a listed job

def extract_skills_chronologically(experience_blocks: List[str]) -> Dict[str, float]:
    """
    Evaluates skills inside experience text blocks and computes the 
    chronological years of experience associated with each skill.
    """
    skill_durations = {}
    
    for block in experience_blocks:
        duration = parse_dates_and_calculate_duration(block)
        block_lower = block.lower()
        
        # Check which skills are mentioned in this specific experience block
        for keyword, clean_skill in SKILL_TAXONOMY.items():
            pattern = rf"\b{re.escape(keyword)}\b"
            if re.search(pattern, block_lower):
                skill_durations[clean_skill] = skill_durations.get(clean_skill, 0.0) + duration
                
    return {k: round(v, 1) for k, v in skill_durations.items()}

def segment_resume_text(text: str) -> Dict[str, str]:
    """Divides resume text into sections based on typical headings."""
    sections = {
        "summary": "",
        "experience": "",
        "education": "",
        "projects": "",
        "certifications": "",
        "achievements": ""
    }
    
    lines = text.split("\n")
    current_section = "summary"
    section_buffer = []
    
    # Header trigger mappings
    headings = {
        "experience": ["experience", "work history", "employment", "professional background", "career history"],
        "education": ["education", "academic background", "qualification", "studies"],
        "projects": ["projects", "personal projects", "academic projects", "key projects"],
        "certifications": ["certifications", "certs", "courses", "licenses"],
        "achievements": ["achievements", "awards", "accomplishments", "honors"]
    }
    
    for line in lines:
        cleaned_line = line.strip().lower()
        if not cleaned_line:
            continue
            
        # Check if line is a section heading
        found_heading = False
        for sec_name, keywords in headings.items():
            for kw in keywords:
                # Match line that matches exactly or starts with heading (like "EXPERIENCE")
                if cleaned_line == kw or cleaned_line.startswith(kw + ":") or (len(cleaned_line) < 30 and cleaned_line.startswith(kw)):
                    sections[current_section] += "\n".join(section_buffer)
                    current_section = sec_name
                    section_buffer = []
                    found_heading = True
                    break
            if found_heading:
                break
                
        if not found_heading:
            section_buffer.append(line)
            
    sections[current_section] += "\n".join(section_buffer)
    return sections

def rule_based_resume_parser(text: str) -> Dict[str, Any]:
    """Deterministic fallback parsing for Resume details."""
    text_lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    # 1. Contact Details
    email = None
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    if email_match:
        email = email_match.group(0)
        
    phone = None
    phone_match = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\b\d{10}\b", text)
    if phone_match:
        phone = phone_match.group(0)
        
    # Name (often first line if it's 2-3 words)
    name = "Applicant"
    for line in text_lines[:5]:
        words = line.split()
        if 2 <= len(words) <= 3 and not any(w.lower() in ["resume", "cv", "curriculum", "email", "phone", "profile"] for w in words):
            name = line
            break

    # Segment document
    segmented = segment_resume_text(text)
    
    # 2. Extract Skills
    skills_found = []
    text_lower = text.lower()
    for kw, clean_skill in SKILL_TAXONOMY.items():
        pattern = rf"\b{re.escape(kw)}\b"
        if re.search(pattern, text_lower) and clean_skill not in skills_found:
            skills_found.append(clean_skill)

    # 3. Parse Experience blocks
    exp_text = segmented["experience"]
    # Split experience text by typical job separator boundaries (e.g. empty lines or date boundaries)
    # Let's break it down into blocks starting with years or lines
    exp_blocks = [block.strip() for block in exp_text.split("\n\n") if len(block.strip()) > 30]
    if not exp_blocks:
        # fallback splitting by lines
        exp_blocks = [block.strip() for block in exp_text.split("\n") if len(block.strip()) > 50]
        
    skill_durations = extract_skills_chronologically(exp_blocks)
    
    experience_list = []
    for block in exp_blocks:
        lines = block.split("\n")
        role = lines[0] if lines else "Professional Experience"
        duration_str = "1 Year"
        duration_val = parse_dates_and_calculate_duration(block)
        
        # Try to find dates in text block to display as duration string
        date_match = re.search(r"\b\d{4}\b", block)
        if date_match:
            duration_str = f"Role ({duration_val} yrs)"
            
        experience_list.append({
            "role": role[:100],
            "company": "Organization",
            "duration": duration_str,
            "years": duration_val,
            "description": block[:300] + "..." if len(block) > 300 else block
        })

    # 4. Parse Education items
    edu_text = segmented["education"]
    edu_lines = [line for line in edu_text.split("\n") if len(line.strip()) > 15]
    education_list = []
    for line in edu_lines[:3]:
        year_match = re.search(r"\b\d{4}\b", line)
        year = year_match.group(0) if year_match else "N/A"
        education_list.append({
            "degree": line[:100],
            "institution": "University / Institute",
            "year": year
        })

    # 5. Parse Projects
    proj_text = segmented["projects"]
    proj_blocks = [b.strip() for b in proj_text.split("\n\n") if len(b.strip()) > 20]
    if not proj_blocks:
        proj_blocks = [line.strip() for line in proj_text.split("\n") if len(line.strip()) > 40]
    project_list = []
    for b in proj_blocks[:4]:
        lines = b.split("\n")
        title = lines[0] if lines else "Project"
        project_list.append({
            "title": title[:100],
            "description": b[:300] + "..." if len(b) > 300 else b
        })

    # 6. Certifications & Achievements
    certs_found = [c.strip() for c in segmented["certifications"].split("\n") if len(c.strip()) > 10]
    achieve_found = [a.strip() for a in segmented["achievements"].split("\n") if len(a.strip()) > 10]

    return {
        "contact": {"name": name, "email": email, "phone": phone},
        "skills": skills_found[:15],
        "skill_durations": skill_durations,
        "education": education_list,
        "experience": experience_list,
        "projects": project_list,
        "certifications": certs_found[:5],
        "achievements": achieve_found[:5]
    }

def call_gemini_parser(text: str) -> Dict[str, Any] | None:
    """Uses the Gemini Generative AI SDK to parse the Resume in structured JSON format."""
    if not settings.GEMINI_API_KEY:
        return None
        
    try:
        import google.generativeai as genai
        import json
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Extract the following structured details from this resume text.
        Return ONLY a raw JSON block with no markdown wrappers or explanation.
        
        JSON schema:
        {{
            "contact": {{ "name": "Name or null", "email": "Email or null", "phone": "Phone or null" }},
            "skills": ["Skill1", "Skill2", ...],
            "education": [{{ "degree": "Degree/Major", "institution": "School", "year": "Graduation Year" }}],
            "experience": [{{ "role": "Job Title", "company": "Company Name", "duration": "Duration (e.g. 2018-2020)", "years": 2.5, "description": "Short summary of responsibilities" }}],
            "projects": [{{ "title": "Project name", "description": "Details" }}],
            "certifications": ["Certification name"],
            "achievements": ["Achievement summary"]
        }}
        
        Resume Text:
        {text}
        """
        
        response = model.generate_content(prompt)
        # Parse output
        clean_text = response.text.strip()
        # Strip markdown markers if returned
        if clean_text.startswith("```"):
            clean_text = re.sub(r"^```(?:json)?\n|```$", "", clean_text, flags=re.MULTILINE).strip()
            
        data = json.loads(clean_text)
        return data
    except Exception as e:
        print(f"Gemini API parsing failed: {e}")
        return None

def parse_resume(text: str) -> Dict[str, Any]:
    """
    Tries Gemini structured extraction first;
    falls back to deterministic local rule-based parsing.
    """
    # 1. Try LLM parser
    parsed_data = call_gemini_parser(text)
    
    # 2. Fallback to rule-based parser
    if not parsed_data:
        parsed_data = rule_based_resume_parser(text)
    else:
        # Calculate skills duration locally using the structured experience descriptions
        # extracted by Gemini, as it adds precision
        exp_blocks = []
        for exp in parsed_data.get("experience", []):
            block_text = f"{exp.get('role')} at {exp.get('company')} during {exp.get('duration')}. {exp.get('description')}"
            exp_blocks.append(block_text)
            
        parsed_data["skill_durations"] = extract_skills_chronologically(exp_blocks)
        
    return parsed_data
