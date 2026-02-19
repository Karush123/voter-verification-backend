from flask import Flask, request, jsonify
from models import create_tables
from db import get_connection
from face_utils import generate_embedding_from_base64, compare_faces
import json

app = Flask(__name__)

# Create tables on startup
with app.app_context():
    create_tables()

# ---------------- ADMIN REGISTER ----------------

@app.route("/admin/register", methods=["POST"])
def register_voter():
    try:
        data = request.get_json()

        voter_id = data["voter_id"]
        name = data["name"]
        image_base64 = data["image"]  # <-- frontend sends image

        # Generate embedding from image
        face_embedding = generate_embedding_from_base64(image_base64)
        face_embedding = json.dumps(face_embedding)

        fingerprint_template = data["fingerprint_template"]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT voter_id FROM voters WHERE voter_id=%s", (voter_id,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"error": "VOTER_ALREADY_EXISTS"}), 400

        cur.execute("""
            INSERT INTO voters (voter_id, name, face_embedding, fingerprint_template)
            VALUES (%s, %s, %s, %s)
        """, (voter_id, name, face_embedding, fingerprint_template))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Voter Registered Successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- FINAL VERIFY + VOTE ----------------

@app.route("/verify-and-vote", methods=["POST"])
def verify_and_vote():
    try:
        data = request.get_json()
        voter_id = data["voter_id"]
        image_base64 = data["image"]
        live_face_embedding = generate_embedding_from_base64(image_base64)
        live_fingerprint = data["fingerprint_template"]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT face_embedding, fingerprint_template, has_voted
            FROM voters
            WHERE voter_id=%s
        """, (voter_id,))

        record = cur.fetchone()

        if not record:
            cur.close()
            conn.close()
            return jsonify({"status": "VOTER_NOT_FOUND"})

        stored_face, stored_fingerprint, has_voted = record

        if has_voted:
            cur.close()
            conn.close()
            return jsonify({"status": "ALREADY_VOTED"})

        face_match = compare_faces(stored_face, live_face_embedding)

        if not face_match:
            cur.close()
            conn.close()
            return jsonify({"status": "FACE_MISMATCH"})

        if stored_fingerprint != live_fingerprint:
            cur.close()
            conn.close()
            return jsonify({"status": "FINGERPRINT_MISMATCH"})

        cur.execute("""
            UPDATE voters
            SET has_voted=TRUE
            WHERE voter_id=%s
        """, (voter_id,))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"status": "VOTE_SUCCESS"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- DEBUG ROUTE ----------------

@app.route("/check-db")
def check_db():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT voter_id, name, has_voted FROM voters;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"rows": rows})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    create_tables()
    app.run(debug=True)
