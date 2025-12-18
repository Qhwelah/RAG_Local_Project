import os, time, sys, logging, argparse, subprocess
import psycopg
from pgvector.psycopg import register_vector
from ollama import Client
import requests
import numpy as np

from ingestion import ingest_data
from ollama_chat import launch_LLM_interaction_service


## ========== Parameter settings ========== ##
# SENTENCE_TRANSFORMER_MODEL = "BAAI/bge-small-en-v1.5"
# EMBEDDING_VECTOR_DIMENSIONS = 384   #for BAAI/bge-small-en-v1.5

SENTENCE_TRANSFORMER_MODEL = "BAAI/bge-base-en-v1.5"
EMBEDDING_VECTOR_DIMENSIONS = 768   #for BAAI/bge-base-en-v1.5
## ======================================== ##

SCRAPE_CACHE_LOCATION="/data/web_pages.jsonl"

OLLAMA_MODEL="mistral"
OLLAMA_SERVICE_ADDRESS='http://ollama:11434'
STREAM_LLM_RESPONSE=False
CHAT_WINDOW_SERVER_NAME='0.0.0.0'
CHAT_WINDOW_SERVER_PORT=7860



# Set up argument processing
parser = argparse.ArgumentParser(description="A script that runs the RAG environment for the specified web domain.")
parser.add_argument('-i', '--do-ingestion', dest="do_ingestion", action='store_true', help='If passed, do ingestion (Chunk, Embed, populate PSQL). Clears previous PSQL db data.')
parser.add_argument('-s', '--scrape-url', dest="url_to_scrape", help='If passed with a valid URL root, program will scrape data from suburls of this domain.', required=False, default="")
args = parser.parse_args()


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
            doc_title text,
            text text,
            embedding vector({EMBEDDING_VECTOR_DIMENSIONS})
        );
        """)
        logger.info(f"Postgres chunk embeddings table 'embeddings_{EMBEDDING_VECTOR_DIMENSIONS}' initialized successfully.")


        # Initial file ingestion and context database filling
            # Scraping
                ## Scrape through a website tree of a specified URL, and return the text from the pages.
            
            # Chunking
                ## Pure hard character limit, or using tiktoken

            # Embedding
                ## Sentence Transformer (use model SENTENCE_TRANSFORMER_MODEL)


        # If the arg --scrape-url is passed with some value, run the URL scraping script with the set URL
        did_scraping = False
        if(len(args.url_to_scrape) > 0):
            logger.info(f"Running web scraper script on root URL '{args.url_to_scrape}'")
            try:
                subprocess.run(["bash", "run_scraper.sh", args.url_to_scrape, SCRAPE_CACHE_LOCATION])
                did_scraping = True
            except Exception as e:
                logger.error(f"Error during scraping: {type(e)} - {e}")
                raise(e)
            logger.info(f"URL scrape complete! Scrape data cached at '{SCRAPE_CACHE_LOCATION}'")


        # Only do ingestion process if the tag argument was passed to the script OR if the scrape script was run
        if(args.do_ingestion or did_scraping):
            # Take web data cached in JSON file, then chunk and embed it
            # Return a list of embedded chunks 
            embedded_chunks = ingest_data(transformer_model=SENTENCE_TRANSFORMER_MODEL)


            # Clear all previous entries in the PSQL table
            logger.info(f"Clearing all previous chunks from RAG knowledge base 'embeddings_{EMBEDDING_VECTOR_DIMENSIONS}...")
            cur.execute(f"TRUNCATE TABLE embeddings_{EMBEDDING_VECTOR_DIMENSIONS} RESTART IDENTITY;")
            cur.execute(f"SELECT COUNT(*) FROM embeddings_{EMBEDDING_VECTOR_DIMENSIONS};")
            logger.info(f"Cleared! Currently there are {cur.fetchone()} entries in the db.")


            # Push embedded chunks to PostgreSQL database
            logger.info(f"Preparing chunks for refilling the database...")
            register_vector(conn)

            sql = f"""
            INSERT INTO embeddings_{EMBEDDING_VECTOR_DIMENSIONS} (doc_id, doc_title, text, embedding)
            VALUES (%s, %s, %s, %s)
            """
            rows = []
            for chunk in embedded_chunks:
                #chunk_entry = embedded_chunks[chunk]
                emb = chunk['embedding']
                if isinstance(emb, np.ndarray):
                    emb = emb.astype(float).ravel().tolist()
                else:
                    emb = list(emb)

                rows.append((chunk['doc_url'], chunk['doc_title'], chunk['text'], emb))

            logger.info(f"Inserting {len(rows)} into table 'embeddings_{EMBEDDING_VECTOR_DIMENSIONS}'")
            cur.executemany(sql, rows)
            logger.info(f"Successfully inserted {len(rows)} entries into the knowledge db!")

            # cur.execute(f"""
            # INSERT INTO embeddings_{EMBEDDING_VECTOR_DIMENSIONS} (doc_id, doc_title, text, embedding)
            #     VALUES ('{chunk['doc_url']}', '{chunk['doc_title']}', '{chunk['text']}', '{chunk['embedding']}');
            # """)




        # Connect to ollama
            ## r = requests.post("http://ollama:11434/api/generate", json={"model": model, "prompt": prompt, "stream": False})
        logger.info(f"Launching LLM interaction service at {CHAT_WINDOW_SERVER_NAME}:{CHAT_WINDOW_SERVER_PORT} \
                     {'using' if STREAM_LLM_RESPONSE else 'without using'} live token stream.")

        launch_LLM_interaction_service(
            server_name=CHAT_WINDOW_SERVER_NAME,
            port=CHAT_WINDOW_SERVER_PORT,
            do_token_stream=STREAM_LLM_RESPONSE,
            model_name=OLLAMA_MODEL,
            ollama_address=OLLAMA_SERVICE_ADDRESS
        )

        logger.info(f"LLM interaction service launched successfully!")
        
        # client = Client(host="http://ollama:11434")
        # messages = [
        #     {'role': 'system', 'content': 'You are a concise assistant.'},
        #     {'role': 'user', 'content': 'Explain how Mars Transfer windows work in one paragraph.'},
        # ]
        # logger.info(f"Requesting LLM the following prompt: {messages[1]['content']}")

        # if(STREAM_LLM_RESPONSE):
        #     # For printing out tokens one at a time as they arrive
        #     logger.info(f"Printing out tokens as they arrive...")
        #     start_time = time.perf_counter()
        #     #response = ""
        #     for chunk in client.chat(model=f'{OLLAMA_MODEL}', messages=messages, stream=True):
        #         #response += chunk
        #         print(chunk['message']['content'], end='', flush=True)
        #     end_time = time.perf_counter()
        #     print()
        #     logger.info(f"Generated for {(end_time-start_time):.4f} seconds.")
        
        # else:
        #     # For one-chunk responses
        #     logger.info(f"Waiting for all tokens before printing out response.")
        #     start_time = time.perf_counter()
        #     resp = client.chat(model=f'{OLLAMA_MODEL}', messages=messages)
        #     end_time = time.perf_counter()
        #     logger.info(f"Generated for {(end_time-start_time):.4f} seconds.\nFull LLM Response: {resp['message']['content']}")



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
    logger.error(f"An unexpected error occurred: {type(e)} - {e}")


# Keep container running (Docker container exists otherwise)
logger.info("sleeping...")
while True:
    time.sleep(120)