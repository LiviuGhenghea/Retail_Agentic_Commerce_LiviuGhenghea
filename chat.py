#!/usr/bin/env python3
"""
Interactive human ↔ Zurich Agent chat.
Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python chat.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from k9_agent.zurich_agent import ZurichAgent


def main():
    print("=" * 60)
    print("  K9 Agent — DA Direkt Dog Insurance")
    print("  Type 'quit' or Ctrl-C to exit, 'reset' to start over")
    print("=" * 60)
    print()

    try:
        agent = ZurichAgent()
    except EnvironmentError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    # Opening greeting
    greeting = agent.chat("Hello, I'm looking for dog health insurance.")
    print(f"K9 Agent: {greeting}\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        if user_input.lower() == "reset":
            agent.reset()
            print("Conversation reset.\n")
            greeting = agent.chat("Hello, I'm looking for dog health insurance.")
            print(f"K9 Agent: {greeting}\n")
            continue

        print()
        response = agent.chat(user_input)
        print(f"K9 Agent: {response}\n")


if __name__ == "__main__":
    main()
