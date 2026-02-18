from flask import Flask, request, jsonify
from models import create_tables
from db import get_connection
from face_utils import get_face_embedding, compare_faces
import requests
from flask import Flask, jsonify



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

# ---------------- VOTING MODE ----------------

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

    return jsonify({"status": "VERIFIED"})

@app.route("/capture-fingerprint", methods=["POST"])
def capture_fingerprint():
    try:
        rd_url = "http://localhost:11100/rd/capture"

        xml_request = '''<PidOptions ver="1.0">
                            <Opts fCount="1" fType="0" format="0" timeout="20000"/>
                         </PidOptions>'''

        response = requests.post(
            rd_url,
            data=xml_request,
            headers={"Content-Type": "text/xml"},
            timeout=30
        )

        return jsonify({
            "status": "success",
            "data": response.text
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

# ---------------- CAST VOTE ----------------

@app.route("/vote", methods=["POST"])
def cast_vote():
    voter_id = request.json["voter_id"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("UPDATE voters SET has_voted=TRUE WHERE voter_id=%s", (voter_id,))
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"message": "Vote Cast Successfully"})

if __name__ == "__main__":
    app.run()
