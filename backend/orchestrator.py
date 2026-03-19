"""
Orchestrator — Multi-Agent Pipeline Coordinator

The orchestrator manages the sequential execution of the three AI agents,
handles error propagation, and assembles the final response payload.

Pipeline:
  User Input → Agent 1 (Analyze) → Agent 2 (Process) → Agent 3 (Refine) → Output
"""

import os
import time
from openai import OpenAI

from agents import Agent1Analyzer, Agent2Processor, Agent3Refiner


class Orchestrator:
    """Coordinates the three-agent AI pipeline."""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            client = OpenAI(api_key=api_key)
        else:
            client = None  # Fall back to mock responses

        self.agent1 = Agent1Analyzer(client=client)
        self.agent2 = Agent2Processor(client=client)
        self.agent3 = Agent3Refiner(client=client)
        self._using_mock = client is None

    def get_mode(self) -> str:
        """Return 'demo' if running with mock responses, 'live' if using the OpenAI API."""
        return "demo" if self._using_mock else "live"

    def run(self, user_input: str) -> dict:
        """
        Execute the full multi-agent pipeline for a given user query.

        Args:
            user_input: Raw business query from the user.

        Returns:
            A structured result dict containing:
              - ``context``       : Agent 1 classification output
              - ``draft``         : Agent 2 raw strategic output
              - ``final_output``  : Agent 3 refined content (Markdown)
              - ``quality_score`` : Confidence score (1–10)
              - ``timings``       : Per-agent execution times (seconds)
              - ``mode``          : "live" or "demo" (indicates whether a real AI model was used)
        """
        user_input = user_input.strip()
        if not user_input:
            raise ValueError("User input must not be empty.")

        timings = {}

        # ── Agent 1: Analyze & Classify ───────────────────────────────
        t0 = time.perf_counter()
        context = self.agent1.analyze(user_input)
        timings["agent1"] = round(time.perf_counter() - t0, 3)

        # ── Agent 2: Generate Strategy ────────────────────────────────
        t0 = time.perf_counter()
        draft = self.agent2.process(context, user_input)
        timings["agent2"] = round(time.perf_counter() - t0, 3)

        # ── Agent 3: Validate & Refine ────────────────────────────────
        t0 = time.perf_counter()
        refined = self.agent3.refine(draft, context)
        timings["agent3"] = round(time.perf_counter() - t0, 3)

        return {
            "context": context,
            "draft": draft,
            "final_output": refined["content"],
            "quality_score": refined["quality_score"],
            "timings": timings,
            "mode": self.get_mode(),
        }
