import psycopg 
import numpy as np
from sentence_transformers import SentenceTransformer
import requests, sys
import os, time

try:
    # Get environment variables
    PGUSER = os.getenv("PGUSER")
    PGPASSWORD = os.getenv("PGPASSWORD")
    print(f"Variables are: PGUSER:{PGUSER}, PGPASSWORD:{PGPASSWORD}")
    

    # Connect to postgres service
    print("Initializing postgres vector database...")
    conn = psycopg.connect(f"host=pg dbname=rag user={PGUSER} password={PGPASSWORD}")
    with conn, conn.cursor() as cur:
        print("Enabling vector extension...")
        cur.execute("""
        CREATE EXTENSION IF NOT EXISTS vector;
        """)
        
        time.sleep(2)

        print("Creating chunks table...")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS chunks(
            id bigserial PRIMARY KEY,
            doc_id text,
            chunk_index int,
            text text,
            embedding vector(768)
        );
        """)
    print("Postgres vector database initialized successfully.")


    # Imports test
    print("Can we make a numpy array?")
    np_zeros_test = np.zeros((3, 4))
    print(np_zeros_test)
    print("The answer is yes I think maybe, see above")


# Handle exceptions
except Exception as e:
    print(f"An unexpected error occurred: {e}")


# Keep container running (Docker container exists otherwise)
while True:
    print("sleeping...")
    time.sleep(30)