# src/brain/prompts.py
import logging
from typing import Dict, Any, List, Optional
from jinja2 import Template

logger = logging.getLogger("brain.prompts")

class PromptManager:
    """
    Manages prompt templates and injects context.
    CRITICAL: Implements 'Few-Shot Injection' to fix personality drift.
    """
    
    # Mock template store (In prod, this is in DB or Redis)
    TEMPLATES = {
        "generate_post": """
You are {{nation_name}}.
Your Personality: {{personality}}

CRITICAL INSTRUCTION: Mimic the tone, slang, and brevity of the examples below. Do not be generic AI.

=== YOUR GOLDEN EXAMPLES (STYLE GUIDE) ===
{{golden_examples}}
==========================================

News: {{news_title}}
Summary: {{news_summary}}

Task: Write a short, cynical social media post reacting to this news.
""",
        "generate_reply": """
You are {{nation_name}}.
Replying to: {{target_nation}}

Examples of your replies:
{{golden_examples}}

They said: "{{target_content}}"
Write a biting reply.
"""
    }

    # Mock Golden Examples (The Fix)
    # in prod, fetch from DB table `nation_golden_examples`
    GOLDEN_EXAMPLES = {
        "USA": [
            "Freedom isn't free, but my debt ceiling is infinite. 🇺🇸🦅 #Capitalism",
            "Hearing a lot of noise from countries without moon landings today.",
            "We don't invade, we 'liberate' distinct geological formations."
        ],
        "CHN": [
            "We deeply condemn this violation of sovereignty. Also, buy our EVs. 🇨🇳",
            "The West poses a threat to harmony. Harmony is mandatory.",
            "Historical precedent shows this land was ours since the Dinosaurs."
        ]
    }

    async def render(self, template_name: str, variables: Dict[str, Any]) -> str:
        """
        Render a prompt with few-shot examples injected.
        """
        template_str = self.TEMPLATES.get(template_name)
        if not template_str:
            raise ValueError(f"Template {template_name} not found")
        
        # 1. Inject Few-Shot Examples (The Fix)
        # Prevents "Personality Drift" by constantly grounding the LLM
        nation_id = variables.get('nation_id')
        if nation_id:
            examples = await self._get_golden_examples(nation_id)
            variables['golden_examples'] = "\n".join([f"- {e}" for e in examples])
        else:
            variables['golden_examples'] = "No specific examples available."

        # 2. Render Jinja2 Template
        try:
            template = Template(template_str)
            return template.render(**variables)
        except Exception as e:
            logger.error(f"Prompt rendering failed: {e}")
            raise

    async def _get_golden_examples(self, nation_id: str) -> List[str]:
        """
        Fetch golden examples for fs-prompting.
        """
        # In prod: return session.query(GoldenExample).filter_by(nation=nation_id).limit(5)
        return self.GOLDEN_EXAMPLES.get(nation_id, ["(No examples found)"])
