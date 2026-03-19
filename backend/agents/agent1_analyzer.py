"""
Agent 1 — Input Analyzer & Classifier

Responsibilities:
  - Parse and understand the raw user input
  - Classify the domain (e.g., marketing, operations, finance, HR, product)
  - Detect intent, urgency, and complexity level
  - Extract key entities and constraints
  - Pass a structured context object to Agent 2
"""

import json
import os
import re
from openai import OpenAI

SYSTEM_PROMPT = """You are a senior business analyst AI specializing in problem classification.
Your sole responsibility is to analyze the user's business challenge and produce a structured JSON context object.

You MUST respond with valid JSON only — no prose, no markdown, no explanation.

The JSON must have exactly these keys:
{
  "domain": "<one of: Marketing | Operations | Finance | HR | Product | Technology | Strategy | Other>",
  "intent": "<one of: Cost Reduction | Revenue Growth | Process Improvement | Risk Mitigation | Innovation | Other>",
  "urgency": "<one of: High | Medium | Low>",
  "complexity": "<one of: High | Medium | Low>",
  "key_entities": ["<entity1>", "<entity2>", ...],
  "constraints": ["<constraint1>", "<constraint2>", ...],
  "summary": "<One crisp sentence summarising the core business problem>"
}"""

# Fallback classification used when no API key is available
_FALLBACK_TEMPLATE = {
    "domain": "Strategy",
    "intent": "Process Improvement",
    "urgency": "Medium",
    "complexity": "Medium",
    "key_entities": ["business process", "stakeholders", "resources"],
    "constraints": ["budget limitations", "time constraints"],
    "summary": "A strategic business challenge requiring structured analysis and actionable recommendations.",
}


class Agent1Analyzer:
    """Analyzes and classifies incoming business queries."""

    def __init__(self, client: OpenAI | None = None, model: str = "gpt-4o-mini"):
        self.client = client
        self.model = model

    def analyze(self, user_input: str) -> dict:
        """
        Analyze the user's business input and return a structured context dict.

        Args:
            user_input: Raw text submitted by the user.

        Returns:
            A dict with classification metadata (domain, intent, urgency, etc.)
        """
        if self.client is None:
            return self._mock_analyze(user_input)

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
        )
        raw = response.choices[0].message.content.strip()
        return self._parse_json(raw)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _parse_json(self, raw: str) -> dict:
        """Extract the first JSON object found in *raw*."""
        # Strip potential markdown fences
        cleaned = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
        return json.loads(cleaned)

    def _mock_analyze(self, user_input: str) -> dict:
        """Return a deterministic mock analysis based on keyword heuristics."""
        text = user_input.lower()

        domain_map = {
            "marketing": "Marketing",
            "sales": "Marketing",
            "brand": "Marketing",
            "customer": "Marketing",
            "finance": "Finance",
            "cost": "Finance",
            "budget": "Finance",
            "revenue": "Finance",
            "profit": "Finance",
            "hr": "HR",
            "hiring": "HR",
            "talent": "HR",
            "employee": "HR",
            "product": "Product",
            "feature": "Product",
            "roadmap": "Product",
            "technology": "Technology",
            "software": "Technology",
            "infrastructure": "Technology",
            "security": "Technology",
            "operations": "Operations",
            "process": "Operations",
            "supply": "Operations",
            "logistics": "Operations",
        }

        intent_map = {
            "reduce": "Cost Reduction",
            "cut": "Cost Reduction",
            "save": "Cost Reduction",
            "grow": "Revenue Growth",
            "increase": "Revenue Growth",
            "expand": "Revenue Growth",
            "scale": "Revenue Growth",
            "improve": "Process Improvement",
            "optimise": "Process Improvement",
            "optimize": "Process Improvement",
            "risk": "Risk Mitigation",
            "security": "Risk Mitigation",
            "innovat": "Innovation",
            "new": "Innovation",
            "launch": "Innovation",
        }

        domain = "Strategy"
        for kw, val in domain_map.items():
            if kw in text:
                domain = val
                break

        intent = "Other"
        for kw, val in intent_map.items():
            if kw in text:
                intent = val
                break

        urgency = "High" if any(w in text for w in ("urgent", "asap", "immediately", "critical")) else "Medium"
        complexity = "High" if len(user_input.split()) > 40 else "Medium"

        words = [w.strip(".,!?") for w in user_input.split() if len(w) > 4][:5]

        return {
            "domain": domain,
            "intent": intent,
            "urgency": urgency,
            "complexity": complexity,
            "key_entities": words if words else _FALLBACK_TEMPLATE["key_entities"],
            "constraints": _FALLBACK_TEMPLATE["constraints"],
            "summary": f"Business challenge in the {domain} domain focused on {intent.lower()}.",
        }
