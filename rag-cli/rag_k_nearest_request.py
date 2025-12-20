from text_chunker import token_chunker
from chunk_embedder import embedder
from pgvector.psycopg import register_vector
from pgvector import Vector
import numpy as np
import psycopg
import logging, os

logger = logging.getLogger(__name__)

SENTENCE_TRANSFORMER_MODEL = "BAAI/bge-base-en-v1.5"
EMBEDDING_VECTOR_DIMENSIONS = 768
CHUNKER_MAX_TOKENS = 450
CHUNKER_TOKEN_OVERLAP = 75
ASSERT_TOKEN_MAX = 512

K_INITIAL = 8
K_FINAL = 4


def get_nearest_chunks(text, k=4):
    PGUSER = os.getenv("PGUSER")
    PGPASSWORD = os.getenv("PGPASSWORD")
    logger.debug(f"Variables are: PGUSER:{PGUSER}, PGPASSWORD:{PGPASSWORD}")


    # Connect to postgres service
    logger.info("Connecting to postgres vector database...")
    conn = psycopg.connect(f"host=pg dbname=rag user={PGUSER} password={PGPASSWORD}")

    with conn, conn.cursor() as cur:
        # Make sure this psql connection knows this is a vector DB
        register_vector(conn)

        # Chunk text input
        logger.info(f"Chunking user request...")
        chunks = token_chunker(text)
        all_chunks = []
        for chunk in chunks:
            completed_chunk = {}
            completed_chunk['doc_title'] = f'user_{len(all_chunks)+1}'
            completed_chunk['text'] = chunk

            all_chunks.append(completed_chunk)
        logger.info(f"Chunking complete!")

        # Embed chunks 
        logger.info(f"Embedding user input...")
        embedded_chunks = embedder(all_chunks, SENTENCE_TRANSFORMER_MODEL)
        logger.info(f"Embedding complete!")

        # Do K-nearest seach on those input chunks
        sql = f"""
        SELECT id, doc_id, doc_title, text, (embedding <=> %s::vector({EMBEDDING_VECTOR_DIMENSIONS})) AS score
            FROM embeddings_{EMBEDDING_VECTOR_DIMENSIONS}
            ORDER BY score
            LIMIT %s;
        """
        
        all_hits = []
        logger.info(f"Beginning PSQL distance search...")
        for qi in embedded_chunks:
            # Convert embedding from np vector to regular list
            emb = qi['embedding']
            if isinstance(emb, np.ndarray):
                emb = emb.astype(float).ravel().tolist()
            else:
                emb = list(emb)

            # Call actual sql query
            cur.execute(sql, (emb, K_INITIAL))
            all_hits.extend(cur.fetchall())
        logger.info(f"Distance search complete!\nFound {len(all_hits)} potential top entries.")


        # Get top K entries
        best_by_chunk_id = {}
        for row in all_hits:
            chunk_id = row[0]
            score = row[4]
            if chunk_id not in best_by_chunk_id or score < best_by_chunk_id[chunk_id][4]:
                best_by_chunk_id[chunk_id] = row

        final = sorted(best_by_chunk_id.values(), key=lambda r: r[4])[:K_FINAL]
        # final_dict = {}
        # for chunk in final:
        #     final_dict[chunk[0]] = {'id': chunk[0], 'url': chunk[1], 'text': chunk[2], 'score': chunk[3]}
        logger.info(f"\n{len(final)} closest context chunks are {final}")

        # Return text from K-nearest chunks
        logger.info(f"Returning closest chunks.")
        return final

# user_text = "I am a Penn State Harrisburg student. What phone numbers should I call if I'm feeling extremely depressed?"
# get_nearest_chunks(user_text)