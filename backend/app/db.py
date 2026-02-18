import psycopg2

def get_connection():
    return psycopg2.connect(
        "postgresql://voter_db_i5mt_user:1l3LLcTIr8kj6AE9IOpcuojnrOtK1iHf@dpg-d67etvk9c44c73dj8ucg-a.singapore-postgres.render.com/voter_db_i5mt",
        sslmode="require"
    )
  

