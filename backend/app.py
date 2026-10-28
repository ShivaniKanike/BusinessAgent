"""
app.py - Flask Backend API
Simple REST API that accepts questions and returns answers.
"""

import sys
import os

# Add project root to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, request, jsonify, send_from_directory
from ai_engine.query_engine import execute_query
from database.db_setup import create_database

app = Flask(__name__, static_folder="../static")


@app.route("/")
def home():
    """Serve the simple HTML frontend."""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/ask", methods=["POST"])
def ask_question():
    """
    API endpoint to ask a question.
    Expects JSON: {"question": "your question here"}
    Returns JSON with answer, data, sql_query, etc.
    """
    data = request.get_json(force=True, silent=True)

    # Validate input
    if not data or "question" not in data:
        return jsonify({"error": "Please provide a question in JSON format: {\"question\": \"...\"}"}), 400

    question = data["question"].strip()
    if len(question) == 0:
        return jsonify({"error": "Question cannot be empty"}), 400

    # Get answer from query engine
    result = execute_query(question)

    # Always return 200 — the frontend checks result["error"] to show messages
    return jsonify(result), 200


@app.route("/api/health", methods=["GET"])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "ok", "message": "API is running"}), 200


# TODO: Add endpoint for getting list of sample questions
# TODO: Add endpoint for revenue comparison between two months


if __name__ == "__main__":
    # Create database on startup
    print("[INFO] Setting up database...")
    create_database()
    print("[INFO] Starting Flask server on port 5001...")
    app.run(debug=True, port=5001)

