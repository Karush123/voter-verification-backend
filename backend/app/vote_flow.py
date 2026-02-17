from app.db import get_connection
from app.face_utils import compare_faces
import json

def process_vote(data):
    voter_id = data.get("voter_id")
    face_embedding = data.get("face_embedding")
    fingerprint_template = data.get("fingerprint_template")

    if not voter_id:
        return {"status": "error", "message": "Missing voter ID"}

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT face_encoding, fingerprint_template, has_voted FROM voters WHERE voter_id=%s",
        (voter_id,)
    )

    result = cursor.fetchone()

    if not result:
        conn.close()
        return {"status": "error", "message": "Voter not found"}

    stored_face = json.loads(result[0])
    stored_fingerprint = result[1]
    has_voted = result[2]

    if has_voted == 1:
        conn.close()
        return {"status": "error", "message": "Already voted"}

    if not compare_faces(stored_face, face_embedding):
        conn.close()
        return {"status": "error", "message": "Face mismatch"}

    if stored_fingerprint != fingerprint_template:
        conn.close()
        return {"status": "error", "message": "Fingerprint mismatch"}

    cursor.execute("UPDATE voters SET has_voted=1 WHERE voter_id=%s", (voter_id,))
    conn.commit()
    conn.close()

    return {"status": "success", "message": "Vote recorded"}
