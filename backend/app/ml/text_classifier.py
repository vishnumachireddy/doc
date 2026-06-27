import re
from typing import Dict, Tuple

class TextDocumentClassifier:
    """
    Analyzes document text using keyword density profiling to classify 
    the text, cross-validates with visual layouts, and outputs final category predictions.
    """
    
    # Target keywords dictionary
    KEYWORDS = {
        "Resume": [
            "experience", "skills", "education", "projects", "summary", "employment",
            "professional", "technologies", "certifications", "achievements", "work history",
            "curriculum vitae", "languages", "contact details", "developer", "engineer"
        ],
        "Aadhaar Card": [
            "government of india", "unique identification", "uidai", "enrollment", "male",
            "female", "yob", "dob", "address", "aadhaar", "signature", "authority of india",
            "aadhaar number", "card"
        ],
        "PAN Card": [
            "income tax department", "permanent account number", "card", "signature", 
            "govt. of india", "pan", "father's name", "permanent account", "income tax",
            "tax assessment", "alphanumeric"
        ],
        "Passport": [
            "republic of india", "passport", "passport no", "given name", "surname",
            "nationality", "date of birth", "place of birth", "date of issue", "date of expiry",
            "passport index", "holder's signature", "republic"
        ],
        "Driving License": [
            "driving license", "licence no", "union of india", "dl no", "date of issue",
            "validity", "authorization", "class of vehicle", "transport", "licence", "non-transport",
            "licensing authority", "motor vehicle"
        ],
        "Marksheet": [
            "marksheet", "statement of marks", "marks obtained", "maximum marks", "roll no",
            "grade", "semester", "subject", "percentage", "failed", "passed", "board of secondary",
            "examination", "marks card", "marks statement", "total marks"
        ],
        "Degree Certificate": [
            "degree of", "bachelor of", "master of", "conferred on", "has been admitted to",
            "diploma", "university", "hereby certifies", "under the seal", "doctor of",
            "passing certificate", "convocation"
        ],
        "Invoice": [
            "invoice", "invoice number", "bill to", "ship to", "description", "quantity",
            "unit price", "total due", "amount due", "payment terms", "invoice date",
            "subtotal", "tax", "invoice no", "remit to"
        ],
        "Receipt": [
            "receipt", "received from", "amount received", "payment receipt", "transaction date",
            "thank you", "cashier", "amount paid", "sales receipt", "subtotal", "cash",
            "change due", "store no"
        ],
        "Bank Statement": [
            "bank statement", "account number", "account statement", "ledger balance",
            "transaction history", "withdrawal", "deposit", "balance", "description",
            "value date", "overdraft", "statement period", "transactions", "branch code"
        ]
    }

    def predict_text_category(self, text: str) -> Tuple[str, float]:
        """Predicts document type based on keyword occurrences in text."""
        if not text or len(text.strip()) < 10:
            return "Generic Document", 0.0

        text_lower = text.lower()
        scores = {}
        
        for category, keywords in self.KEYWORDS.items():
            match_count = 0
            for kw in keywords:
                # Use regex word boundaries for precise matching
                pattern = rf"\b{re.escape(kw)}\b" if len(kw.split()) == 1 else re.escape(kw)
                matches = re.findall(pattern, text_lower)
                if matches:
                    # Give higher weight to matches
                    match_count += len(matches)
            
            # Normalize score relative to the category keyword list size
            scores[category] = match_count / (len(keywords) + 2)

        best_category = max(scores, key=scores.get)
        raw_score = scores[best_category]
        
        # Scale score to a 0.0 - 1.0 range
        confidence = min(raw_score / 1.5, 1.0)
        
        if confidence < 0.15:
            return "Generic Document", 0.3
            
        return best_category, round(confidence, 2)

    def cross_validate(self, visual_label: str, visual_conf: float, text_label: str, text_conf: float) -> Tuple[str, float]:
        """
        Consolidates visual and textual classification passes.
        """
        # If text is extremely weak (OCR failed or empty image), default entirely to visual prediction
        if text_label == "Generic Document" and text_conf <= 0.0:
            return visual_label, visual_conf
            
        # If visual and textual predictions match
        if visual_label == text_label:
            final_conf = 0.65 * text_conf + 0.35 * visual_conf
            return visual_label, min(round(final_conf, 2), 1.0)
            
        # If they disagree
        # Resumes are highly text-dependent
        if text_label == "Resume" and text_conf > 0.6:
            return "Resume", text_conf
            
        # If textual classifier is highly confident, trust it
        if text_conf > 0.7:
            return text_label, text_conf
            
        # If visual classifier is highly confident, trust it
        if visual_conf > 0.75:
            return visual_label, visual_conf
            
        # Else, average them or favor the textual prediction
        final_conf = 0.6 * text_conf + 0.4 * visual_conf
        chosen_label = text_label if text_conf >= visual_conf else visual_label
        return chosen_label, min(round(final_conf, 2), 1.0)

text_document_classifier = TextDocumentClassifier()
