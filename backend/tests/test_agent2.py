"""
Unit tests for Agent 2 — Core Processor & Strategy Generator.
These tests use the mock (no-API-key) path.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from agents.agent2_processor import Agent2Processor


@pytest.fixture
def agent():
    return Agent2Processor(client=None)  # mock mode


SAMPLE_CONTEXT = {
    "domain": "Marketing",
    "intent": "Revenue Growth",
    "urgency": "High",
    "complexity": "Medium",
    "key_entities": ["campaigns", "customers"],
    "constraints": ["budget limitations"],
    "summary": "Improving marketing ROI to drive revenue growth.",
}


class TestAgent2Processor:

    def test_returns_string(self, agent):
        result = agent.process(SAMPLE_CONTEXT, "Improve our marketing ROI.")
        assert isinstance(result, str)

    def test_result_not_empty(self, agent):
        result = agent.process(SAMPLE_CONTEXT, "Improve our marketing ROI.")
        assert len(result.strip()) > 100

    def test_contains_executive_summary(self, agent):
        result = agent.process(SAMPLE_CONTEXT, "Improve our marketing ROI.")
        assert "Executive Summary" in result

    def test_contains_strategic_recommendations(self, agent):
        result = agent.process(SAMPLE_CONTEXT, "Improve our marketing ROI.")
        assert "Recommendation" in result or "recommendation" in result

    def test_contains_roadmap(self, agent):
        result = agent.process(SAMPLE_CONTEXT, "Improve our marketing ROI.")
        assert "Phase" in result or "Roadmap" in result or "roadmap" in result

    def test_contains_kpis(self, agent):
        result = agent.process(SAMPLE_CONTEXT, "Improve our marketing ROI.")
        assert "KPI" in result or "Metric" in result or "Outcome" in result

    def test_context_domain_reflected(self, agent):
        result = agent.process(SAMPLE_CONTEXT, "Improve our marketing ROI.")
        assert "Marketing" in result

    def test_context_intent_reflected(self, agent):
        result = agent.process(SAMPLE_CONTEXT, "Improve our marketing ROI.")
        assert "Revenue Growth" in result or "revenue" in result.lower()

    def test_different_domains_produce_output(self, agent):
        for domain in ("Finance", "Operations", "Technology", "HR"):
            ctx = {**SAMPLE_CONTEXT, "domain": domain}
            result = agent.process(ctx, "Generic business challenge.")
            assert isinstance(result, str) and len(result) > 50

    def test_markdown_headers_present(self, agent):
        result = agent.process(SAMPLE_CONTEXT, "Improve our marketing ROI.")
        assert "##" in result
