"""
Agent 2 — Core Processor & Strategy Generator

Responsibilities:
  - Consume the structured context produced by Agent 1
  - Generate a comprehensive, business-grade strategic response
  - Produce actionable recommendations, a roadmap, and expected KPIs
  - Output a structured response object for Agent 3 to refine
"""

import os
from openai import OpenAI

SYSTEM_PROMPT = """You are a world-class management consultant and business strategist with experience at
McKinsey, BCG, and leading technology companies.

You will receive a structured business context (JSON) produced by a classification agent.
Your task is to generate a comprehensive strategic response that includes:

1. **Executive Summary** — 2-3 sentences capturing the core opportunity or challenge.
2. **Strategic Recommendations** — 3-5 specific, actionable recommendations with rationale.
3. **Implementation Roadmap** — Three phases (Quick Wins / 0-3 months, Strategic Initiatives / 3-12 months, Long-term Vision / 12+ months).
4. **Expected KPIs & Outcomes** — 3-5 measurable success metrics.
5. **Risk Considerations** — 2-3 key risks and mitigation strategies.

Format your response in clean Markdown. Be concise, professional, and business-oriented.
Avoid generic advice — make every recommendation specific to the domain and intent provided."""

_MOCK_RESPONSE = """## Executive Summary

Your organisation faces a strategic challenge that, when addressed systematically, represents a significant opportunity for sustainable competitive advantage. By applying a structured, data-driven approach across three key dimensions, you can achieve measurable impact within 90 days while building long-term resilience.

---

## Strategic Recommendations

### 1. Establish a Data-Driven Decision Framework
Implement a unified analytics layer to surface real-time performance signals. This removes guesswork and enables rapid pivots based on evidence rather than intuition.

### 2. Prioritise High-Leverage Quick Wins
Identify the top 20% of activities that drive 80% of outcomes. Redirect resources towards these levers immediately to demonstrate early ROI and build organisational momentum.

### 3. Build Cross-Functional Alignment
Create a dedicated task force with representatives from each impacted business unit. Weekly cadences and shared OKRs ensure accountability and prevent siloed execution.

### 4. Automate Repetitive Workflows
Map current manual processes and automate the three highest-volume workflows. This typically yields 30-40% efficiency gains within the first quarter.

### 5. Establish a Feedback Loop
Deploy lightweight measurement mechanisms (NPS, cycle time, error rate) and review monthly. Continuous feedback shortens learning cycles and compounds improvement over time.

---

## Implementation Roadmap

**Phase 1 — Quick Wins (0–3 months)**
- Audit current state and baseline KPIs
- Deploy automation for top 3 manual workflows
- Launch cross-functional alignment sessions

**Phase 2 — Strategic Initiatives (3–12 months)**
- Roll out unified analytics platform
- Implement revised operating model
- Upskill teams on new tooling and processes

**Phase 3 — Long-term Vision (12+ months)**
- Achieve full process automation across business units
- Establish Centre of Excellence for continuous improvement
- Expand successful pilots to adjacent business areas

---

## Expected KPIs & Outcomes

| Metric | Current Baseline | 12-Month Target |
|--------|-----------------|-----------------|
| Operational Efficiency | Baseline | +35% |
| Cost per Process Unit | Baseline | -25% |
| Time-to-Decision | Baseline | -40% |
| Employee Productivity | Baseline | +20% |
| Customer Satisfaction | Baseline | +15 NPS points |

---

## Risk Considerations

**Risk 1 — Change Resistance**
*Mitigation:* Secure executive sponsorship early and communicate the "why" clearly to all stakeholders.

**Risk 2 — Resource Constraints**
*Mitigation:* Phase investments to align with budget cycles; prioritise initiatives with the highest ROI-to-effort ratio.

**Risk 3 — Technology Integration Complexity**
*Mitigation:* Begin with a pilot programme in one business unit before scaling; maintain rollback capabilities throughout."""


class Agent2Processor:
    """Generates strategic recommendations based on classified context."""

    def __init__(self, client: OpenAI | None = None, model: str = "gpt-4o-mini"):
        self.client = client
        self.model = model

    def process(self, context: dict, original_input: str) -> str:
        """
        Generate strategic content for the given context.

        Args:
            context: Structured analysis dict from Agent 1.
            original_input: The original raw user query.

        Returns:
            A Markdown-formatted strategic response string.
        """
        if self.client is None:
            return self._mock_process(context)

        user_message = (
            f"**Original user query:**\n{original_input}\n\n"
            f"**Classified context:**\n"
            f"- Domain: {context.get('domain')}\n"
            f"- Intent: {context.get('intent')}\n"
            f"- Urgency: {context.get('urgency')}\n"
            f"- Complexity: {context.get('complexity')}\n"
            f"- Key entities: {', '.join(context.get('key_entities', []))}\n"
            f"- Constraints: {', '.join(context.get('constraints', []))}\n"
            f"- Summary: {context.get('summary')}"
        )

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.7,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content.strip()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _mock_process(self, context: dict) -> str:
        domain = context.get("domain", "Strategy")
        intent = context.get("intent", "Improvement")
        urgency = context.get("urgency", "Medium")

        header = (
            f"## Executive Summary\n\n"
            f"Your **{domain}** challenge — centred on **{intent}** with **{urgency}** urgency — "
            f"is a well-defined opportunity. The following recommendations are tailored to your specific context "
            f"and designed to deliver measurable results within a realistic timeframe.\n"
        )
        return header + _MOCK_RESPONSE[_MOCK_RESPONSE.index("\n---"):]
