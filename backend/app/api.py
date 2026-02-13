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
