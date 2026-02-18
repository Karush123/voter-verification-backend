from flask import Flask, request, jsonify
from models import create_tables
from db import get_connection
from face_utils import compare_faces

app = Flask(__name__)

create_tables()

# ---------------- ADMIN MODE ----------------

@app.route("/admin/register", methods=["POST"])
def register_voter():
    data = request.json

    voter_id = data["voter_id"]
    name = data["name"]
    face_embedding = data["face_embedding"]
    fingerprint_template = data["fingerprint"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO voters (voter_id, name, face_embedding, fingerprint_template)
        VALUES (%s, %s, %s, %s)
    """, (voter_id, name, face_embedding, fingerprint_template))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Voter Registered Successfully"})

# ---------------- VERIFY FACE ----------------

@app.route("/verify", methods=["POST"])
def verify_voter():
    data = request.json
    voter_id = data["voter_id"]
    live_face_embedding = data["face_embedding"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT face_embedding, has_voted FROM voters WHERE voter_id=%s", (voter_id,))
    record = cur.fetchone()

    if not record:
        return jsonify({"status": "VOTER_NOT_FOUND"})

    stored_embedding, has_voted = record

    if has_voted:
        return jsonify({"status": "ALREADY_VOTED"})

    match = compare_faces(stored_embedding, live_face_embedding)

    if not match:
        return jsonify({"status": "FACE_MISMATCH"})

    cur.close()
    conn.close()

    return jsonify({"status": "FACE_VERIFIED"})

# ---------------- STORE FINGERPRINT ----------------

@app.route("/store-fingerprint", methods=["POST"])
def store_fingerprint():
    data = request.json
    voter_id = data["voter_id"]
    fingerprint_xml = data["fingerprint_xml"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE voters
        SET fingerprint_template=%s
        WHERE voter_id=%s
    """, (fingerprint_xml, voter_id))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "FINGERPRINT_STORED"})

# ---------------- CAST VOTE ----------------

@app.route("/vote", methods=["POST"])
def cast_vote():
    voter_id = request.json["voter_id"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE voters
        SET has_voted=TRUE
        WHERE voter_id=%s
    """, (voter_id,))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Vote Cast Successfully"})
@app.route("/check-db")
def check_db():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM voters;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {"rows": rows}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    create_tables()
    app.run(debug=True)
