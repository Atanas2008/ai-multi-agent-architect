"""
Unit tests for Agent 1 — Input Analyzer & Classifier.
These tests use the mock (no-API-key) path.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from agents.agent1_analyzer import Agent1Analyzer


@pytest.fixture
def agent():
    return Agent1Analyzer(client=None)  # mock mode


class TestAgent1Analyzer:

    def test_returns_required_keys(self, agent):
        result = agent.analyze("We need to reduce our marketing spend.")
        for key in ("domain", "intent", "urgency", "complexity", "key_entities", "constraints", "summary"):
            assert key in result, f"Missing key: {key}"

    def test_domain_marketing_detected(self, agent):
        result = agent.analyze("Our marketing campaigns are underperforming.")
        assert result["domain"] == "Marketing"

    def test_domain_finance_detected(self, agent):
        result = agent.analyze("We need to reduce operational costs and improve budget allocation.")
        assert result["domain"] == "Finance"

    def test_domain_technology_detected(self, agent):
        result = agent.analyze("Our software infrastructure is struggling to scale.")
        assert result["domain"] == "Technology"

    def test_domain_operations_detected(self, agent):
        result = agent.analyze("Our supply chain logistics process is inefficient.")
        assert result["domain"] == "Operations"

    def test_intent_cost_reduction(self, agent):
        result = agent.analyze("We want to reduce our operational costs by 20%.")
        assert result["intent"] == "Cost Reduction"

    def test_intent_revenue_growth(self, agent):
        result = agent.analyze("We want to grow revenue and scale our sales team.")
        assert result["intent"] == "Revenue Growth"

    def test_intent_process_improvement(self, agent):
        result = agent.analyze("We need to improve our deployment process.")
        assert result["intent"] == "Process Improvement"

    def test_urgency_high_on_urgent_keywords(self, agent):
        result = agent.analyze("This is urgent: we need to fix our critical issue immediately.")
        assert result["urgency"] == "High"

    def test_urgency_default_medium(self, agent):
        result = agent.analyze("We are thinking about a new product strategy.")
        assert result["urgency"] == "Medium"

    def test_complexity_high_on_long_input(self, agent):
        long_input = " ".join(["word"] * 50)
        result = agent.analyze(long_input)
        assert result["complexity"] == "High"

    def test_complexity_medium_on_short_input(self, agent):
        result = agent.analyze("Improve our sales.")
        assert result["complexity"] == "Medium"

    def test_key_entities_is_list(self, agent):
        result = agent.analyze("Customer retention strategy for B2B SaaS.")
        assert isinstance(result["key_entities"], list)

    def test_constraints_is_list(self, agent):
        result = agent.analyze("Any business challenge.")
        assert isinstance(result["constraints"], list)

    def test_summary_is_string(self, agent):
        result = agent.analyze("We need help with our HR hiring process.")
        assert isinstance(result["summary"], str)
        assert len(result["summary"]) > 0

    def test_parse_json_strips_markdown_fences(self, agent):
        raw = '```json\n{"key": "value"}\n```'
        result = agent._parse_json(raw)
        assert result == {"key": "value"}

    def test_parse_json_plain(self, agent):
        raw = '{"domain": "Finance"}'
        result = agent._parse_json(raw)
        assert result["domain"] == "Finance"
