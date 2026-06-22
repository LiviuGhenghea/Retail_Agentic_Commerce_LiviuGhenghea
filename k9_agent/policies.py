"""
Static knowledge about DA Direkt dog insurance plans.
Sourced from live /api/petolo/v1/policies and the AS-IS documentation.
"""

# Coverage type → human description
COVERAGE_TYPES = {
    "vollschutz": "Vollschutz (full health coverage): outpatient, inpatient, surgery, diagnostics, medication.",
    "op_schutz": "OP-Schutz (surgery-only coverage): covers operations and hospitalisation, not routine vet visits.",
}

# policy_category integer → (coverage_type, tier, display_name)
POLICY_MAP: dict[int, dict] = {
    14: {"coverage": "vollschutz", "tier": "komfort",      "name": "Vollschutz Komfort"},
    15: {"coverage": "vollschutz", "tier": "premium",      "name": "Vollschutz Premium"},
    16: {"coverage": "vollschutz", "tier": "premium_plus", "name": "Vollschutz Premium Plus"},
    17: {"coverage": "op_schutz",  "tier": "komfort",      "name": "OP-Schutz Komfort"},
    18: {"coverage": "op_schutz",  "tier": "premium",      "name": "OP-Schutz Premium"},
    19: {"coverage": "op_schutz",  "tier": "premium_plus", "name": "OP-Schutz Premium Plus"},
}

# Tier descriptions for customer-facing explanations
TIER_DESCRIPTIONS = {
    "komfort": (
        "Komfort — entry level. Annual limit ~3,000 €. "
        "80% reimbursement, 3× GOT fee scale, 250 € deductible."
    ),
    "premium": (
        "Premium — mid tier. Annual limit ~5,000 €. "
        "90% reimbursement, 3× GOT fee scale, 200 € deductible. "
        "Includes emergency clinic fees."
    ),
    "premium_plus": (
        "Premium Plus — top tier. Annual limit ~8,000 €. "
        "100% reimbursement up to limit, 4× GOT fee scale, 0 € deductible. "
        "Includes preventive care module and emergency clinic fees."
    ),
}

# Coverage comparison for the most common customer questions
COVERAGE_FAQ = {
    "waiting_period": (
        "General waiting period: 3 weeks from policy start. "
        "Accidents: covered immediately. "
        "Surgery under OP-Schutz: 3-week waiting period applies."
    ),
    "free_vet_choice": "Yes — you may use any licensed vet or clinic in Germany, including emergency services.",
    "got_explanation": (
        "GOT (Gebührenordnung für Tierärzte) is the German veterinary fee schedule. "
        "The multiplier (3× or 4×) is the maximum fee the insurer will reimburse. "
        "Most routine visits are billed at 1–2×; complex cases or clinics may go to 3–4×."
    ),
    "preexisting_conditions": (
        "Pre-existing conditions diagnosed or treated before the policy start date are generally excluded. "
        "Undisclosed conditions may also void the policy. "
        "If your dog has had a previous diagnosis, it is safest to disclose it during sign-up."
    ),
    "deductible": "The annual deductible is deducted once per policy year, not per claim.",
    "reimbursement": (
        "Submit your vet invoice via the DA Direkt app or customer portal. "
        "Reimbursement is typically processed within 5–10 business days."
    ),
}


def describe_plan(policy_category: int) -> str:
    """Return a plain-language description of a plan."""
    meta = POLICY_MAP.get(policy_category)
    if not meta:
        return f"Unknown policy category {policy_category}."
    coverage_desc = COVERAGE_TYPES[meta["coverage"]]
    tier_desc = TIER_DESCRIPTIONS[meta["tier"]]
    return f"**{meta['name']}**\n{coverage_desc}\n{tier_desc}"


def plans_for_coverage(coverage_type: str) -> list[int]:
    """Return sorted list of policy_category IDs for 'vollschutz' or 'op_schutz'."""
    return sorted(k for k, v in POLICY_MAP.items() if v["coverage"] == coverage_type)


def all_dog_categories() -> list[int]:
    return sorted(POLICY_MAP.keys())
