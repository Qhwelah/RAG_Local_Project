import json
import logging
import text_chunker

logger = logging.getLogger(__name__)

def ingest_data():
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
    
    logger.info("Chunking completed successfully!")
    
    chunk_num = 1
    for chunk in chunked_documents:
        logger.debug(f"Chunk {chunk_num}: {chunk}")
        chunk_num += 1