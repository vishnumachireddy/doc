import re
import numpy as np
from typing import Dict, Any, List

# Common AI clichés and buzzwords in resumes
AI_CLICHES = [
    "spearheaded", "leveraged", "fostered", "synergy", "delved", "testament", 
    "vibrant", "holistic", "transformative", "driving success", "cutting-edge", 
    "robust", "demystify", "seamlessly", "furthermore", "moreover", "beacon", 
    "tapestry", "game-changer", "empowered", "elevated", "revolutionized"
]

def calculate_lexical_diversity(words: List[str]) -> float:
    """Computes Type-Token Ratio (unique words / total words)."""
    if not words:
        return 1.0
    unique_words = set(words)
    return len(unique_words) / len(words)

def calculate_burstiness(sentences: List[str]) -> float:
    """Calculates standard deviation of sentence lengths in words."""
    lengths = []
    for s in sentences:
        words = re.findall(r"\b\w+\b", s)
        if words:
            lengths.append(len(words))
            
    if len(lengths) < 3:
        return 8.0 # Standard normal variation default
        
    return float(np.std(lengths))

def estimate_ai_likelihood(text: str) -> Dict[str, Any]:
    """
    Estimates the probability that the text was written or assisted by AI.
    Returns:
    {
        "ai_percentage": int (0-100),
        "classification": str ("Mostly Human Written", "Human with AI Assistance", "Mostly AI Assisted"),
        "reasons": List[str]
    }
    """
    if not text or len(text.strip()) < 50:
        return {
            "ai_percentage": 0,
            "classification": "Mostly Human Written",
            "reasons": ["Text is too short to estimate authorship."]
        }

    # Split into sentences and words
    sentences = re.split(r"[.!?\n]+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    words = re.findall(r"\b\w+\b", text.lower())
    total_words = len(words)
    
    # Heuristics
    reasons = []
    ai_score = 10.0  # Base score
    
    # 1. Burstiness (sentence length variation)
    burstiness = calculate_burstiness(sentences)
    if burstiness < 3.5:
        ai_score += 25
        reasons.append("Low sentence length variance (very uniform pacing typical of AI models)")
    elif burstiness < 5.0:
        ai_score += 15
        reasons.append("Slightly uniform sentence lengths")
        
    # 2. Lexical Diversity (Type-Token Ratio)
    diversity = calculate_lexical_diversity(words)
    if diversity < 0.40:
        ai_score += 20
        reasons.append("Low vocabulary diversity (repetitive word selection)")
    elif diversity < 0.48:
        ai_score += 10
        
    # 3. Buzzwords / Clichés
    matched_cliches = []
    for cliche in AI_CLICHES:
        pattern = rf"\b{re.escape(cliche)}\b" if len(cliche.split()) == 1 else re.escape(cliche)
        matches = re.findall(pattern, text.lower())
        if matches:
            matched_cliches.append(cliche)
            
    cliche_weight = len(matched_cliches) * 6
    ai_score += min(35, cliche_weight)
    if len(matched_cliches) >= 5:
        reasons.append(f"Excessive corporate buzzwords & AI clichés: {', '.join(matched_cliches[:5])}")
    elif len(matched_cliches) >= 2:
        reasons.append(f"Contains multiple AI-preferred verbs: {', '.join(matched_cliches)}")

    # 4. Bullet Patterns
    # AI bullet points often start with similar structures: e.g. Action Verb + Adjective + noun
    # Let's count bullet point occurrences
    bullet_lines = [line.strip() for line in text.split("\n") if line.strip().startswith(("-", "*", "•"))]
    if len(bullet_lines) >= 4:
        # Check if they share very similar lengths
        bullet_word_counts = [len(line.split()) for line in bullet_lines]
        bullet_std = np.std(bullet_word_counts)
        if bullet_std < 2.5:
            ai_score += 15
            reasons.append("Highly standardized bullet point lengths indicating automated drafting templates")

    # Limit and round
    ai_percentage = min(99, max(5, int(ai_score)))
    
    # Classify
    if ai_percentage < 35:
        classification = "Mostly Human Written"
        if not reasons:
            reasons.append("Natural sentence length variation and vocabulary choice.")
    elif ai_percentage < 70:
        classification = "Human with AI Assistance"
        reasons.insert(0, "Features suggest human editing alongside AI structural guidance")
    else:
        classification = "Mostly AI Assisted"
        reasons.insert(0, "Highly structured sentence layouts indicate machine-generated content")

    return {
        "ai_percentage": ai_percentage,
        "classification": classification,
        "reasons": reasons
    }
