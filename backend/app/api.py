from flask import Flask, request, jsonify
from app.vote_flow import process_vote

app = Flask(__name__)

@app.route("/vote", methods=["POST"])
def vote():
    data = request.json
    result = process_vote(data)
    return jsonify(result)
