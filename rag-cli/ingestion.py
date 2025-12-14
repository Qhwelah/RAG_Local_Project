import json
import logging
import text_chunker

logger = logging.getLogger(__name__)

def ingest_data():
    data = ""
    try:
        with open("/data/web_pages.jsonl", 'r') as file:
            data = json.load(file)
    except Exception as e:
        logger.err(f"An error occurred while reading JSON file: {e}")
    logger.info("JSON data loaded successfully.")


    logger.info("Beginning chunking... ")

    logger.debug(data)

    #chunks = text_chunker.token_chunker(data)