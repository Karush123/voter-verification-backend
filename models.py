from db import get_connection

def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS voters (
            voter_id VARCHAR(50) PRIMARY KEY,
            name TEXT,
            face_embedding FLOAT[],
            fingerprint_template TEXT,
            has_voted BOOLEAN DEFAULT FALSE
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
