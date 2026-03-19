"""
AI Multi-Agent Architect — Flask Application

Entry point for the backend API server.
"""

import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from orchestrator import Orchestrator

load_dotenv()

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

orchestrator = Orchestrator()


# ---------------------------------------------------------------------------
# Routes — Frontend static files
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(FRONTEND_DIR, path)


# ---------------------------------------------------------------------------
# Routes — API
# ---------------------------------------------------------------------------

@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    POST /api/analyze
    Body: { "query": "<user business query>" }
    Returns the full pipeline result as JSON.
    """
    data = request.get_json(silent=True) or {}
    user_input = (data.get("query") or "").strip()

    if not user_input:
        return jsonify({"error": "The 'query' field is required and must not be empty."}), 400

    if len(user_input) > 2000:
        return jsonify({"error": "Query must not exceed 2000 characters."}), 400

    try:
        result = orchestrator.run(user_input)
        return jsonify(result)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:  # noqa: BLE001
        app.logger.exception("Unexpected pipeline error: %s", type(exc).__name__)
        return jsonify({"error": "An internal error occurred. Please try again."}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "mode": orchestrator.get_mode()})


# ---------------------------------------------------------------------------
# Dev server entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
