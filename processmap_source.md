# K9 Agent — Process Design Map
## Retail_Agentic_Commerce_LiviuGhenghea

---

```
╔══════════════════════════════════════════════════════════════════════════════════════════════╗
║                              K9 AGENT — PROCESS DESIGN MAP                                  ║
║              AI-Native Dog Insurance: Research → Quote → Bind                               ║
╚══════════════════════════════════════════════════════════════════════════════════════════════╝

┌────────────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 1 — CUSTOMER SIDE                                                                   │
│                                                                                            │
│  ┌─────────────────────────────────────────────┐                                          │
│  │         CUSTOMER AGENT (Haiku)              │                                          │
│  │                                             │                                          │
│  │  Profile: owner name, address, DOB, IBAN    │                                          │
│  │           dog name, breed, DOB, gender      │                                          │
│  │           budget & coverage preference      │                                          │
│  │                                             │                                          │
│  │  Capabilities:                              │                                          │
│  │  • Opens conversation with dog profile      │                                          │
│  │  • Evaluates plan options & prices          │                                          │
│  │  • Asks about exclusions & waiting periods  │                                          │
│  │  • Provides owner details on request        │                                          │
│  │  • Gives explicit purchase consent          │                                          │
│  └──────────────────────┬──────────────────────┘                                          │
│                         │  Natural language messages (turn-by-turn)                       │
└─────────────────────────┼──────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 2 — ZURICH AGENT (Orchestrator)                                                     │
│                                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                    ZURICH K9 AGENT (claude-sonnet-4-6)                              │  │
│  │                                                                                     │  │
│  │   Conversation History ──► System Prompt ──► Claude API                            │  │
│  │                                   │                                                 │  │
│  │                                   ▼                                                 │  │
│  │                         ┌─────────────────┐                                        │  │
│  │                         │  AGENTIC LOOP   │                                        │  │
│  │                         │                 │                                        │  │
│  │    ┌────────────────────┤  stop_reason?   ├────────────────────┐                  │  │
│  │    │  tool_use          └────────┬────────┘       end_turn     │                  │  │
│  │    ▼                            │                              ▼                  │  │
│  │  Execute                        │                     Return text response        │  │
│  │  tools                          │                     to Customer Agent           │  │
│  │    │                            │                                                 │  │
│  │    └────────────────────────────┘                                                 │  │
│  │    (tool results appended to history, loop continues)                             │  │
│  └──────────────────────────────────┬──────────────────────────────────────────────┘  │  │
│                                     │  Tool calls (httpx REST)                        │  │
└─────────────────────────────────────┼──────────────────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 3 — TOOLS (12 available)                                                            │
│                                                                                            │
│  RESEARCH TOOLS                  PRICING TOOLS              JOURNEY TOOLS                 │
│  ┌───────────────────┐           ┌──────────────────┐       ┌────────────────────────┐    │
│  │ search_breeds     │           │ get_price        │       │ create_lead            │    │
│  │ get_all_plans     │           │ get_all_prices   │       │ update_lead            │    │
│  │ get_plan_details  │           └──────────────────┘       │ get_lead               │    │
│  │ get_coverage_faq  │                                       │ check_missing_fields   │    │
│  │ get_start_dates   │                                       │ bind_coverage          │    │
│  └───────────────────┘                                       └────────────────────────┘    │
│                                                                                            │
└────────────────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 4 — PETOLO BETA APIs  (https://beta.dentolo-test.de)                                │
│                                                                                            │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  /breeds   │  │ /policies  │  │   /price   │  │    /leads    │  │   /customers    │   │
│  │  GET list  │  │ GET list   │  │  GET price │  │ POST create  │  │  POST convert   │   │
│  │  GET by id │  │            │  │            │  │ PUT  update  │  │  (bind)         │   │
│  └────────────┘  └────────────┘  └────────────┘  │ GET  fetch   │  └─────────────────┘   │
│                                                   │ POST recurr. │                         │
│                                                   └──────────────┘                         │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │  Auth: x-api-key: 7604c1e4-1248-4eb5-98ca-1b2afea54afe   (beta environment)        │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════
  JOURNEY FLOW (non-linear — any step can loop back)
═══════════════════════════════════════════════════════════════════

  [1] RESEARCH          [2] QUOTE             [3] COLLECT
  ─────────────         ──────────            ───────────
  Customer asks    →    Zurich calls    →     Customer provides
  about plans          get_all_prices         owner + dog data
  and coverage         search_breeds          (name, address,
  differences          get_all_plans          email, phone,
                                              IBAN, DOB)

        ↑                                           │
        └───────────────────────────────────────────┘
          (loops if customer has more questions)

  [4] VALIDATE          [5] CONFIRM           [6] BIND
  ────────────          ───────────           ──────
  check_missing   →     Zurich shows    →     Customer gives
  _fields()             full summary          explicit consent
                        + price              → bind_coverage()
                        + start date         → Lead converted
                        + plan details         to customer
                                             → Policy issued


═══════════════════════════════════════════════════════════════════
  POLICY CATEGORIES (live from /api/petolo/v1/policies)
═══════════════════════════════════════════════════════════════════

  VOLLSCHUTZ (Full Health)          OP-SCHUTZ (Surgery Only)
  ────────────────────────          ────────────────────────
  cat=14  Komfort    ~€48/mo        cat=17  Komfort    ~€48/mo
  cat=15  Premium    ~€59/mo        cat=18  Premium    ~€59/mo
  cat=16  Premium+   ~€81/mo        cat=19  Premium+   ~€81/mo
```
