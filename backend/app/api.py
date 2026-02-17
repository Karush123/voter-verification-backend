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
@app.route("/verify_face", methods=["POST"])
def verify_face():
    from app.face_utils import get_face_embedding, compare_faces
    from app.db import get_connection
    import json

    data = request.json
    voter_id = data.get("voter_id")
    image = data.get("image")

    embedding = get_face_embedding(image)

    if embedding is None:
        return jsonify({"status": "error", "message": "No face detected"})

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT face_encoding FROM voters WHERE voter_id=%s", (voter_id,))
    result = cursor.fetchone()

    stored_face = result[0]

    # If no face stored yet → store it
    if stored_face is None:
        cursor.execute(
            "UPDATE voters SET face_encoding=%s WHERE voter_id=%s",
            (json.dumps(embedding), voter_id)
        )
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Face registered"})

    # Compare
    stored_face = json.loads(stored_face)
    match = compare_faces(stored_face, embedding)

    conn.close()

    if not match:
        return jsonify({"status": "error", "message": "Face mismatch"})

    return jsonify({"status": "success", "message": "Face verified"})
