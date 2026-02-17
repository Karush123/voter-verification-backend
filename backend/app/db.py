import psycopg2
import os

def get_connection():
    DATABASE_URL = "postgresql://voter_db_i5mt_user:1l3LLcTIr8kj6AE9IOpcuojnrOtK1iHf@dpg-d67etvk9c44c73dj8ucg-a.singapore-postgres.render.com/voter_db_i5mt"
    return psycopg2.connect(DATABASE_URL)

