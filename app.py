"""
K9 Agent — DA Direkt Dog Insurance
Streamlit chat UI with scripted Zurich Agent flow + live Petolo API calls.

Run with:  streamlit run app.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from k9_agent import api, policies
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="K9 Agent — DA Direkt",
    page_icon="🐾",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #f5f7fa; }
    .main-header {
        background: linear-gradient(135deg, #003882 0%, #0057b8 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .main-header h1 { color: white; margin: 0; font-size: 1.8rem; }
    .main-header p  { color: #cce0ff; margin: 0.3rem 0 0 0; font-size: 0.95rem; }
    .plan-card {
        background: white;
        border: 1px solid #e0e8f0;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
    }
    .plan-card.recommended {
        border: 2px solid #0057b8;
        background: #f0f6ff;
    }
    .price-tag {
        font-size: 1.4rem;
        font-weight: 700;
        color: #0057b8;
    }
    .badge {
        display: inline-block;
        background: #0057b8;
        color: white;
        font-size: 0.7rem;
        padding: 2px 8px;
        border-radius: 20px;
        margin-left: 8px;
        vertical-align: middle;
    }
    .step-indicator {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    .stChatMessage { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🐾 K9 Agent</h1>
    <p>DA Direkt · AI-native Dog Insurance · Research, Quote & Bind</p>
</div>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "messages": [],           # chat history
        "step": "welcome",        # current journey step
        "dog": {},                # collected dog info
        "owner": {},              # collected owner info
        "bank": {},               # bank info
        "breed_id": None,
        "breed_name": None,
        "prices": None,           # fetched prices dict
        "selected_category": None,
        "lead_uuid": None,
        "start_dates": None,
        "selected_start_date": None,
        "awaiting_input": None,   # what we're waiting for from the user
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Helper to add messages ────────────────────────────────────────────────────
def agent_msg(text: str):
    st.session_state.messages.append({"role": "assistant", "content": text})

def user_msg(text: str):
    st.session_state.messages.append({"role": "user", "content": text})

# ── Journey steps ─────────────────────────────────────────────────────────────

STEPS = ["Welcome", "Dog Info", "Quote", "Plan", "Owner", "Payment", "Confirm", "Done"]

def step_index():
    step_map = {
        "welcome": 0, "dog_name": 1, "dog_breed": 1, "dog_dob": 1,
        "dog_gender": 1, "quoting": 2, "select_plan": 3,
        "owner_name": 4, "owner_email": 4, "owner_phone": 4,
        "owner_address": 4, "owner_dob": 4,
        "payment": 5, "confirm": 6, "done": 7,
    }
    return step_map.get(st.session_state.step, 0)

# Progress bar
progress = step_index() / (len(STEPS) - 1)
st.progress(progress)
cols = st.columns(len(STEPS))
for i, (col, label) in enumerate(zip(cols, STEPS)):
    idx = step_index()
    if i < idx:
        col.markdown(f"<div style='text-align:center;font-size:0.65rem;color:#0057b8;'>✓ {label}</div>", unsafe_allow_html=True)
    elif i == idx:
        col.markdown(f"<div style='text-align:center;font-size:0.65rem;font-weight:700;color:#0057b8;'>{label}</div>", unsafe_allow_html=True)
    else:
        col.markdown(f"<div style='text-align:center;font-size:0.65rem;color:#aaa;'>{label}</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Render chat history ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🐾" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# ── Welcome ───────────────────────────────────────────────────────────────────
if st.session_state.step == "welcome":
    agent_msg(
        "👋 **Hello! I'm the K9 Agent**, DA Direkt's AI insurance specialist.\n\n"
        "I'll help you find the best dog health insurance in just a few steps — "
        "with live pricing, clear explanations, and no hidden surprises.\n\n"
        "**Let's start with your dog. What's their name?**"
    )
    st.session_state.step = "dog_name"
    st.rerun()

# ── Chat input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Type your message here...")

if user_input:
    user_msg(user_input)
    step = st.session_state.step

    # ── Dog name ──────────────────────────────────────────────────────────────
    if step == "dog_name":
        st.session_state.dog["name"] = user_input.strip().title()
        agent_msg(
            f"Great name! **{st.session_state.dog['name']}** sounds like a wonderful dog. 🐕\n\n"
            f"What **breed** is {st.session_state.dog['name']}? "
            "(e.g. Golden Retriever, Labrador, German Shepherd)"
        )
        st.session_state.step = "dog_breed"

    # ── Dog breed ─────────────────────────────────────────────────────────────
    elif step == "dog_breed":
        search_term = user_input.strip()
        with st.spinner("Looking up breed..."):
            breeds = api.search_breeds(search_term)
        if not breeds:
            agent_msg(
                f"I couldn't find a breed matching **\"{search_term}\"**. "
                "Could you try a shorter name or different spelling? (e.g. 'Golden', 'Lab', 'Shepherd')"
            )
        elif len(breeds) == 1:
            b = breeds[0]
            st.session_state.breed_id = b["id"]
            st.session_state.breed_name = b["name"]
            agent_msg(
                f"Found it: **{b['name']}**. ✅\n\n"
                f"When was {st.session_state.dog['name']} born? "
                "Please enter the date in **YYYY-MM-DD** format (e.g. 2022-03-15)"
            )
            st.session_state.step = "dog_dob"
        else:
            options = "\n".join(f"- {b['name']}" for b in breeds[:6])
            agent_msg(
                f"I found a few breeds matching that. Which one is correct?\n\n{options}\n\n"
                "Please type the exact breed name."
            )

    # ── Dog DOB ───────────────────────────────────────────────────────────────
    elif step == "dog_dob":
        dob = user_input.strip()
        try:
            datetime.strptime(dob, "%Y-%m-%d")
            st.session_state.dog["date_of_birth"] = dob
            agent_msg(
                f"Got it — born **{dob}**.\n\n"
                f"Is {st.session_state.dog['name']} **male** or **female**?"
            )
            st.session_state.step = "dog_gender"
        except ValueError:
            agent_msg(
                "Please enter the date in **YYYY-MM-DD** format, for example: `2022-03-15`"
            )

    # ── Dog gender ────────────────────────────────────────────────────────────
    elif step == "dog_gender":
        g = user_input.strip().lower()
        if g in ("male", "female", "m", "f", "männlich", "weiblich"):
            gender = "male" if g in ("male", "m", "männlich") else "female"
            st.session_state.dog["gender"] = gender
            st.session_state.step = "quoting"
            agent_msg(
                f"Perfect. Let me now calculate live prices for **{st.session_state.dog['name']}** "
                f"({st.session_state.breed_name}, {st.session_state.dog['date_of_birth']}, {gender})...\n\n"
                "⏳ Fetching quotes from DA Direkt..."
            )
            st.rerun()
        else:
            agent_msg("Please answer **male** or **female**.")

    # ── Owner name ────────────────────────────────────────────────────────────
    elif step == "owner_name":
        parts = user_input.strip().split()
        if len(parts) >= 2:
            st.session_state.owner["first_name"] = parts[0]
            st.session_state.owner["last_name"] = " ".join(parts[1:])
            agent_msg(
                f"Nice to meet you, **{st.session_state.owner['first_name']}**! 👋\n\n"
                "What is your **email address**?"
            )
            st.session_state.step = "owner_email"
        else:
            agent_msg("Please enter your **full name** (first name and last name).")

    # ── Owner email ───────────────────────────────────────────────────────────
    elif step == "owner_email":
        email = user_input.strip()
        if "@" in email and "." in email.split("@")[-1]:
            st.session_state.owner["email"] = email
            agent_msg(
                "Thanks! What is your **German mobile number**?\n\n"
                "Format: **+49** followed by the number (e.g. +4917612345678)"
            )
            st.session_state.step = "owner_phone"
        else:
            agent_msg("That doesn't look like a valid email. Please try again.")

    # ── Owner phone ───────────────────────────────────────────────────────────
    elif step == "owner_phone":
        phone = user_input.strip().replace(" ", "")
        if phone.startswith("+49") and len(phone) >= 12:
            st.session_state.owner["phone_number"] = phone
            agent_msg(
                "Got it. What is your **date of birth**?\n\n"
                "Format: **YYYY-MM-DD** (e.g. 1988-04-15)"
            )
            st.session_state.step = "owner_dob"
        else:
            agent_msg(
                "The phone number must start with **+49** and be a valid German number.\n"
                "Example: +4917612345678"
            )

    # ── Owner DOB ─────────────────────────────────────────────────────────────
    elif step == "owner_dob":
        dob = user_input.strip()
        try:
            datetime.strptime(dob, "%Y-%m-%d")
            st.session_state.owner["date_of_birth"] = dob
            agent_msg(
                "Almost there! What is your **home address**?\n\n"
                "Please provide it in this format:\n"
                "`Street Name, House Number, Postcode, City`\n\n"
                "Example: `Kastanienallee, 42, 10435, Berlin`"
            )
            st.session_state.step = "owner_address"
        except ValueError:
            agent_msg("Please use **YYYY-MM-DD** format, e.g. `1988-04-15`")

    # ── Owner address ─────────────────────────────────────────────────────────
    elif step == "owner_address":
        parts = [p.strip() for p in user_input.split(",")]
        if len(parts) >= 4:
            st.session_state.owner["street_name"]  = parts[0]
            st.session_state.owner["house_number"] = parts[1]
            st.session_state.owner["postcode"]     = parts[2]
            st.session_state.owner["city"]         = parts[3]
            agent_msg(
                f"✅ Address saved: **{parts[0]} {parts[1]}, {parts[2]} {parts[3]}**\n\n"
                "Now for payment. Please enter your **German IBAN**:\n\n"
                "Format: **DE** followed by 20 digits (e.g. DE89370400440532013000)"
            )
            st.session_state.step = "payment"
        else:
            agent_msg(
                "Please use this format:\n"
                "`Street Name, House Number, Postcode, City`\n\n"
                "Example: `Kastanienallee, 42, 10435, Berlin`"
            )

    # ── Payment / IBAN ────────────────────────────────────────────────────────
    elif step == "payment":
        iban = user_input.strip().replace(" ", "").upper()
        if iban.startswith("DE") and len(iban) == 22:
            st.session_state.bank["iban"] = iban
            st.session_state.bank["first_name"] = st.session_state.owner.get("first_name", "")
            st.session_state.bank["last_name"]  = st.session_state.owner.get("last_name", "")
            st.session_state.step = "confirm"
            st.rerun()
        else:
            agent_msg(
                "A German IBAN starts with **DE** and has 22 characters total.\n"
                "Example: `DE89370400440532013000`"
            )

    # ── Confirm ───────────────────────────────────────────────────────────────
    elif step == "confirm":
        answer = user_input.strip().lower()
        if any(w in answer for w in ["yes", "confirm", "ja", "ok", "agree", "proceed", "buy", "✓"]):
            with st.spinner("Creating your insurance application..."):
                try:
                    meta = policies.POLICY_MAP[st.session_state.selected_category]
                    start_date = st.session_state.selected_start_date or st.session_state.start_dates[0]
                    now_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+01:00")

                    lead = api.create_lead({
                        "customer": {
                            **st.session_state.owner,
                            "gender": "male",
                            "sign_up_source": "da_direkt",
                        },
                        "contract": {
                            "policy_category": st.session_state.selected_category,
                            "starting_at": start_date,
                            "billing_day": "1",
                            "insurance_for": "me",
                            "documents_accepted_at": now_str,
                            "insured_pet": {
                                "breed_id":      st.session_state.breed_id,
                                "name":          st.session_state.dog.get("name"),
                                "gender":        st.session_state.dog.get("gender"),
                                "date_of_birth": st.session_state.dog.get("date_of_birth"),
                                "pet_type":      "dog",
                            },
                        },
                        "bank_account": st.session_state.bank,
                    })
                    st.session_state.lead_uuid = lead["uuid"]

                    plan_name = meta["name"]
                    price = st.session_state.prices[st.session_state.selected_category]
                    agent_msg(
                        f"🎉 **Coverage successfully bound!**\n\n"
                        f"**Policy:** {plan_name}\n"
                        f"**Dog:** {st.session_state.dog.get('name')} ({st.session_state.breed_name})\n"
                        f"**Start date:** {start_date}\n"
                        f"**Monthly premium:** €{price:.2f}\n"
                        f"**Reference:** `{lead['uuid']}`\n\n"
                        f"Welcome to DA Direkt! 🐾 A confirmation email will be sent to "
                        f"**{st.session_state.owner.get('email')}**.\n\n"
                        f"You can access your policy documents in the DA Direkt customer portal."
                    )
                    st.session_state.step = "done"
                except Exception as e:
                    agent_msg(
                        f"⚠️ There was an issue creating the application: `{e}`\n\n"
                        "Please try again or contact DA Direkt support."
                    )
        elif any(w in answer for w in ["no", "nein", "cancel", "stop", "back"]):
            agent_msg(
                "No problem — I've cancelled the purchase. Your data has not been submitted.\n\n"
                "If you'd like to start again, type **restart**."
            )
        else:
            agent_msg("Please type **yes** to confirm the purchase, or **no** to cancel.")

    # ── Done / restart ────────────────────────────────────────────────────────
    elif step == "done":
        if "restart" in user_input.lower():
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        else:
            agent_msg(
                "Your policy is active. 🐾\n\n"
                "Is there anything else I can help you with? "
                "Type **restart** to start a new quote."
            )

    st.rerun()

# ── Quoting step (no user input needed — triggered by step change) ────────────
if st.session_state.step == "quoting" and st.session_state.prices is None:
    with st.spinner("Fetching live prices from DA Direkt..."):
        prices = {}
        for cat in policies.all_dog_categories():
            try:
                prices[cat] = api.get_price(
                    st.session_state.breed_id,
                    cat,
                    st.session_state.dog["date_of_birth"],
                )
            except Exception:
                pass
        start_dates = api.get_start_dates()
        st.session_state.prices = prices
        st.session_state.start_dates = start_dates
        st.session_state.selected_start_date = start_dates[0] if start_dates else None
        st.session_state.step = "select_plan"

    # Build price comparison message
    dog_name = st.session_state.dog["name"]
    breed = st.session_state.breed_name

    lines = [
        f"Here are **live prices** for **{dog_name}** ({breed}):\n",
        "---",
        "### 🏥 Vollschutz — Full Health Coverage",
        "_Covers: outpatient, inpatient, surgery, diagnostics, medication_\n",
    ]
    for cat in [14, 15, 16]:
        meta = policies.POLICY_MAP[cat]
        price = prices.get(cat, 0)
        tier = meta["tier"].replace("_", " ").title()
        rec = " ⭐ *Most popular*" if cat == 15 else ""
        lines.append(f"**{tier}** — €{price:.2f}/month{rec}")
        lines.append(policies.TIER_DESCRIPTIONS[meta["tier"]] + "\n")

    lines += [
        "---",
        "### 🔪 OP-Schutz — Surgery Only",
        "_Covers: operations and hospitalisation only (not routine vet visits)_\n",
    ]
    for cat in [17, 18, 19]:
        meta = policies.POLICY_MAP[cat]
        price = prices.get(cat, 0)
        tier = meta["tier"].replace("_", " ").title()
        lines.append(f"**{tier}** — €{price:.2f}/month")
        lines.append(policies.TIER_DESCRIPTIONS[meta["tier"]] + "\n")

    lines += [
        "---",
        "💡 **Note:** Waiting period is 3 weeks from start date (accidents covered immediately). "
        "Free choice of any licensed vet in Germany.\n",
        f"Which plan would you like for **{dog_name}**? "
        "Type the plan name, e.g. **Vollschutz Premium** or **OP-Schutz Komfort**.",
    ]
    agent_msg("\n".join(lines))
    st.rerun()

# ── Plan selection (separate from chat input — handled by rerun) ──────────────
if st.session_state.step == "select_plan" and st.session_state.selected_category is None:
    # Check if the last user message is a plan selection
    user_msgs = [m for m in st.session_state.messages if m["role"] == "user"]
    if user_msgs:
        last = user_msgs[-1]["content"].lower()
        plan_map = {
            "vollschutz komfort": 14, "vollschutz premium plus": 16, "vollschutz premium": 15,
            "komfort vollschutz": 14, "premium plus vollschutz": 16, "premium vollschutz": 15,
            "op-schutz komfort": 17, "op schutz komfort": 17, "op-schutz premium plus": 19,
            "op-schutz premium": 18, "op schutz premium": 18,
            "komfort": 14, "premium plus": 16, "premium": 15,
        }
        matched = None
        for key, cat in plan_map.items():
            if key in last:
                matched = cat
                break

        if matched:
            st.session_state.selected_category = matched
            meta = policies.POLICY_MAP[matched]
            price = st.session_state.prices[matched]
            plan_name = meta["name"]

            agent_msg(
                f"Excellent choice! ✅ **{plan_name}** at **€{price:.2f}/month**.\n\n"
                f"**Start date:** {st.session_state.selected_start_date}\n"
                f"_(You can also choose from: {', '.join(st.session_state.start_dates[:3])})_\n\n"
                f"Now I need a few details to complete your application.\n\n"
                f"What is your **full name**? (first name and last name)"
            )
            st.session_state.step = "owner_name"
            st.rerun()

# ── Confirm step — show summary card ─────────────────────────────────────────
if st.session_state.step == "confirm" and not any(
    "Please review" in m["content"] for m in st.session_state.messages
    if m["role"] == "assistant"
):
    meta = policies.POLICY_MAP[st.session_state.selected_category]
    price = st.session_state.prices[st.session_state.selected_category]
    owner = st.session_state.owner
    dog = st.session_state.dog
    start = st.session_state.selected_start_date

    summary = (
        f"📋 **Please review your application before confirming:**\n\n"
        f"| | |\n|---|---|\n"
        f"| **Policy** | {meta['name']} |\n"
        f"| **Monthly premium** | €{price:.2f} |\n"
        f"| **Start date** | {start} |\n"
        f"| **Dog** | {dog.get('name')} · {st.session_state.breed_name} · "
        f"{dog.get('date_of_birth')} · {dog.get('gender')} |\n"
        f"| **Policyholder** | {owner.get('first_name')} {owner.get('last_name')} |\n"
        f"| **Email** | {owner.get('email')} |\n"
        f"| **Phone** | {owner.get('phone_number')} |\n"
        f"| **Address** | {owner.get('street_name')} {owner.get('house_number')}, "
        f"{owner.get('postcode')} {owner.get('city')} |\n"
        f"| **IBAN** | {st.session_state.bank.get('iban', '')[:6]}...{st.session_state.bank.get('iban', '')[-4:]} |\n\n"
        f"By confirming, you accept the DA Direkt insurance terms and conditions.\n\n"
        f"Type **yes** to confirm and bind coverage, or **no** to cancel."
    )
    agent_msg(summary)
    st.rerun()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🐾 K9 Agent")
    st.markdown("**DA Direkt Dog Insurance**")
    st.markdown("---")

    if st.session_state.dog.get("name"):
        st.markdown("**Your Dog**")
        st.markdown(f"🐕 {st.session_state.dog.get('name', '—')}")
        st.markdown(f"Breed: {st.session_state.breed_name or '—'}")
        st.markdown(f"Born: {st.session_state.dog.get('date_of_birth', '—')}")
        st.markdown("---")

    if st.session_state.selected_category:
        meta = policies.POLICY_MAP[st.session_state.selected_category]
        price = st.session_state.prices[st.session_state.selected_category]
        st.markdown("**Selected Plan**")
        st.markdown(f"📄 {meta['name']}")
        st.markdown(f"💶 €{price:.2f}/month")
        st.markdown("---")

    if st.session_state.lead_uuid:
        st.markdown("**Policy Reference**")
        st.markdown(f"`{st.session_state.lead_uuid}`")
        st.markdown("---")

    st.markdown("**Coverage FAQ**")
    with st.expander("Waiting period"):
        st.markdown(policies.COVERAGE_FAQ["waiting_period"])
    with st.expander("Free vet choice?"):
        st.markdown(policies.COVERAGE_FAQ["free_vet_choice"])
    with st.expander("What is GOT?"):
        st.markdown(policies.COVERAGE_FAQ["got_explanation"])
    with st.expander("Pre-existing conditions"):
        st.markdown(policies.COVERAGE_FAQ["preexisting_conditions"])
    with st.expander("Deductible"):
        st.markdown(policies.COVERAGE_FAQ["deductible"])
    with st.expander("How to claim"):
        st.markdown(policies.COVERAGE_FAQ["reimbursement"])

    st.markdown("---")
    if st.button("🔄 Start over", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
