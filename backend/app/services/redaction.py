import re

# Regex patterns for sensitive IDs
AADHAAR_REGEX = re.compile(r"\b\d{4}\s\d{4}\s\d{4}\b|\b\d{12}\b|\b\d{4}-\d{4}-\d{4}\b")
PAN_REGEX = re.compile(r"\b[a-zA-Z]{5}\d{4}[a-zA-Z]{1}\b")
PASSPORT_REGEX = re.compile(r"\b[a-zA-Z]{1}\d{7,8}\b")
# Driving License (e.g. DL-1420110012345 or DL14 20110012345)
DL_REGEX = re.compile(r"\b[a-zA-Z]{2}[-\s]?\d{2}[-\s]?\d{4}[-\s]?\d{7}\b|\b[a-zA-Z]{2}\d{13}\b")

def redact_sensitive_data(text: str, document_type: str) -> str:
    """
    Scans the extracted text and redacts sensitive ID digits based on the document type.
    """
    if not text:
        return ""

    redacted_text = text

    # Redact Aadhaar Card
    if document_type == "Aadhaar Card":
        redacted_text = AADHAAR_REGEX.sub("[REDACTED AADHAAR NUMBER]", redacted_text)
        
    # Redact PAN Card
    elif document_type == "PAN Card":
        redacted_text = PAN_REGEX.sub("[REDACTED PAN NUMBER]", redacted_text)
        
    # Redact Passport
    elif document_type == "Passport":
        redacted_text = PASSPORT_REGEX.sub("[REDACTED PASSPORT NUMBER]", redacted_text)
        
    # Redact Driving License
    elif document_type == "Driving License":
        redacted_text = DL_REGEX.sub("[REDACTED DRIVING LICENSE NUMBER]", redacted_text)

    # General fallback: if the document contains sensitive numbers, we can redact them too
    # but specific module requirement says "If a document is classified as a sensitive government identification card"
    return redacted_text
