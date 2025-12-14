import json
import logging
import text_chunker
from sentence_transformers import SentenceTransformer

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
    chunked_documents = []
    try:
        for document in data:
            url = document['url']
            title = document['title']

            chunks = text_chunker.token_chunker(document['text'])

            # Each individual chunk should have labelled which URl it was from and what the page title was 
            for chunk in chunks:
                completed_chunk = {}
                completed_chunk['doc_url'] = url
                completed_chunk['doc_title'] = title
                completed_chunk['text'] = chunk

                chunked_documents.append(completed_chunk)

    except Exception as e:
        logger.error(f"Error during chunking: {type(e)} - {e}")
        raise(e)
    
    # chunk_num = 0
    # for chunk in chunked_documents:
    #     logger.debug(f"Chunk {chunk_num}: {chunk}")
    #     chunk_num += 1

    logger.info("Chunking completed successfully!")


    # Embedding
    logger.info("Beginning embedding...")
    embedding_model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
    embedded_chunks = []
    chunk_index = 0

    try:
        for chunk in chunked_documents:
            ch_embedding = embedding_model.encode(chunk['text'])
            logger.debug(f"Chunk {chunk_index}: {chunk}\nEmbedding: {ch_embedding}\n")
            chunked_documents[chunk_index]['embedding'] = ch_embedding

            if(chunk_index < 3):
                logger.debug(f"Final chunk entry: {chunked_documents[chunk_index]}\n")

            chunk_index += 1
            
    except Exception as e:
        logger.error(f"Error during embedding chunk index #{chunk_index}: {type(e)} - {e}")
        raise(e)