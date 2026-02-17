from flask import Flask, request, jsonify
from app.vote_flow import process_vote

app = Flask(__name__)

@app.route("/")
def home():
    return "Backend is running"

@app.route("/health")
def health():
    return "OK"

@app.route("/vote", methods=["POST"])
def vote():
    data = request.json
    result = process_vote(data)
    return jsonify(result)
@app.route("/verify_voter", methods=["POST"])
def verify_voter():
    from app.db import get_connection
    data = request.json
    voter_id = data.get("voter_id")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT has_voted FROM voters WHERE voter_id=%s", (voter_id,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return jsonify({"status": "error", "message": "Voter not found"})

    if result[0] == 1:
        conn.close()
        return jsonify({"status": "error", "message": "Already voted"})

    conn.close()
    return jsonify({"status": "success", "message": "Voter verified"})
