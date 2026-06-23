# Hyper Challenge 2026 — Technical Summary

---

## Team

- **Team name:** `Retail_Agentic_Commerce_LiviuGhenghea`
- **Use case:** `Retail_Agentic_Commerce` — Agentic Commerce for the Personal Agent Era
- **Platform used:** `claude_api`
- **Team members:**
  - Liviu Ghenghea, `liviu.ghenghea@zurich.com`

---

## Where to find your submission

| Artifact | Filename or URL |
|---|---|
| GitHub repo | https://github.com/LiviuGhenghea/Retail_Agentic_Commerce_LiviuGhenghea |
| Live demo | https://k9agent.streamlit.app |
| Exported workflow / solution | https://k9agent.streamlit.app |
| Copilot Studio agent name | N/A |
| Demo video | `LiviuGhenghea_Retail_Agentic_Commerce.mp4` |
| Video transcript | `LiviuGhenghea_Retail_Agentic_Commerce_transcript.md` |
| Pitch deck | `LiviuGhenghea_Retail_Agentic_Commerce.pdf` |
| Technical summary | `Retail_Agentic_Commerce_LiviuGhenghea.md` |
| Process design map | `LiviuGhenghea_Retail_Agentic_Commerce_processmap.png` |
| URL to prototype | https://k9agent.streamlit.app |

---

## Models & tools summary

| Stage | Model / Tool | Purpose |
|---|---|---|
| Zurich Agent — reasoning & tool orchestration | `claude-sonnet-4-6` | Drives the insurance journey: understands intent, selects tools, generates transparent explanations |
| Customer Agent — personal agent simulation | `claude-haiku-4-5-20251001` | Acts on behalf of the dog owner: initiates requests, evaluates responses, provides data, confirms consent |
| Breeds API | `GET /api/petolo/v1/breeds` | Resolves breed names to numeric IDs required for pricing |
| Policies API | `GET /api/petolo/v1/policies` | Retrieves live catalogue of dog insurance plans |
| Price API | `GET /api/petolo/v1/price` | Calculates monthly premium for a given breed, DOB, and plan |
| Leads API | `POST/PUT/GET /api/petolo/v1/leads` | Creates and progressively enriches a customer lead through the funnel |
| Recurring Lead Check | `POST /api/petolo/v1/leads/check_recurring_lead` | Detects duplicate leads by email or phone |
| Contract Start Dates API | `GET /api/v1/contracts/available_start_dates` | Returns valid policy start dates (first of month, up to 6 months ahead) |
| Customers API | `POST /api/petolo/v1/customers` | Converts a fully-populated lead into a live insurance application (bind) |

---

## 1. What did you build?

### Goal

K9 Agent is an AI-native, agent-to-agent insurance journey for DA Direkt dog health insurance. It eliminates the current linear, form-driven web funnel and replaces it with a conversational, adaptive experience where a **customer-owned personal agent** interacts directly with a **Zurich-hosted insurance agent** to research, quote, and bind coverage — without the customer needing to navigate a website.

The system directly addresses the five pain points identified in the AS-IS analysis: relevance, understanding, engagement, transparency, and purchase guidance — all resolved through natural conversation rather than static pages.

### Key components

```
┌─────────────────────────────────────────────────────────────┐
│                    CUSTOMER AGENT                           │
│         claude-haiku-4-5  (personal agent layer)           │
│  • Holds owner + dog profile                               │
│  • Drives conversation: asks, evaluates, consents          │
│  • Simulates real-world agent-to-agent interaction         │
└──────────────────────────┬──────────────────────────────────┘
                           │  natural language messages
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   ZURICH K9 AGENT                           │
│         claude-sonnet-4-6  (insurance specialist)          │
│  • Stateful conversation history                           │
│  • Agentic tool-use loop (12 tools)                        │
│  • Transparent explanations: GOT, exclusions, scenarios    │
│  • Manages full lead lifecycle                             │
└──────────────────────────┬──────────────────────────────────┘
                           │  REST API calls (httpx)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               PETOLO / DA DIREKT BETA APIS                  │
│  Breeds · Policies · Price · Leads · Customers             │
│  Recurring Check · Contract Start Dates                    │
│  Base: https://beta.dentolo-test.de                        │
└─────────────────────────────────────────────────────────────┘
```

**12 tools** are available to the Zurich Agent:

| Tool | Purpose |
|---|---|
| `search_breeds` | Resolve breed name → breed_id |
| `get_all_plans` | List all 6 coverage options |
| `get_price` | Price a single plan |
| `get_all_prices` | Full comparison table across all plans |
| `get_plan_details` | Plain-language plan description |
| `get_coverage_faq` | Answer: waiting periods, GOT, pre-existing conditions, deductibles, reimbursement |
| `get_available_start_dates` | Valid contract start dates |
| `create_lead` | Open a new lead in the system |
| `update_lead` | Progressively enrich lead data |
| `get_lead` | Retrieve current lead state |
| `check_missing_fields` | Validate readiness before bind |
| `bind_coverage` | Convert lead to insurance application |

---

## 2. How did you build it?

### Agent interaction model

The system uses a **two-agent, sequential interaction** pattern — not a single monolithic agent:

1. **Customer Agent** opens the conversation with the owner's dog profile and sends the first message to the Zurich Agent.
2. **Zurich Agent** enters an agentic loop: receives the message, decides which tools to call (if any), executes them against live APIs, and returns a response.
3. **Customer Agent** evaluates the response and decides the next message — pushing for more detail, providing owner data, or confirming consent.
4. The loop continues until the Zurich Agent successfully calls `bind_coverage` or the customer agent signals completion.

The **Zurich Agent is the orchestrator**: it owns the tool-use loop, the lead UUID, and the conversation state. The Customer Agent is a lightweight driver that simulates realistic human-agent behaviour.

### Technology stack

| Component | Technology |
|---|---|
| LLM backbone | Anthropic Claude API (`claude-sonnet-4-6`, `claude-haiku-4-5`) |
| HTTP client | `httpx` (sync, with 15s timeout) |
| Language | Python 3.9+ |
| Agent framework | Native Anthropic tool-use (no LangChain / AutoGen) |
| API authentication | `x-api-key` header (Petolo beta key) |
| State management | In-memory conversation history (list of messages) |

### Data and knowledge base

- **Live API data**: breeds, plans, prices, start dates — all fetched in real time from the beta environment. No static price tables.
- **Static knowledge layer** (`policies.py`): plan descriptions, tier comparisons, GOT explanations, FAQ answers — grounded in the AS-IS documentation and real product terms.
- **Synthetic owner profiles** (`simulate.py`): realistic German customer data (name, address, IBAN, pet details) used for the agent-to-agent demo.

### Journey flow (non-linear by design)

The Zurich Agent does **not** follow a fixed script. It responds to the customer agent's questions in any order — if asked about pre-existing conditions before breed, it answers. If the customer provides all data in one message, it processes it in one pass. The journey adapts:

```
Research → Quote → Explain → Recommend → Collect data → Validate → Confirm → Bind
     ↑_______________|______________|_______________|
          (non-linear: any step can loop back)
```

---

## 3. How do you control and evaluate it?

### Behavioural controls

- **System prompt constraints**: The Zurich Agent's system prompt explicitly prohibits marketing language, requires transparency on exclusions and waiting periods, and mandates explicit consent before calling `bind_coverage`.
- **Tool gating**: `bind_coverage` can only be called after `check_missing_fields` confirms all required fields are present. The tool dispatcher validates inputs before any API call.
- **Field validation**: All 15+ required fields for customer conversion are validated in `tools.py` before the bind is attempted. Errors surface as structured messages to the agent, not silent failures.
- **Dry-run mode**: `simulate.py --dry-run` stops the simulation before bind — safe for demos and testing.

### Evaluation approach

- **API smoke tests** (`test_apis.py`): 18 tests covering all API endpoints and tool dispatcher functions — run in ~10 seconds, no LLM calls required.
- **Agent-to-agent simulation**: the full journey is observable as structured turn-by-turn output, making it easy to audit decisions.
- **Lead state inspection**: `get_lead` can be called at any point to verify the exact data state in the system.

### Known limitations and risks

| Risk | Mitigation |
|---|---|
| LLM hallucination of prices or coverage terms | All prices fetched live from API; static FAQ answers grounded in documented product terms |
| Incomplete data at bind time | `check_missing_fields` tool catches gaps before `bind_coverage` is called |
| Ambiguous breed names | `search_breeds` returns a list; agent asks customer to confirm before proceeding |
| Pre-existing condition misclassification | Agent proactively surfaces FAQ on pre-existing conditions when relevant |
| Beta API availability | `httpx` raises clear exceptions; agent surfaces errors as natural language messages |
| Prompt injection (noted in submission criteria) | Agent system prompt does not instruct it to follow external instructions; tool results are treated as data |

---

## 4. How do you scale it?

### Path to production

| Step | What's needed |
|---|---|
| Replace beta URL | Change `BASE` in `api.py` to production Faircare URL |
| Production API key | Rotate from beta key to production credential (env var, not hardcoded) |
| Persistent lead state | Store `lead_uuid` per user session in a database (Redis / Postgres) |
| Authentication | Add customer identity verification before bind (already modelled in `documents_accepted_at` field) |
| Webhook support | Subscribe to Petolo lead status webhooks to handle async policy issuance |

### Scaling the agent layer

- **Stateless design**: each `ZurichAgent` instance holds only in-memory history — trivial to containerise and scale horizontally.
- **Model tiering**: Haiku for the customer agent keeps costs low; Sonnet only where reasoning depth matters (Zurich Agent).
- **Multi-channel**: the `ZurichAgent.chat()` interface is channel-agnostic — the same agent core can serve WhatsApp, web chat, voice (with STT/TTS wrapper), or other AI agents via MCP.
- **Multi-product**: the tool and policy layer can be extended to cat insurance, liability, or other DA Direkt products with minimal changes to the agent core.

### MCP server opportunity

The 12 tools in `tools.py` can be exposed as an **MCP (Model Context Protocol) server**, making the Zurich Agent discoverable and callable by any MCP-compatible personal agent (Claude, Perplexity, others) — a direct path to the agent-to-agent commerce standard described in the challenge brief.

---

## 5. Cost considerations

### Prototype build cost

| Item | Estimate |
|---|---|
| Development time | ~1 day (Claude Code assisted) |
| API calls during development | ~$2–5 (Anthropic) |
| Beta Petolo API | Provided free for hackathon |

### Cost per simulation run (agent-to-agent, ~10 turns)

| Component | Tokens (approx.) | Cost (approx.) |
|---|---|---|
| Zurich Agent (Sonnet) | ~15,000 input + 3,000 output | ~$0.06 |
| Customer Agent (Haiku) | ~5,000 input + 1,000 output | ~$0.003 |
| **Total per full journey** | | **~$0.06** |

### Cost at scale

| Volume | Monthly cost estimate |
|---|---|
| 1,000 quote journeys/month | ~$60 |
| 10,000 quote journeys/month | ~$600 |
| 100,000 quote journeys/month | ~$6,000 |

The solution is **token-lean by design**: the Customer Agent uses Haiku, tool results are concise JSON (not verbose text), and the static knowledge layer avoids RAG/vector search overhead. Caching the system prompt (Anthropic prompt caching) would reduce costs by ~80% on the Sonnet calls at scale.

---

## 6. Learnings

### What worked well

- **Native tool-use without a framework**: building directly on the Anthropic API (no LangChain/AutoGen) kept the system transparent, debuggable, and fast. The tool-use loop is ~50 lines of code.
- **Probing the live API first**: calling the beta endpoints before writing any agent code meant the policy/pricing knowledge was grounded in real data from the start, not assumptions.
- **Two-agent design**: separating the customer agent (lightweight, cheap) from the Zurich agent (capable, orchestrating) proved a natural fit — it mirrors how real agent-to-agent commerce will work, where the personal agent and the insurer's agent are independent systems.
- **Check-before-bind pattern**: the `check_missing_fields` tool prevents the most common failure mode (trying to bind with incomplete data) and gives the agent a clear, structured path to completion.

### What we would do differently

- **Add streaming output**: for a live demo, streaming the Zurich Agent's responses token-by-token would be more engaging than waiting for the full response.
- **Persist session state**: the current in-memory history means a browser refresh loses context. A short-lived Redis session store would fix this for a production demo.
- **Add a web UI**: a simple chat interface (FastAPI + WebSocket) would make the demo more compelling than a terminal simulation.
- **Broader edge case testing**: more time would go into testing unusual breeds, very old dogs, dogs with declared health conditions, and incomplete IBAN formats — the areas most likely to trip up in the hackathon's adversarial testing phase.

---

*Submitted by: Liviu Ghenghea · liviu.ghenghea@zurich.com · 2026-06-22*
