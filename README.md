# K9 Agent

AI-native dog insurance agent for Zurich / DA Direkt — Agentic AI Hyper Challenge 2026.

## Architecture

```
Customer Agent (claude-haiku — fast, cheap)
       │  natural language / structured data
       ▼
Zurich K9 Agent (claude-sonnet — reasoning + tool use)
       │  tool calls
       ▼
Petolo REST APIs (beta.dentolo-test.de)
  ├── Breeds API       → resolve breed names
  ├── Policies API     → list coverage plans
  ├── Price API        → calculate monthly premium
  ├── Leads API        → manage the customer lead
  ├── Recurring API    → detect duplicate leads
  ├── Start Dates API  → valid contract start dates
  └── Customers API    → bind coverage (convert lead)
```

## Plans

| Category | Name | Coverage | Tier |
|----------|------|----------|------|
| 14 | Vollschutz Komfort | Full health | Entry |
| 15 | Vollschutz Premium | Full health | Mid |
| 16 | Vollschutz Premium Plus | Full health | Top |
| 17 | OP-Schutz Komfort | Surgery only | Entry |
| 18 | OP-Schutz Premium | Surgery only | Mid |
| 19 | OP-Schutz Premium Plus | Surgery only | Top |

## Setup

```bash
export ANTHROPIC_API_KEY=sk-ant-...
pip install anthropic httpx
```

## Usage

### Interactive chat (human ↔ Zurich Agent)
```bash
python chat.py
```

### Agent-to-agent simulation (full journey, safe dry run)
```bash
python simulate.py --dry-run
```

### Agent-to-agent simulation (live bind)
```bash
python simulate.py
```

### Smoke-test all APIs (no API key needed)
```bash
python test_apis.py
```

## File structure

```
k9-agent/
├── chat.py              # Interactive human ↔ agent chat
├── simulate.py          # Agent-to-agent simulation
├── test_apis.py         # API smoke tests
└── k9_agent/
    ├── api.py           # REST API wrappers (Petolo)
    ├── policies.py      # Static plan knowledge + FAQ
    ├── tools.py         # Tool schemas + dispatcher
    ├── zurich_agent.py  # Zurich Agent (agentic loop)
    └── customer_agent.py # Personal/customer agent
```
