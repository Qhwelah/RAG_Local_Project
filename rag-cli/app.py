import psycopg 
import numpy as np
from sentence_transformers import SentenceTransformer
import requests, sys, logging
import os, time
from text_chunker import chunker


## ========== Parameter settings ========== ##
SENTENCE_TRANSFORMER_MODEL = "BAAI/bge-small-en-v1.5"
EMBEDDING_VECTOR_DIMENSIONS = 384   #for BAAI/bge-small-en-v1.5

# SENTENCE_TRANSFORMER_MODEL = "BAAI/bge-base-en-v1.5"
# EMBEDDING_VECTOR_DIMENSIONS = 768   #for BAAI/bge-base-en-v1.5
## ======================================== ##


# Configure logger
## Logging to log file in volume
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='/data/rag_service.log',
    filemode="w"
)

## Logging to console
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger('').addHandler(console_handler)

logger = logging.getLogger(__name__)


# Begin service setup
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

        logger.info("Initializing chunks embedding table...")
        logger.info(f"Using {EMBEDDING_VECTOR_DIMENSIONS} dimensions for the vector embeddings.")
        # Make sure the vector dimensions number matches that of the model you are calling
        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS embeddings_{EMBEDDING_VECTOR_DIMENSIONS}(
            id bigserial PRIMARY KEY,
            doc_id text,
            chunk_index int,
            text text,
            embedding vector({EMBEDDING_VECTOR_DIMENSIONS})
        );
        """)
    logger.info(f"Postgres chunk embeddings table 'embeddings_{EMBEDDING_VECTOR_DIMENSIONS}' initialized successfully.")

    # Initial file ingestion and context database filling
        # Chunking
            ## Pure hard character limit, or using tiktoken

        # Embedding
            ## Sentence Transformer (use model SENTENCE_TRANSFORMER_MODEL)


    # Connect to ollama
        ## r = requests.post("http://ollama:11434/api/generate", json={"model": model, "prompt": prompt, "stream": False})

    # LLM call loop
        # Wait for user input
            ## External text editor perhaps, or multiline text entry
            ## See `user_prompt_input.py`

        # Chunk and vectorize the user's input
            ## Same chunking and embedding functions from above

        # Call psql vector distance comparison
            ## Using <-> operator to find vector distances
            ## "Retrieval"

        # With the k closest results of the vector search prepended, call the LLM model
            ## Prompt: "Use the context to answer.\n\nContext:\n{ctx}\n\nQuestion: {q}\nAnswer:"
            ## "Augmented Generation"
        
        # Print out the model's response to the user
            ## answer = ollama_generate(prompt)
            ## print(answer)
        
        # Repeat  




# Handle exceptions
except Exception as e:
    logger.error(f"An unexpected error occurred: {e}")


# Keep container running (Docker container exists otherwise)
logger.info("sleeping...")
while True:
    time.sleep(120)