"""
Integration tests for the Orchestrator pipeline and Flask API.
These tests use the mock (no-API-key) path.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import json


# ── Orchestrator tests ───────────────────────────────────────────────────── #

from orchestrator import Orchestrator


@pytest.fixture
def orchestrator():
    return Orchestrator()  # will use mock mode (no OPENAI_API_KEY in CI)


class TestOrchestrator:

    def test_run_returns_dict(self, orchestrator):
        result = orchestrator.run("We need to reduce churn in our SaaS product.")
        assert isinstance(result, dict)

    def test_result_has_required_keys(self, orchestrator):
        result = orchestrator.run("Improve employee engagement.")
        for key in ("context", "draft", "final_output", "quality_score", "timings", "mode"):
            assert key in result, f"Missing key: {key}"

    def test_context_is_dict(self, orchestrator):
        result = orchestrator.run("Scale our engineering team.")
        assert isinstance(result["context"], dict)

    def test_draft_is_string(self, orchestrator):
        result = orchestrator.run("Launch a new product line.")
        assert isinstance(result["draft"], str)

    def test_final_output_is_string(self, orchestrator):
        result = orchestrator.run("Expand into European markets.")
        assert isinstance(result["final_output"], str)

    def test_quality_score_range(self, orchestrator):
        result = orchestrator.run("Reduce operational costs.")
        assert 1 <= result["quality_score"] <= 10

    def test_timings_has_agent_keys(self, orchestrator):
        result = orchestrator.run("Any business challenge.")
        for key in ("agent1", "agent2", "agent3"):
            assert key in result["timings"]

    def test_timings_are_positive(self, orchestrator):
        result = orchestrator.run("Any business challenge.")
        for key in ("agent1", "agent2", "agent3"):
            assert result["timings"][key] >= 0

    def test_mode_is_demo_without_api_key(self, orchestrator):
        result = orchestrator.run("Test query.")
        assert result["mode"] == "demo"

    def test_empty_input_raises_value_error(self, orchestrator):
        with pytest.raises(ValueError):
            orchestrator.run("")

    def test_whitespace_input_raises_value_error(self, orchestrator):
        with pytest.raises(ValueError):
            orchestrator.run("   ")


# ── Flask API tests ──────────────────────────────────────────────────────── #

from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


class TestFlaskAPI:

    def test_health_endpoint(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"

    def test_analyze_returns_200_on_valid_input(self, client):
        resp = client.post(
            "/api/analyze",
            data=json.dumps({"query": "We need to improve customer retention."}),
            content_type="application/json",
        )
        assert resp.status_code == 200

    def test_analyze_returns_required_fields(self, client):
        resp = client.post(
            "/api/analyze",
            data=json.dumps({"query": "Improve our sales process."}),
            content_type="application/json",
        )
        data = resp.get_json()
        for key in ("context", "final_output", "quality_score", "timings", "mode"):
            assert key in data, f"Missing key: {key}"

    def test_analyze_returns_400_on_empty_query(self, client):
        resp = client.post(
            "/api/analyze",
            data=json.dumps({"query": ""}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_analyze_returns_400_on_missing_query(self, client):
        resp = client.post(
            "/api/analyze",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_analyze_returns_400_on_too_long_query(self, client):
        resp = client.post(
            "/api/analyze",
            data=json.dumps({"query": "x" * 2001}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_index_serves_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"<!DOCTYPE html>" in resp.data or b"StratAI" in resp.data

    def test_analyze_mode_is_demo_without_key(self, client):
        resp = client.post(
            "/api/analyze",
            data=json.dumps({"query": "Scale our technology stack."}),
            content_type="application/json",
        )
        data = resp.get_json()
        assert data["mode"] == "demo"
