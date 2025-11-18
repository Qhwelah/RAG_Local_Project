import psycopg
import numpy as np
from sentence_transformers import SentenceTransformer
import requests, sys
import os

PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")

conn = psycopg.connect(f"host=pg dbname=rag user={PGUSER} password={PGPASSWORD}")