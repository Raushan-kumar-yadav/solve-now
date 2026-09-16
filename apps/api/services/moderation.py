import re
from sqlalchemy.orm import Session
from typing import Dict, Any

from models.moderation import ContentFlag

# Basic PII and spam heuristics
PII_PATTERNS = [
    re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'), # Email
    re.compile(r'\b(?:\+?1[-.\s]?)?\(?[2-9][0-8][0-9]\)?[-.\s]?[2-9][0-9]{2}[-.\s]?[0-9]{4}\b') # US Phone
]

SPAM_KEYWORDS = [
    "buy now",
    "click here",
    "free money",
    "crypto investment"
]

def analyze_content(content: str) -> Dict[str, Any]:
    """
    Automated risk analysis based on heuristics, PII, and spam patterns.
    """
    flags = {
        "pii_detected": False,
        "spam_detected": False
    }
    
    # Check PII
    for pattern in PII_PATTERNS:
        if pattern.search(content):
            flags["pii_detected"] = True
            break
            
    # Check Spam
    content_lower = content.lower()
    for keyword in SPAM_KEYWORDS:
        if keyword in content_lower:
            flags["spam_detected"] = True
            break
            
    # Risk scoring
    if flags["pii_detected"] or flags["spam_detected"]:
        risk_level = "HIGH"
    else:
        # We could have medium for borderline cases, but for now it's low or high
        risk_level = "LOW"
        
    return {
        "risk_level": risk_level,
        "flags": flags
    }

def record_flags(db: Session, entity_type: str, entity_id: str, analysis: Dict[str, Any]):
    if analysis["risk_level"] != "LOW":
        flag = ContentFlag(
            entity_type=entity_type,
            entity_id=entity_id,
            risk_level=analysis["risk_level"],
            flags=analysis["flags"]
        )
        db.add(flag)
        db.commit()

