"""
Customer Agent — acts on behalf of a dog owner.
Drives the quote-and-bind journey by interacting with the Zurich Agent.
Used for hackathon demos, automated testing, and agent-to-agent simulation.
"""
from __future__ import annotations
import os
import httpx
import json as _json

MODEL = "claude-haiku-4-5-20251001"
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"

SYSTEM_PROMPT = """\
You are a personal AI agent acting on behalf of a dog owner who wants to get pet insurance.
You interact with the Zurich K9 Agent (an insurance specialist AI) to research, get quotes,
and purchase a suitable policy on behalf of your owner.

## Your owner's profile
{owner_profile}

## Your mission
Work through the full insurance journey:
1. Introduce yourself and your owner's dog
2. Ask about available plans and get a full price comparison
3. Ask clarifying questions about coverage differences relevant to the dog
4. Select the plan that best fits your owner's needs and budget
5. Provide all required owner and dog details to complete the application
6. Confirm the summary and explicitly consent to purchase
7. Confirm successful binding

## Style
- Be concise and direct — you are an AI agent, not a human
- Pass structured data efficiently (you can send JSON-formatted details)
- Push for transparency: ask about exclusions, waiting periods, and pre-existing conditions
- Confirm consent explicitly with phrases like "I confirm on behalf of [owner] that..."

## Constraints
- Only provide the details in your owner profile — do not invent data
- If asked for information not in the profile, say it is not available
- Do not accept a policy without understanding what it covers and excludes
"""


class CustomerAgent:
    """
    Personal agent that acts on behalf of a dog owner.
    Communicates with ZurichAgent to complete the quote-and-bind journey.
    """

    def __init__(self, owner_profile: dict):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise EnvironmentError("ANTHROPIC_API_KEY environment variable is not set.")
        self.owner_profile = owner_profile
        self.history = []

    def _system(self) -> str:
        profile_str = _json.dumps(self.owner_profile, indent=2, ensure_ascii=False)
        return SYSTEM_PROMPT.format(owner_profile=profile_str)

    def _call_api(self, messages: list) -> str:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
        }
        body = {
            "model": MODEL,
            "max_tokens": 1024,
            "system": self._system(),
            "messages": messages,
        }
        r = httpx.post(ANTHROPIC_API_URL, headers=headers, json=body, timeout=60.0)
        r.raise_for_status()
        content = r.json().get("content", [])
        return next((b["text"] for b in content if b.get("type") == "text"), "")

    def decide_next_message(self, zurich_response: str) -> str:
        self.history.append({"role": "user", "content": f"[Zurich K9 Agent]: {zurich_response}"})
        reply = self._call_api(self.history)
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def opening_message(self) -> str:
        """Generate the first message to send to the Zurich Agent."""
        dog = self.owner_profile.get("dog", {})
        owner = self.owner_profile.get("owner", {})
        return (
            f"Hello, I am a personal AI agent acting on behalf of {owner.get('first_name', 'my owner')} "
            f"{owner.get('last_name', '')}. I am looking for dog health insurance for their "
            f"{dog.get('breed', 'dog')} named {dog.get('name', 'their dog')}, "
            f"born {dog.get('date_of_birth', 'unknown DOB')}. "
            "Please help me find the best coverage. Start by showing me all available plans and prices."
        )
