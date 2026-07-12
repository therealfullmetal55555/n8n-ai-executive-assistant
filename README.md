# Autonomous AI Executive Assistant (Tool-Calling Agent)

<div align="center">

[![n8n Agent](https://img.shields.io/badge/Agent_Engine-n8n_LangChain-EA4B71.svg?style=flat-square&logo=n8n&logoColor=white)](https://n8n.io/)
[![OpenAI GPT-4o](https://img.shields.io/badge/Model-GPT--4o-412991.svg?style=flat-square&logo=openai&logoColor=white)](https://openai.com/)
[![Google Calendar](https://img.shields.io/badge/Integration-Google_Calendar-4285F4.svg?style=flat-square&logo=googlecalendar&logoColor=white)](https://workspace.google.com/)
[![Notion](https://img.shields.io/badge/Database-Notion_API-000000.svg?style=flat-square&logo=notion&logoColor=white)](https://developers.notion.com/)
[![Tavily Search](https://img.shields.io/badge/Search-Tavily_AI-4F46E5.svg?style=flat-square)](https://tavily.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-2ea44f.svg?style=flat-square)](./LICENSE)
[![Safety Protocol](https://img.shields.io/badge/Safety_Gate-Confirm_Before_Write-blue.svg?style=flat-square)](#safety-guardrails--confirm-before-write)

**Multi-tool calling autonomous agent built in n8n and LangChain. Integrates Google Calendar, Notion, and Tavily Search with strict human-in-the-loop confirmation gates before executing calendar write actions.**

[Key Features](#key-features) • [Agent Architecture](#agent-architecture) • [Safety Protocol](#safety-guardrails--confirm-before-write) • [Quick Start](#quick-start) • [Cost Breakdown](#token-telemetry--cost-breakdown) • [Offline Traces](#offline-simulation-traces)

</div>

---

## Overview

Unlike standard chatbots that execute actions immediately upon single-turn user prompts, this executive assistant implements **two-step transactional safety**. 

When a user requests a meeting or calendar event, the agent first queries availability, drafts the proposal, and explicitly asks for confirmation. Only upon affirmative user consent does the agent invoke write tools.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ User:  "Schedule a 30-min strategy review with Alex tomorrow at 3 PM."      │
├─────────────────────────────────────────────────────────────────────────────┤
│ Agent: 🔍 Tool: calendar_check_availability(2026-09-29T15:00:00)            │
│        Result: Slot is available.                                           │
│                                                                             │
│        "I've verified that tomorrow (Sept 29) at 3:00 PM is free.          │
│         Should I go ahead and book 'Strategy Review with Alex' for 30 min?" │
├─────────────────────────────────────────────────────────────────────────────┤
│ User:  "Yes, please book it."                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ Agent: ✍️ Tool: calendar_create_event(summary, start, end)                  │
│        "✅ Event successfully created in your Google Calendar!"             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Features

- 🛠️ **Autonomous Multi-Tool Routing:** Dynamically selects the appropriate tool (Calendar, Notion, Web Search) based on real-time intent analysis.
- 🛡️ **Human-in-the-Loop Safety Gate:** System prompt forbids direct invocation of `calendar_create_event` without explicit prior confirmation from the user.
- ❓ **Active Disambiguation:** Asks clarifying questions whenever critical parameters (date, time, duration, attendee) are omitted.
- 🧠 **Multi-Turn Window Memory:** Maintains 10 conversational turns (20 messages) to support multi-step confirmation loops seamlessly.
- 🌐 **Real-Time Web Intelligence:** Routes research and company lookups through Tavily Search API.
- 📋 **Structured Notion Integration:** Creates tasks with properties (Status, Due Date, Priority) in Notion databases.

---

## Agent Architecture

<div align="center">
  <img src="assets/architecture.svg?v=2026" alt="n8n AI Executive Assistant Architecture" width="100%">
</div>

---

## Repository Structure

```text
n8n-ai-executive-assistant/
├── n8n-workflow.json        # 9-node n8n autonomous AI agent workflow
├── simulate_agent.py        # Python simulation testing multi-turn confirmation
├── docker-compose.yml       # Containerized n8n deployment stack
├── docs/
│   └── system-prompt.md     # Production system prompt with safety rules
├── demo-scenarios/
│   └── traces.json          # Recorded multi-turn tool execution traces
├── .env.example             # Environment variable template
├── .gitignore               # Standard git ignore rules
└── LICENSE                  # MIT License
```

---

## Safety Guardrails & Confirm-Before-Write

The agent operates under a strict system prompt safety specification (see [`docs/system-prompt.md`](./docs/system-prompt.md)):

```markdown
Rule 1 (Calendar Write Gate):
You MUST NEVER call `create_calendar_event` on the first user turn.
Always call `check_availability` first, formulate the booking proposal,
and ask the user: "Should I book this event for you?"

Rule 2 (Disambiguation):
If the user's request lacks specific date, time, or duration, ask for
clarification before invoking any write tool.

Rule 3 (Least Privilege Scope):
No delete or mass-update tools are exposed to the agent.
```

---

## Quick Start

### 1. Offline Simulation (No Credentials Required)

Validate the agent's intent classification, tool dispatching, and two-step confirmation flow locally:

```bash
# Clone the repository
git clone https://github.com/therealfullmetal55555/n8n-ai-executive-assistant.git
cd n8n-ai-executive-assistant

# Run offline simulation
python3 simulate_agent.py
```

<details>
<summary><b>🔍 Click to view Offline Simulation Traces</b></summary>

```text
================================================================================
AUTONOMOUS AI EXECUTIVE ASSISTANT: OFFLINE SIMULATION TRACES
================================================================================

[Scenario 1: Two-Turn Calendar Confirmation]
  Turn 1: User -> "Book a sync with Sarah tomorrow at 2 PM for 45 min."
    • Intent: Calendar Booking
    • Safety Gate: Check availability only (Write forbidden on Turn 1)
    • Tool Call: calendar_check_availability(start="2026-09-29T14:00:00")
    • Agent: "2:00 PM tomorrow is available. Should I confirm and book 'Sync with Sarah' (45 min)?"
  
  Turn 2: User -> "Yes, confirm."
    • Intent: Positive Confirmation
    • Safety Gate: Confirmed -> Allowed
    • Tool Call: calendar_create_event(summary="Sync with Sarah", start="2026-09-29T14:00:00")
    • Agent: "✅ Event successfully booked in your Google Calendar."

[Scenario 2: Notion Task Creation]
  Turn 1: User -> "Add task to Notion: Prepare Q3 analytics deck by Friday."
    • Intent: Task Management
    • Tool Call: notion_create_task(title="Prepare Q3 analytics deck", due_date="2026-10-02")
    • Agent: "✅ Task added to your Notion Tasks database."
================================================================================
```
</details>

### 2. Live n8n Deployment

1. Set up environment configuration:
   ```bash
   cp .env.example .env
   ```

2. Start the n8n container:
   ```bash
   docker compose up -d
   ```

3. Open `http://localhost:5678` in your browser.
4. Import [`n8n-workflow.json`](./n8n-workflow.json).
5. Configure OAuth2 & API credentials in n8n Credentials Manager:
   - **OpenAI API Key**
   - **Telegram Bot Token**
   - **Google Calendar OAuth2**
   - **Notion API Token**
   - **Tavily Search API Key**
6. Message your Telegram bot to test interactive execution.

---

## Token Telemetry & Cost Breakdown

*Calculated with standard OpenAI `gpt-4o` pricing ($2.50 / 1M prompt tokens, $10.00 / 1M output tokens):*

$$\text{Cost per Turn} = \left(\frac{650}{10^6} \times \$2.50\right) + \left(\frac{120}{10^6} \times \$10.00\right) \approx \mathbf{\$0.0028 \text{ USD}}$$

| Monthly Usage Volume | Estimated Prompt Tokens | Estimated Completion Tokens | Monthly LLM Cost |
| :---: | :---: | :---: | :---: |
| **100 dialogue turns** | ~65k | ~12k | **~$0.28 USD** |
| **500 dialogue turns** | ~325k | ~60k | **~$1.41 USD** |
| **2,000 dialogue turns** | ~1.30M | ~240k | **~$5.65 USD** |

---

## Engineering Design Decisions

| Architectural Decision | Implementation | Why it matters |
| :--- | :--- | :--- |
| **Confirm-Before-Write Policy** | Multi-Turn System Guardrail | Eliminates accidental calendar double-bookings and unwanted invites. |
| **Active Clarification** | Prompt Disambiguation Gate | Prevents hallucinated default durations or ambiguous dates. |
| **Read / Append-Only Scopes** | Restricted OAuth Scopes | Eliminates risk of catastrophic data loss by withholding delete/wipe permissions. |
| **Window Buffer Memory** | 10 Conversational Turns | Sufficient depth for confirmation dialogs while bounding prompt token consumption. |
| **Decoupled Prompt File** | [`docs/system-prompt.md`](./docs/system-prompt.md) | Enables version-controlled prompt reviews independent of workflow JSON schema. |

---

## License

Distributed under the MIT License. See [`LICENSE`](./LICENSE) for full details.
