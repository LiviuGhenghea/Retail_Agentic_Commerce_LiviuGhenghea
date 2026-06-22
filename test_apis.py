#!/usr/bin/env python3
"""
Smoke-test all API wrappers against the beta environment.
No ANTHROPIC_API_KEY needed — only tests the Petolo REST APIs.

Usage:  python test_apis.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from k9_agent import api, tools

PASS = "\033[32m✓\033[0m"
FAIL = "\033[31m✗\033[0m"

results = []


def check(label: str, fn):
    try:
        result = fn()
        print(f"{PASS} {label}: {result}")
        results.append((label, True))
    except Exception as e:
        print(f"{FAIL} {label}: {e}")
        results.append((label, False))


print("\n=== K9 Agent — API Smoke Tests ===\n")

check("breeds search (Golden)", lambda: api.search_breeds("Golden")[0]["name"])
check("breeds search (Lab)", lambda: api.search_breeds("Lab")[0]["name"])

breed_id = api.search_breeds("Golden")[0]["id"]
check("get_breed by id", lambda: api.get_breed(breed_id)["name"])

check("policies list (dog)", lambda: f"{len(api.get_policies())} plans")

check("price vollschutz komfort", lambda: f"€{api.get_price(breed_id, 14, '2022-01-01')}/mo")
check("price vollschutz premium", lambda: f"€{api.get_price(breed_id, 15, '2022-01-01')}/mo")
check("price vollschutz premium+", lambda: f"€{api.get_price(breed_id, 16, '2022-01-01')}/mo")
check("price op-schutz komfort", lambda: f"€{api.get_price(breed_id, 17, '2022-01-01')}/mo")

check("start dates", lambda: api.get_start_dates()[0])

# Lead lifecycle
import json

print("\n--- Lead lifecycle ---")
lead = None

def create():
    global lead
    lead = api.create_lead({
        "customer": {
            "first_name": "Test",
            "last_name": "Agent",
            "email": "test.k9agent@example.com",
            "sign_up_source": "da_direkt",
        }
    })
    return f"UUID={lead['uuid']}"

check("create lead", create)

def update():
    return api.update_lead(lead["uuid"], {"customer": {"city": "Berlin"}})["uuid"]

check("update lead", update)

def get():
    return api.get_lead(lead["uuid"])["uuid"]

check("get lead", get)

def recurring():
    return api.check_recurring_lead(lead["uuid"], "test.k9agent@example.com", "+4917600000000")

check("check recurring", recurring)

# Tool dispatcher
print("\n--- Tool dispatcher ---")
check("tool: search_breeds", lambda: json.loads(tools.run_tool("search_breeds", {"name": "Beagle"})))
check("tool: get_all_plans", lambda: len(json.loads(tools.run_tool("get_all_plans", {}))["plans"]))
check("tool: get_all_prices", lambda: json.loads(tools.run_tool("get_all_prices", {"breed_id": breed_id, "date_of_birth": "2022-01-01"}))["prices"][0])
check("tool: get_coverage_faq", lambda: tools.run_tool("get_coverage_faq", {"topic": "waiting_period"})[:60])
check("tool: get_plan_details", lambda: tools.run_tool("get_plan_details", {"policy_category": 15})[:60])

print()
passed = sum(1 for _, ok in results if ok)
total = len(results)
status = "\033[32mPASS\033[0m" if passed == total else "\033[31mFAIL\033[0m"
print(f"Results: {passed}/{total} {status}")
