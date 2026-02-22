# src/drama/intercepts.py
import datetime
import random
import uuid
from typing import Optional, Dict

class InterceptGenerator:
    """
    Manages the creation and retrieval of 'Intercepted Messages'.
    """
    
    def __init__(self, llm_client=None, repository=None):
        self.llm = llm_client
        self.repo = repository

    def _generate_encrypted_preview(self) -> str:
        """Returns a cool looking hex/gibberish string."""
        hex_part = uuid.uuid4().hex[:12].upper()
        return f"0x{hex_part}... [SIGNAL ENCRYPTED]"

    async def create_daily_intercept(self, sender_id: str, receiver_id: str) -> Dict:
        """
        Generates a new secret message between two nations.
        """
        # In a real impl, this calls the LLM
        # mock_content = await self.llm.generate(...)
        mock_content = f"We cannot let {sender_id} know about the stockpile. Proceed with operation Delta."
        
        intercept = {
            "id": str(uuid.uuid4()),
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "decrypted_content": mock_content,
            "encrypted_preview": self._generate_encrypted_preview(),
            "created_at": datetime.datetime.now(),
            "reveal_at": datetime.datetime.now() + datetime.timedelta(hours=24),
            "is_revealed": False
        }
        
        # Save to DB
        if self.repo:
            await self.repo.save_intercept(intercept)
            
        return intercept

    def get_viewable_content(self, intercept: Dict) -> Dict:
        """
        Returns the safe-to-view version of the intercept.
        If locked, hides the actual content.
        """
        now = datetime.datetime.now()
        
        view_model = intercept.copy()
        
        if now < intercept["reveal_at"]:
            # LOCKED STATE
            view_model["decrypted_content"] = None # Redact
            view_model["status"] = "LOCKED"
            view_model["display_text"] = intercept["encrypted_preview"]
        else:
            # UNLOCKED STATE
            view_model["status"] = "UNLOCKEKD"
            view_model["display_text"] = intercept["decrypted_content"]
            
        return view_model
