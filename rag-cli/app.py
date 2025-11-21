import psycopg 
import numpy as np
from sentence_transformers import SentenceTransformer
import requests, sys, logging
import os, time

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    # Get environment variables
    PGUSER = os.getenv("PGUSER")
    PGPASSWORD = os.getenv("PGPASSWORD")
    logger.debug(f"Variables are: PGUSER:{PGUSER}, PGPASSWORD:{PGPASSWORD}")
    

    # Connect to postgres service
    logger.info("Initializing postgres vector database...")
    conn = psycopg.connect(f"host=pg dbname=rag user={PGUSER} password={PGPASSWORD}")
    with conn, conn.cursor() as cur:
        logger.info("Initializing vector extension...")
        cur.execute("""
        CREATE EXTENSION IF NOT EXISTS vector;
        """)
        
        time.sleep(2)

        logger.info("Initializing chunks table...")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS chunks(
            id bigserial PRIMARY KEY,
            doc_id text,
            chunk_index int,
            text text,
            embedding vector(768)
        );
        """)
    logger.info("Postgres vector database initialized successfully.")


# Handle exceptions
except Exception as e:
    logger.error(f"An unexpected error occurred: {e}")


# Keep container running (Docker container exists otherwise)
logger.debug("sleeping...")
while True:
    time.sleep(120)