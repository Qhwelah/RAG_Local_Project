import json
import logging
import numpy as np
from  text_chunker import token_chunker
from chunk_embedder import embedder

SENTENCE_TRANSFORMER_MODEL = "BAAI/bge-base-en-v1.5"

logger = logging.getLogger(__name__)

def ingest_data():
    # Pull data from cached data (from last scrape)
    data = []
    try:
        with open("/data/web_pages.jsonl", 'r') as file:
            for line in file:
                json_obj = json.loads(line.strip())
                data.append(json_obj)
    except Exception as e:
        logger.error(f"An error occurred while reading JSON file: {e}")
        raise(e)
    logger.info("JSON data loaded successfully.")


    logger.debug(f"Input data to chunk: {data}")


    # Chunking
    logger.info("Beginning chunking... ")
    all_chunks = []
    try:
        for document in data:
            url = document['url']
            title = document['title']

            chunks = token_chunker(document['text'])

            # Each individual chunk should have labelled which URl it was from and what the page title was 
            for chunk in chunks:
                completed_chunk = {}
                completed_chunk['doc_url'] = url
                completed_chunk['doc_title'] = title
                completed_chunk['text'] = chunk

                all_chunks.append(completed_chunk)

    except Exception as e:
        logger.error(f"Error during chunking: {type(e)} - {e}")
        raise(e)

    logger.info("Chunking completed successfully!")


    # Embedding
    logger.info("Beginning embedding...")
    try:
        embedded_chunks = embedder(all_chunks=all_chunks, transformer_model=SENTENCE_TRANSFORMER_MODEL)

        logger.debug(f"First embedded chunk: {embedded_chunks[0] if len(embedded_chunks) > 0 else []}")

    except Exception as e:
        logger.error(f"Error during embedding chunks: {type(e)} - {e}")
        raise(e)

    logger.info("Embedding completed successfully!")