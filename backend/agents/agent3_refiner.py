"""
Agent 3 — Validator, Optimiser & Refiner

Responsibilities:
  - Review the strategic content produced by Agent 2
  - Validate completeness, coherence, and business appropriateness
  - Optimise language for executive-level audiences
  - Add a concrete "Next Steps" action plan
  - Assign a confidence score and quality assessment
  - Return the final, polished output ready for the user
"""

import os
from openai import OpenAI

SYSTEM_PROMPT = """You are a senior executive editor and quality-assurance specialist for business strategy documents.

You will receive a draft strategic response. Your task is to:

1. **Validate** — Confirm that the response is complete, coherent, and relevant.
2. **Optimise** — Sharpen the language to be crisp, executive-ready, and action-oriented. Remove any vague or generic statements.
3. **Add Next Steps** — Append a concrete "Immediate Next Steps" section with 3 specific actions the user should take in the next 7 days.
4. **Quality Score** — End with a brief quality note: `> **Quality Assessment:** [X/10] — [one-sentence rationale]`

Return the refined, complete document in clean Markdown. Do not add meta-commentary about your editing process."""

_NEXT_STEPS_SUFFIX = """
---

## Immediate Next Steps (Next 7 Days)

1. **Schedule a stakeholder kick-off** — Bring together the relevant business unit leaders to align on the challenge and validate the proposed approach.
2. **Baseline your KPIs** — Capture current performance metrics across the 3-5 KPIs identified above so you can measure progress objectively.
3. **Identify a pilot scope** — Select one business unit or process to test the first quick-win initiative, minimising risk while building proof of concept.

---

> **Quality Assessment:** 9/10 — Comprehensive, actionable, and structured for executive presentation with clear phases and measurable outcomes.
"""


class Agent3Refiner:
    """Validates, optimises, and finalises the strategic output."""

    def __init__(self, client: OpenAI | None = None, model: str = "gpt-4o-mini"):
        self.client = client
        self.model = model

    def refine(self, draft: str, context: dict) -> dict:
        """
        Refine and validate the strategic draft.

        Args:
            draft: Markdown strategic content from Agent 2.
            context: Original classification context from Agent 1.

        Returns:
            A dict with keys: ``content`` (final Markdown) and ``quality_score`` (int 1-10).
        """
        if self.client is None:
            return self._mock_refine(draft)

        user_message = (
            f"**Domain context:** {context.get('domain')} / {context.get('intent')}\n\n"
            f"**Draft response to refine:**\n\n{draft}"
        )

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.3,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        refined = response.choices[0].message.content.strip()
        score = self._extract_score(refined)
        return {"content": refined, "quality_score": score}

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _extract_score(self, text: str) -> int:
        """Parse the quality score from the output (e.g. '9/10')."""
        import re
        match = re.search(r"\b(\d{1,2})/10\b", text)
        return int(match.group(1)) if match else 8

    def _mock_refine(self, draft: str) -> dict:
        refined = draft.rstrip() + _NEXT_STEPS_SUFFIX
        return {"content": refined, "quality_score": 9}
