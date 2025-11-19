import psycopg 
import numpy as np
from sentence_transformers import SentenceTransformer
import requests, sys
import os, time

# Get environment variables
PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")

print(f"Variables are: PGUSER:{PGUSER}, PGPASSWORD:{PGPASSWORD}")


try:
    # Connect to postgres service
    conn = psycopg.connect(f"host=pg dbname=rag user={PGUSER} password={PGPASSWORD}")
    with conn, conn.cursor() as cur:
        cur.execute("""
        Create extension vector;
        """)
        
        time.sleep(2)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS chunks(
            id bigserial PRIMARY KEY,
            doc_id text,
            chunk_index int,
            text text,
            embedding vector(768)
        );
        """)


    print("Imports done, we're in the script lol")

    print("Can we make a numpy array?")
    np_zeroes_test = np.zeros((3, 4))
    print(np_zeroes_test)
    print("The answer is yes I think maybe, see above")


except Exception as e:
    print(f"An unexpected error occurred: {e}")


while time.sleep(30):
    print("sleeping...")