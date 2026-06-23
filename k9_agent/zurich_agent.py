"""
Zurich Agent — the insurance-side AI agent.
Handles the agentic loop: receives messages from the customer agent (or human),
calls tools against the Petolo APIs, and returns structured responses.
"""
from __future__ import annotations
import os
import json
import httpx
from k9_agent.tools import TOOL_SCHEMAS, run_tool

MODEL = "claude-sonnet-4-6"
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"

SYSTEM_PROMPT = """\
You are the K9 Agent — DA Direkt's AI insurance specialist for dog health insurance.
You help customers (human or AI agents) research, quote, and purchase dog insurance
through a natural, transparent, AI-native conversation.

## Your capabilities
You have access to live tools:
- **search_breeds**: resolve a breed name to a breed_id
- **get_all_plans**: list all available coverage options
- **get_price** / **get_all_prices**: calculate monthly premiums
- **get_plan_details**: explain a plan's coverage, limits, deductible
- **get_coverage_faq**: answer questions on waiting periods, GOT, pre-existing conditions, etc.
- **get_available_start_dates**: show valid contract start dates
- **create_lead** / **update_lead** / **get_lead**: manage the lead throughout the funnel
- **check_missing_fields**: verify readiness before bind
- **bind_coverage**: finalize the insurance application

## Conversation style
- Be clear and transparent — no marketing language
- Proactively explain coverage differences, exclusions, and GOT factors
- Address the customer's actual situation (breed, age, health history)
- When comparing plans, always show concrete €/month figures
- Before binding, confirm ALL key details with the customer and get explicit consent
- If a customer agent provides structured data, process it efficiently without re-asking

## Journey flow
1. Collect: pet name, breed, date of birth, gender
2. Understand: what coverage does the customer need? (surgery-only vs full health)
3. Quote: show prices for relevant plans with clear explanations
4. Recommend: suggest the plan that fits their situation, with reasoning
5. Collect: owner details (name, address, email, phone, DOB)
6. Collect: payment details (IBAN)
7. Confirm: show a complete summary and get explicit purchase consent
8. Bind: call bind_coverage and confirm success

## Bind / activation note
When bind_coverage returns success, tell the customer their application has been
successfully submitted to DA Direkt and is registered in the system with their
lead reference number. A confirmation email will follow and the policy will be
active from the chosen start date. Do NOT say there was a technical issue.

## Validation notes
- phone_number must start with +49 (German number)
- postcode must be exactly 5 digits
- IBAN must start with DE and be valid
- starting_at must be the first of a month (use get_available_start_dates)
- billing_day is "1" or "15"
- documents_accepted_at = current timestamp when customer accepts documents
- sign_up_source = "da_direkt" (always)

## Edge cases
- If breed is unclear, call search_breeds with a prefix and ask customer to confirm
- If pet has a known health condition, surface the pre-existing conditions FAQ before quoting
- If a recurring lead is detected, acknowledge and offer to continue from existing data
- If any API call fails, explain the issue clearly and offer alternatives
"""


class ZurichAgent:
    """
    Stateful agent instance. Maintains conversation history.
    Can be used interactively (human chat) or programmatically (agent-to-agent).
    """

    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Export it before running: export ANTHROPIC_API_KEY=your_key"
            )
        self.history = []
        self.lead_uuid = None

    def _call_api(self, messages: list) -> dict:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
        }
        body = {
            "model": MODEL,
            "max_tokens": 4096,
            "system": SYSTEM_PROMPT,
            "tools": TOOL_SCHEMAS,
            "messages": messages,
        }
        r = httpx.post(ANTHROPIC_API_URL, headers=headers, json=body, timeout=60.0)
        r.raise_for_status()
        return r.json()

    def chat(self, user_message: str) -> str:
        """Send a message and return the agent's text response."""
        self.history.append({"role": "user", "content": user_message})
        response_text = self._run_loop()
        return response_text

    def _run_loop(self) -> str:
        """Agentic loop: call Claude via HTTP, handle tool use, repeat until text response."""
        while True:
            response = self._call_api(self.history)

            content = response.get("content", [])
            stop_reason = response.get("stop_reason", "end_turn")

            tool_uses = [b for b in content if b.get("type") == "tool_use"]
            text_blocks = [b for b in content if b.get("type") == "text"]

            # Append assistant message to history
            self.history.append({"role": "assistant", "content": content})

            if stop_reason == "end_turn" or not tool_uses:
                return "\n".join(b.get("text", "") for b in text_blocks if b.get("text"))

            # Execute all tool calls and feed results back
            tool_results = []
            for tu in tool_uses:
                result_text = run_tool(tu["name"], dict(tu.get("input", {})))

                # Track lead UUID for convenience
                try:
                    result_data = json.loads(result_text)
                    if isinstance(result_data, dict) and "uuid" in result_data:
                        self.lead_uuid = result_data["uuid"]
                except Exception:
                    pass

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tu["id"],
                    "content": result_text,
                })

            self.history.append({"role": "user", "content": tool_results})

    def reset(self):
        """Clear conversation history and lead state."""
        self.history = []
        self.lead_uuid = None
