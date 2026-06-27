import pytest
import os
import tempfile
from backend.app.services.binary_signature import validate_binary_signature
from backend.app.services.redaction import redact_sensitive_data
from backend.app.services.verification import calculate_file_hash, verify_document_quality
from backend.app.services.ats_analyzer import analyze_ats_compliance, calculate_flesch_readability, calculate_readiness_score
from backend.app.services.ai_detector import estimate_ai_likelihood

def test_binary_signature_validation():
    """Verifies that extension magic-byte checks work and block spoofing."""
    # Create temporary mock files
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"%PDF-1.4\ncontent")
        pdf_path = f.name
        
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        # Spoofed file: named PDF, but starts with zip archive headers
        f.write(b"PK\x03\x04ziparchivecontents")
        spoofed_path = f.name

    try:
        # Valid signature should return format 'pdf'
        assert validate_binary_signature(pdf_path) == "pdf"
        # Spoofed file should return the actual detected format 'docx' (or whatever maps PK header)
        assert validate_binary_signature(spoofed_path) != "pdf"
    finally:
        os.remove(pdf_path)
        os.remove(spoofed_path)

def test_pii_redaction_compliance():
    """Verifies text data protection masking for sensitive ID digits."""
    aadhaar_text = "My Aadhaar Card number is 1234 5678 9012. Date of birth is 01-01-2000."
    pan_text = "Please find my PAN details: ABCDE1234F."
    passport_text = "Passport number: Z1234567"
    dl_text = "DL No: DL1420110012345"

    # Aadhaar redaction
    redacted_aadhaar = redact_sensitive_data(aadhaar_text, "Aadhaar Card")
    assert "[REDACTED AADHAAR NUMBER]" in redacted_aadhaar
    assert "1234 5678 9012" not in redacted_aadhaar

    # PAN redaction
    redacted_pan = redact_sensitive_data(pan_text, "PAN Card")
    assert "[REDACTED PAN NUMBER]" in redacted_pan
    assert "ABCDE1234F" not in redacted_pan

    # Passport redaction
    redacted_passport = redact_sensitive_data(passport_text, "Passport")
    assert "[REDACTED PASSPORT NUMBER]" in redacted_passport
    assert "Z1234567" not in redacted_passport

    # DL redaction
    redacted_dl = redact_sensitive_data(dl_text, "Driving License")
    assert "[REDACTED DRIVING LICENSE NUMBER]" in redacted_dl
    assert "DL1420110012345" not in redacted_dl

def test_ats_scoring_metrics():
    """Verifies that the ATS Score drops appropriately for missing sections and contact data."""
    # Mock resume data missing Experience and Education
    bad_resume_data = {
        "contact": {"name": "Test"},
        "skills": [],
        "education": [],
        "experience": [],
        "projects": []
    }
    raw_text = "Test Resume\nThis is a simple text with no bullet points and no active verbs."
    
    score, suggestions = analyze_ats_compliance(bad_resume_data, raw_text)
    
    # Missing experience (-15), education (-10), projects (-10), skills (-15), contact phone/email (-20), bullet style (-5), active verbs (-10)
    # The score should be low
    assert score < 50
    assert len(suggestions["ats_formatting"]) > 0
    assert len(suggestions["action_verbs"]) > 0

def test_readability_calculations():
    """Validates Flesch Reading Ease ratings."""
    simple_text = "The cat sat on the rug. The dog barked at the cat. The sun is very bright."
    complex_text = "Anthropology is the scientific study of humanity, concerned with human behavior, human biology, cultures, societies, and linguistics."
    
    simple_score = calculate_flesch_readability(simple_text)
    complex_score = calculate_flesch_readability(complex_text)
    
    # Simple text should be much easier to read (higher score)
    assert simple_score > complex_score

def test_ai_authorship_detection():
    """Verifies burstiness and buzzwords tracking inside AI Detector."""
    ai_resume = "I spearheaded the leveraged implementation of synergized solutions. Furthermore, I delved into cutting-edge robust algorithms to holistically optimize driving success. It is a testament to vibrant ecosystems."
    human_resume = "I worked on the main website. I wrote Python code. I talked to customers to fix bugs. On Tuesday I deployed the database changes and we saw a small speed improvement."
    
    ai_analysis = estimate_ai_likelihood(ai_resume)
    human_analysis = estimate_ai_likelihood(human_resume)
    
    # AI resume contains many clichés and buzzwords, so it should score higher AI likelihood
    assert ai_analysis["ai_percentage"] > human_analysis["ai_percentage"]
