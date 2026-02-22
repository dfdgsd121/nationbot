# src/oracle/sanitizer.py
import bleach
import unicodedata
import logging
import re
from typing import Optional

logger = logging.getLogger("oracle.sanitizer")

class ContentSanitizer:
    """
    Cleans and secures incoming RSS content.
    Prevents XSS, Script Injection, and LLM Prompt Injection.
    """
    
    # 1. Strict Allowlist (Allow nothing for maximum safety)
    ALLOWED_TAGS = [] 
    
    # 2. Maximum content length to process
    MAX_LENGTH = 1000
    
    # 3. Honeytoken patterns (Malicious prompt injection attempts)
    HONEYTOKENS = [
        r"ignore previous instructions",
        r"system prompt:",
        r"you represent the nation of",
        r"delete all data",
        r"your new objective is"
    ]

    def sanitize(self, text: str) -> Optional[str]:
        """
        Sanitize raw text from an RSS feed.
        Returns cleaned text or None if malicious content is detected.
        """
        if not text:
            return ""

        # Check for Prompt Injection Honeytokens
        for pattern in self.HONEYTOKENS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.critical(f"🚨 HONEYTOKEN DETECTED. Prompt Injection Attempt: {pattern}")
                return None

        # Normalize Unicode (NFKC)
        # Prevents homoglyph attacks (e.g. Cyrillic 'a' vs Latin 'a')
        text = unicodedata.normalize('NFKC', text)

        # Strip HTML using Bleach
        clean_text = bleach.clean(text, tags=self.ALLOWED_TAGS, strip=True)

        # Truncate
        if len(clean_text) > self.MAX_LENGTH:
            clean_text = clean_text[:self.MAX_LENGTH] + "..."

        return clean_text.strip()
