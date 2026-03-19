"""
Unit tests for Agent 3 — Validator, Optimiser & Refiner.
These tests use the mock (no-API-key) path.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from agents.agent3_refiner import Agent3Refiner


@pytest.fixture
def agent():
    return Agent3Refiner(client=None)  # mock mode


SAMPLE_DRAFT = """## Executive Summary

This is a draft strategic response for testing purposes.

## Recommendations

1. Do something actionable.
2. Measure results.
3. Iterate quickly.

## Roadmap

Phase 1: Quick wins.
Phase 2: Strategic rollout.
Phase 3: Long-term vision.
"""

SAMPLE_CONTEXT = {
    "domain": "Operations",
    "intent": "Process Improvement",
    "urgency": "Medium",
    "complexity": "Medium",
}


class TestAgent3Refiner:

    def test_returns_dict(self, agent):
        result = agent.refine(SAMPLE_DRAFT, SAMPLE_CONTEXT)
        assert isinstance(result, dict)

    def test_returns_content_key(self, agent):
        result = agent.refine(SAMPLE_DRAFT, SAMPLE_CONTEXT)
        assert "content" in result

    def test_returns_quality_score_key(self, agent):
        result = agent.refine(SAMPLE_DRAFT, SAMPLE_CONTEXT)
        assert "quality_score" in result

    def test_content_is_string(self, agent):
        result = agent.refine(SAMPLE_DRAFT, SAMPLE_CONTEXT)
        assert isinstance(result["content"], str)

    def test_quality_score_is_int(self, agent):
        result = agent.refine(SAMPLE_DRAFT, SAMPLE_CONTEXT)
        assert isinstance(result["quality_score"], int)

    def test_quality_score_in_range(self, agent):
        result = agent.refine(SAMPLE_DRAFT, SAMPLE_CONTEXT)
        assert 1 <= result["quality_score"] <= 10

    def test_content_contains_next_steps(self, agent):
        result = agent.refine(SAMPLE_DRAFT, SAMPLE_CONTEXT)
        assert "Next Steps" in result["content"] or "next steps" in result["content"].lower()

    def test_content_contains_original_draft(self, agent):
        result = agent.refine(SAMPLE_DRAFT, SAMPLE_CONTEXT)
        assert "Executive Summary" in result["content"]

    def test_content_extended_beyond_draft(self, agent):
        result = agent.refine(SAMPLE_DRAFT, SAMPLE_CONTEXT)
        assert len(result["content"]) > len(SAMPLE_DRAFT)

    def test_extract_score_from_text(self, agent):
        text = "Some content. > **Quality Assessment:** 8/10 — Good overall."
        assert agent._extract_score(text) == 8

    def test_extract_score_defaults_to_8(self, agent):
        assert agent._extract_score("No score here at all.") == 8

    def test_extract_score_handles_10(self, agent):
        assert agent._extract_score("Score: 10/10") == 10
