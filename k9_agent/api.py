"""
Thin wrapper around the Petolo/Faircare beta REST APIs.
All methods raise RuntimeError on HTTP or API-level errors.
"""
from __future__ import annotations
from typing import Optional
import httpx

BASE = "https://beta.dentolo-test.de"
API_KEY = "7604c1e4-1248-4eb5-98ca-1b2afea54afe"
HEADERS = {
    "x-api-key": API_KEY,
    "x-getolo-locale": "de",
    "Content-Type": "application/json",
    "Accept": "*/*",
}
TIMEOUT = 15.0


def _get(path: str, params: Optional[dict] = None) -> object:
    url = f"{BASE}{path}"
    r = httpx.get(url, headers=HEADERS, params=params, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def _post(path: str, body: dict) -> dict:
    url = f"{BASE}{path}"
    r = httpx.post(url, headers=HEADERS, json=body, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def _put(path: str, body: dict) -> dict:
    url = f"{BASE}{path}"
    r = httpx.put(url, headers=HEADERS, json=body, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


# ── Breeds ───────────────────────────────────────────────────────────────────

def search_breeds(name: str, pet_type: str = "dog") -> list[dict]:
    """Return breeds whose name starts with `name` (case-insensitive search)."""
    data = _get("/api/petolo/v1/breeds", {"pet_type": pet_type, "search": name})
    return data if isinstance(data, list) else []


def get_breed(breed_id: int) -> dict:
    data = _get(f"/api/petolo/v1/breeds/{breed_id}")
    return data.get("breed", data)


# ── Policies ─────────────────────────────────────────────────────────────────

def get_policies() -> list[dict]:
    """Return all dog insurance policies from the beta catalogue."""
    data = _get("/api/petolo/v1/policies", {"combined": "true"})
    return [p for p in data if "Hund" in p.get("name", "")]


# ── Price ─────────────────────────────────────────────────────────────────────

def get_price(breed_id: int, policy_category: int, date_of_birth: str) -> float:
    """Return monthly premium (€) for the given parameters."""
    data = _get(
        "/api/petolo/v1/price",
        {
            "breed_id": breed_id,
            "policy_category": policy_category,
            "date_of_birth": date_of_birth,
        },
    )
    price = data.get("policy_price")
    if price is None:
        raise RuntimeError("Price API returned no price — check breed/DOB/category.")
    return float(price)


# ── Contract start dates ──────────────────────────────────────────────────────

def get_start_dates() -> list[str]:
    data = _get("/api/v1/contracts/available_start_dates")
    return data.get("available_start_dates", [])


# ── Leads ─────────────────────────────────────────────────────────────────────

def create_lead(payload: dict) -> dict:
    resp = _post("/api/petolo/v1/leads", payload)
    if resp.get("status") == "fail":
        raise RuntimeError(f"Lead creation failed: {resp.get('errors')}")
    return resp["lead"]


def update_lead(uuid: str, payload: dict) -> dict:
    resp = _put(f"/api/petolo/v1/leads/{uuid}", payload)
    if resp.get("status") == "fail":
        raise RuntimeError(f"Lead update failed: {resp.get('errors')}")
    return resp["lead"]


def get_lead(uuid: str) -> dict:
    resp = _get(f"/api/petolo/v1/leads/{uuid}")
    return resp.get("lead", resp)


def check_recurring_lead(uuid: str, email: str, phone_number: str) -> bool:
    resp = _post(
        "/api/petolo/v1/leads/check_recurring_lead",
        {"lead_data": {"uuid": uuid, "customer": {"email": email, "phone_number": phone_number}}},
    )
    return bool(resp.get("recurring", False))


# ── Convert lead → customer (bind) ───────────────────────────────────────────

def bind_coverage(uuid: str) -> dict:
    """Convert a fully-populated lead into an insurance customer."""
    resp = _post("/api/petolo/v1/customers", {"uuid": uuid})
    if resp.get("status") == "fail":
        raise RuntimeError(f"Bind failed: {resp.get('errors')}")
    return resp
