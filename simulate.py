#!/usr/bin/env python3
"""
Agent-to-agent simulation: CustomerAgent ↔ ZurichAgent.
Runs a full quote-and-bind journey end-to-end.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python simulate.py [--dry-run]

  --dry-run: stops before calling bind_coverage (safe for demos)
"""
import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(__file__))
from k9_agent.zurich_agent import ZurichAgent
from k9_agent.customer_agent import CustomerAgent

# ── Synthetic owner profile ───────────────────────────────────────────────────
DEMO_OWNER = {
    "owner": {
        "first_name": "Emma",
        "last_name": "Schneider",
        "gender": "female",
        "date_of_birth": "1988-04-15",
        "email": "emma.schneider.k9demo@example.com",
        "phone_number": "+4917612345678",
        "street_name": "Kastanienallee",
        "house_number": "42",
        "postcode": "10435",
        "city": "Berlin",
        "iban": "DE89370400440532013000",
    },
    "dog": {
        "name": "Luna",
        "breed": "Golden Retriever",
        "date_of_birth": "2022-03-10",
        "gender": "female",
        "notes": "Healthy, no known pre-existing conditions. Owner prefers full coverage.",
    },
    "preferences": {
        "max_monthly_budget_eur": 70,
        "coverage_preference": "full health, not surgery-only",
        "priority": "good reimbursement rate and free vet choice",
    },
}

MAX_TURNS = 12


def separator(label: str):
    print(f"\n{'─' * 60}")
    print(f"  {label}")
    print('─' * 60)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Stop before binding coverage")
    args = parser.parse_args()

    try:
        zurich = ZurichAgent()
        customer = CustomerAgent(DEMO_OWNER)
    except EnvironmentError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    separator("Agent-to-Agent Simulation: K9 Insurance Journey")
    print(f"Customer: {DEMO_OWNER['owner']['first_name']} {DEMO_OWNER['owner']['last_name']}")
    print(f"Dog:      {DEMO_OWNER['dog']['name']} ({DEMO_OWNER['dog']['breed']}, born {DEMO_OWNER['dog']['date_of_birth']})")
    print(f"Mode:     {'DRY RUN (no bind)' if args.dry_run else 'FULL (will bind)'}")

    # First customer message
    customer_msg = customer.opening_message()

    for turn in range(1, MAX_TURNS + 1):
        separator(f"Turn {turn}")
        print(f"\n[CUSTOMER AGENT]\n{customer_msg}\n")

        # Zurich agent processes
        zurich_response = zurich.chat(customer_msg)
        print(f"[ZURICH K9 AGENT]\n{zurich_response}\n")

        # Check if journey is complete
        done_phrases = [
            "coverage bound", "application created", "insurance application",
            "successfully bound", "policy is now active",
        ]
        if any(p in zurich_response.lower() for p in done_phrases):
            separator("Journey Complete")
            print(f"Lead UUID: {zurich.lead_uuid}")
            print("Insurance application successfully created.")
            break

        # Dry-run gate: stop before bind
        bind_phrases = ["bind_coverage", "convert", "finalize", "purchase is confirmed"]
        if args.dry_run and any(p in zurich_response.lower() for p in bind_phrases):
            separator("Dry Run — stopping before bind")
            print(f"Lead UUID: {zurich.lead_uuid}")
            print("All data collected. Would call bind_coverage in a real run.")
            break

        # Customer agent decides next message
        customer_msg = customer.decide_next_message(zurich_response)

    else:
        separator("Max turns reached")
        print(f"Lead UUID: {zurich.lead_uuid}")


if __name__ == "__main__":
    main()
