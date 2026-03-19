# StratAI — AI Multi-Agent Business Advisor

> A professional, hackathon-ready web application demonstrating a three-agent AI pipeline for business strategy generation.

![StratAI Hero](https://github.com/user-attachments/assets/49715f07-1d48-46ba-8ed0-44cc36a9f75b)

---

## Overview

**StratAI** is a business-ready AI advisory platform that orchestrates three specialised AI agents to transform a raw business challenge into a polished, executive-grade strategic report — in seconds.

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Flask 3, OpenAI API |
| Frontend | HTML5, CSS3, Vanilla JS (no framework) |
| AI Model | GPT-4o-mini (falls back to deterministic mock without API key) |

---

## System Architecture

```
User Input → [Agent 1: Analyzer] → [Agent 2: Processor] → [Agent 3: Refiner] → Output
```

### Agent Responsibilities

| Agent | Role | Output |
|-------|------|--------|
| **Agent 1 — Analyzer** | Parses input; classifies domain, intent, urgency, complexity; extracts entities | Structured JSON context |
| **Agent 2 — Processor** | Generates executive summary, recommendations, phased roadmap, KPIs, risks | Markdown strategic draft |
| **Agent 3 — Refiner** | Validates completeness, sharpens language, adds 7-day action plan, scores quality | Polished Markdown + score |

---

## Project Structure

```
ai-multi-agent-architect/
├── backend/
│   ├── app.py                   # Flask application & REST API
│   ├── orchestrator.py          # Multi-agent pipeline coordinator
│   ├── requirements.txt
│   ├── .env.example
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── agent1_analyzer.py   # Input analysis & classification
│   │   ├── agent2_processor.py  # Strategy generation
│   │   └── agent3_refiner.py    # Validation, optimisation & refinement
│   └── tests/
│       ├── test_agent1.py
│       ├── test_agent2.py
│       ├── test_agent3.py
│       └── test_integration.py
└── frontend/
    ├── index.html               # Single-page application
    ├── css/style.css
    └── js/main.js
```

---

## Quick Start

### 1. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure environment (optional)

```bash
cp .env.example .env
# Add your OPENAI_API_KEY to .env for live AI responses.
# Without a key the app runs in demo mode with deterministic mock responses.
```

### 3. Run the server

```bash
python app.py
# Open http://localhost:5000
```

---

## API Reference

### `POST /api/analyze`

Runs the full three-agent pipeline.

**Request**
```json
{ "query": "Our SaaS startup has a 25% monthly churn rate..." }
```

**Response**
```json
{
  "context":       { "domain": "Marketing", "intent": "Cost Reduction", ... },
  "draft":         "## Executive Summary\n...",
  "final_output":  "## Executive Summary\n...\n## Immediate Next Steps\n...",
  "quality_score": 9,
  "timings":       { "agent1": 0.42, "agent2": 1.85, "agent3": 0.93 },
  "mode":          "live"
}
```

### `GET /api/health`

Returns `{ "status": "ok", "mode": "demo" | "live" }`.

---

## Running Tests

```bash
cd backend
pytest tests/ -v
# 58 tests — all agents + orchestrator + Flask API
```

---

## User Flow

1. **Describe** your business challenge in plain English
2. **Agent 1** classifies domain, intent, urgency, and extracts key entities
3. **Agent 2** generates a full strategic response with roadmap and KPIs
4. **Agent 3** refines, validates, adds next steps, and scores quality
5. **Download** the executive-ready report

![Pipeline Result](https://github.com/user-attachments/assets/6c3ff4a2-e44e-4342-9ee5-b3d5fec9ad3e)

---

## Demo Mode

The application works **without an OpenAI API key** using intelligent keyword-based heuristics for Agent 1 and high-quality pre-structured templates for Agents 2 and 3. This makes it ideal for hackathon demonstrations without incurring API costs.
