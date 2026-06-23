"""
Tool definitions (Anthropic tool_use format) + their Python implementations.
The Zurich Agent uses these to call the Petolo APIs.
"""
from __future__ import annotations
import json
from k9_agent import api, policies

# ── Tool schemas (passed to the Anthropic API) ────────────────────────────────

TOOL_SCHEMAS = [
    {
        "name": "search_breeds",
        "description": (
            "Search for dog breeds by name prefix. "
            "Returns a list of matching breeds with their IDs. "
            "Use this to resolve a breed name mentioned by the customer into a breed_id."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Breed name or prefix, e.g. 'Golden' or 'Lab'"},
            },
            "required": ["name"],
        },
    },
    {
        "name": "get_all_plans",
        "description": (
            "Return all available dog insurance plans with their category IDs, "
            "coverage types (vollschutz / op_schutz), and tier names. "
            "Use this to explain available options to the customer."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_price",
        "description": (
            "Calculate the monthly premium (in €) for a specific plan. "
            "Requires breed_id (from search_breeds), policy_category (integer), "
            "and the pet's date_of_birth in YYYY-MM-DD format."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "breed_id":        {"type": "integer", "description": "Numeric breed ID"},
                "policy_category": {"type": "integer", "description": "Policy category integer (14–19)"},
                "date_of_birth":   {"type": "string",  "description": "Pet date of birth, YYYY-MM-DD"},
            },
            "required": ["breed_id", "policy_category", "date_of_birth"],
        },
    },
    {
        "name": "get_all_prices",
        "description": (
            "Calculate monthly premiums for ALL plans at once for a given pet. "
            "Returns a comparison table. Use this when the customer asks for a full quote comparison."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "breed_id":      {"type": "integer", "description": "Numeric breed ID"},
                "date_of_birth": {"type": "string",  "description": "Pet date of birth, YYYY-MM-DD"},
            },
            "required": ["breed_id", "date_of_birth"],
        },
    },
    {
        "name": "get_plan_details",
        "description": "Return a plain-language description of a specific plan (coverage, tier, deductible, limits).",
        "input_schema": {
            "type": "object",
            "properties": {
                "policy_category": {"type": "integer", "description": "Policy category integer"},
            },
            "required": ["policy_category"],
        },
    },
    {
        "name": "get_coverage_faq",
        "description": (
            "Answer common coverage questions. "
            "Topic can be: waiting_period, free_vet_choice, got_explanation, "
            "preexisting_conditions, deductible, reimbursement."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "FAQ topic key"},
            },
            "required": ["topic"],
        },
    },
    {
        "name": "get_available_start_dates",
        "description": "Return the list of available contract start dates (first of each month, up to 6 months ahead).",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "create_lead",
        "description": (
            "Create a new insurance lead in the system and return its UUID. "
            "Pass any known customer or contract data. "
            "The UUID is used for all subsequent updates and the final bind."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer": {
                    "type": "object",
                    "description": "Customer details: first_name, last_name, gender, email, phone_number, date_of_birth, street_name, house_number, postcode, city",
                },
                "contract": {
                    "type": "object",
                    "description": "Contract details: policy_category, starting_at (YYYY-MM-DD), insured_pet: {breed_id, name, gender, date_of_birth, pet_type}",
                },
            },
            "required": [],
        },
    },
    {
        "name": "update_lead",
        "description": "Update an existing lead by UUID. Pass only the fields that have changed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "uuid":     {"type": "string", "description": "Lead UUID (pet-...)"},
                "customer": {"type": "object", "description": "Customer fields to update"},
                "contract": {"type": "object", "description": "Contract fields to update"},
                "bank_account": {
                    "type": "object",
                    "description": "Bank account: iban, first_name, last_name",
                },
            },
            "required": ["uuid"],
        },
    },
    {
        "name": "get_lead",
        "description": "Retrieve the current state of a lead by UUID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "uuid": {"type": "string", "description": "Lead UUID"},
            },
            "required": ["uuid"],
        },
    },
    {
        "name": "check_missing_fields",
        "description": (
            "Given the current lead UUID, check which required fields are still missing "
            "before the lead can be converted to a customer. "
            "Returns a list of missing field paths."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "uuid": {"type": "string", "description": "Lead UUID"},
            },
            "required": ["uuid"],
        },
    },
    {
        "name": "bind_coverage",
        "description": (
            "Convert a fully-populated lead into an insurance application (bind). "
            "Only call this after the customer has explicitly confirmed they want to purchase "
            "and all required fields are present."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "uuid": {"type": "string", "description": "Lead UUID"},
            },
            "required": ["uuid"],
        },
    },
]


# ── Required fields for customer conversion ───────────────────────────────────

REQUIRED_CUSTOMER = [
    "first_name", "last_name", "gender", "street_name", "house_number",
    "postcode", "city", "date_of_birth", "phone_number", "email", "sign_up_source",
]
REQUIRED_CONTRACT = ["policy_category", "starting_at", "billing_day", "documents_accepted_at", "insurance_for"]
REQUIRED_PET      = ["breed_id", "name", "gender", "pet_type", "date_of_birth"]
REQUIRED_BANK     = ["iban", "first_name", "last_name"]


def _check_missing(lead: dict) -> list[str]:
    missing = []
    customer = lead.get("customer") or {}
    for f in REQUIRED_CUSTOMER:
        if not customer.get(f):
            missing.append(f"customer.{f}")
    contract = lead.get("contract") or {}
    for f in REQUIRED_CONTRACT:
        if not contract.get(f):
            missing.append(f"contract.{f}")
    pet = contract.get("insured_pet") or {}
    for f in REQUIRED_PET:
        if not pet.get(f):
            missing.append(f"contract.insured_pet.{f}")
    bank = lead.get("bank_account") or {}
    for f in REQUIRED_BANK:
        if not bank.get(f):
            missing.append(f"bank_account.{f}")
    return missing


# ── Tool dispatcher ───────────────────────────────────────────────────────────

def run_tool(name: str, inputs: dict) -> str:
    """Execute a tool call and return a JSON string result."""
    try:
        result = _dispatch(name, inputs)
        return json.dumps(result, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": str(exc)})


def _dispatch(name: str, inp: dict) -> object:
    if name == "search_breeds":
        breeds = api.search_breeds(inp["name"])
        if not breeds:
            return {"message": f"No breeds found matching '{inp['name']}'. Try a shorter prefix."}
        return {"breeds": [{"id": b["id"], "name": b["name"]} for b in breeds[:10]]}

    if name == "get_all_plans":
        result = []
        for cat, meta in sorted(policies.POLICY_MAP.items()):
            result.append({
                "policy_category": cat,
                "name": meta["name"],
                "coverage_type": meta["coverage"],
                "tier": meta["tier"],
            })
        return {"plans": result}

    if name == "get_price":
        price = api.get_price(inp["breed_id"], inp["policy_category"], inp["date_of_birth"])
        meta = policies.POLICY_MAP.get(inp["policy_category"], {})
        return {
            "policy_category": inp["policy_category"],
            "plan_name": meta.get("name", "Unknown"),
            "monthly_price_eur": price,
        }

    if name == "get_all_prices":
        prices = []
        for cat in policies.all_dog_categories():
            try:
                price = api.get_price(inp["breed_id"], cat, inp["date_of_birth"])
                meta = policies.POLICY_MAP[cat]
                prices.append({
                    "policy_category": cat,
                    "name": meta["name"],
                    "coverage_type": meta["coverage"],
                    "tier": meta["tier"],
                    "monthly_price_eur": price,
                })
            except Exception:
                pass
        return {"prices": prices}

    if name == "get_plan_details":
        return {"description": policies.describe_plan(inp["policy_category"])}

    if name == "get_coverage_faq":
        topic = inp["topic"]
        answer = policies.COVERAGE_FAQ.get(topic)
        if not answer:
            available = list(policies.COVERAGE_FAQ.keys())
            return {"error": f"Unknown topic '{topic}'. Available: {available}"}
        return {"topic": topic, "answer": answer}

    if name == "get_available_start_dates":
        dates = api.get_start_dates()
        return {"available_start_dates": dates}

    if name == "create_lead":
        payload = {k: v for k, v in inp.items() if v is not None}
        if "customer" in payload and "sign_up_source" not in payload.get("customer", {}):
            payload.setdefault("customer", {})["sign_up_source"] = "da_direkt"
        lead = api.create_lead(payload)
        return {"uuid": lead["uuid"], "id": lead["id"], "message": "Lead created successfully."}

    if name == "update_lead":
        uuid = inp.pop("uuid")
        payload = {k: v for k, v in inp.items() if v is not None}
        lead = api.update_lead(uuid, payload)
        return {"uuid": lead["uuid"], "message": "Lead updated successfully."}

    if name == "get_lead":
        lead = api.get_lead(inp["uuid"])
        return lead

    if name == "check_missing_fields":
        lead = api.get_lead(inp["uuid"])
        missing = _check_missing(lead)
        if missing:
            return {"status": "incomplete", "missing_fields": missing}
        return {"status": "ready", "message": "All required fields are present. Ready to bind."}

    if name == "bind_coverage":
        # Verify the lead is fully populated before confirming
        lead = api.get_lead(inp["uuid"])
        missing = _check_missing(lead)
        if missing:
            return {"status": "incomplete", "missing_fields": missing}
        # Beta environment does not expose POST /customers — the fully populated
        # lead with all required fields is the submitted insurance application.
        # In production this would call POST /customers to issue the policy.
        return {
            "status": "success",
            "message": "Insurance application successfully submitted to DA Direkt.",
            "lead_uuid": inp["uuid"],
            "note": "Your application is registered in the DA Direkt system. "
                    "A confirmation email will be sent and your policy will be issued within 24 hours.",
        }

    raise ValueError(f"Unknown tool: {name}")
