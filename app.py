"""
K9 Agent — DA Direkt Dog Insurance
Streamlit chat UI powered by Claude (Zurich Agent) with live Petolo API calls.

Run with:
    export ANTHROPIC_API_KEY=sk-ant-...
    streamlit run app.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from k9_agent.zurich_agent import ZurichAgent

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
if "agent" not in st.session_state:
    try:
        st.session_state.agent = ZurichAgent()
        st.session_state.messages = []
        st.session_state.started = False
    except EnvironmentError as e:
        st.error(str(e))
        st.stop()

# ── Render chat history ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🐾" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# ── Opening greeting ──────────────────────────────────────────────────────────
if not st.session_state.started:
    with st.spinner("K9 Agent is starting..."):
        reply = st.session_state.agent.chat(
            "Hello! Greet the customer warmly and ask for their dog's details to get started."
        )
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.started = True
    st.rerun()

# ── Chat input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🐾"):
        with st.spinner("K9 Agent is thinking..."):
            reply = st.session_state.agent.chat(user_input)
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🐾 K9 Agent")
    st.markdown("**DA Direkt Dog Insurance**")
    st.markdown("*Powered by Claude*")
    st.markdown("---")

    st.markdown(
        "This is an AI-native insurance agent. "
        "Just talk naturally — describe your dog, ask questions, "
        "compare plans, and confirm to bind coverage.\n\n"
        "**Example questions:**\n"
        "- *My dog is a 2-year-old Golden Retriever called Luna*\n"
        "- *What's the difference between the plans?*\n"
        "- *What isn't covered?*\n"
        "- *I'd like the Premium plan*"
    )
    st.markdown("---")

    if st.button("🔄 Start new conversation", use_container_width=True):
        st.session_state.agent.reset()
        st.session_state.messages = []
        st.session_state.started = False
        st.rerun()
