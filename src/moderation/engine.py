# src/moderation/engine.py
import logging
import re
from typing import List, Tuple

logger = logging.getLogger("moderation")

class KeywordFilter:
    """
    Local Regex-based filtering for speed.
    """
    
    # 1. Zero Tolerance (Hate Speech)
    BLOCKLIST = [
        r"\b(slur1|slur2)\b",  # Placeholder for actual blocklist
        r"\b(hate|kill)\s+(all|the)\b" # Contextual patterns
    ]
    
    # 2. Accusation / Libel Triggers (The Audit Fix)
    # AI cannot verify crimes. If it generates these, human must review.
    # We flag these as 'NEEDS_REVIEW' rather than 'BLOCK'.
    CRIME_KEYWORDS = [
        r"\b(stole|stealing)\b",
        r"\b(bribe|bribed|bribery)\b",
        r"\b(murder|murdered|killer)\b",
        r"\b(embezzle|embezzled)\b",
        r"\b(launder|laundering)\b",
        r"\b(trafficked|trafficking)\b",
        r"\b(scam|scammed|fraud)\b",
        r"\b(assault|assaulted)\b"
    ]

    def check_hate_speech(self, text: str) -> bool:
        """Returns True if hate speech detected."""
        for pattern in self.BLOCKLIST:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"BLOCKED: Hate speech pattern '{pattern}' matched.")
                return True
        return False

    def check_accusation(self, text: str) -> bool:
        """Returns True if potential libel found."""
        for pattern in self.CRIME_KEYWORDS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.info(f"FLAGGED: Accusation pattern '{pattern}' matched.")
                return True
        return False

class ModerationEngine:
    """
    The Referee.
    Orchestrates filters and LLM safety checks.
    """
    
    def __init__(self):
        self.keyword_filter = KeywordFilter()

    async def check_content(self, text: str) -> dict:
        """
        Run all checks.
        Returns: { 'status': 'PASS' | 'BLOCK' | 'REVIEW', 'reason': str }
        """
        
        # 1. Local Blocklist (Fastest)
        if self.keyword_filter.check_hate_speech(text):
            return {"status": "BLOCK", "reason": "Hate Speech"}
            
        # 2. Accusation Logic (Legal Safety)
        if self.keyword_filter.check_accusation(text):
            return {"status": "REVIEW", "reason": "Potential Libel/Accusation"}
            
        # 3. LLM Safety (API Call - Mocked for MVP)
        # Using Gemini Safety Settings would happen here
        # settings = {HARM_CATEGORY_HATE_SPEECH: BLOCK_LOW_AND_ABOVE}
        is_unsafe = False 
        
        if is_unsafe:
             return {"status": "BLOCK", "reason": "LLM Safety Filter"}
             
        return {"status": "PASS", "reason": None}

