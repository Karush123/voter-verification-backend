from app.db import get_connection

def process_vote(data):
    voter_id = data.get("voter_id")

    if not voter_id:
        return {"status": "error", "message": "Voter ID missing"}

    conn = get_connection()
    cursor = conn.cursor()

    # Check if voter exists
    cursor.execute("SELECT has_voted FROM voters WHERE voter_id=?", (voter_id,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return {"status": "error", "message": "Voter not found"}

    if result[0] == 1:
        conn.close()
        return {"status": "error", "message": "Already voted"}

    # Mark as voted
    cursor.execute("UPDATE voters SET has_voted=1 WHERE voter_id=?", (voter_id,))
    conn.commit()
    conn.close()

    return {"status": "success", "message": "Vote recorded"}
