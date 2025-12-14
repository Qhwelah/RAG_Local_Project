import logging
import numpy as np
from sentence_transformers import SentenceTransformer


logger = logging.getLogger(__name__)

def embedder(all_chunks, transformer_model):
    # Return empty array if no chunks inputted
    if(len(all_chunks) <= 0):
        return []


    # Set up embedding model with specified model
    embedding_model = SentenceTransformer(transformer_model)


    # Create an array of text to embed
    text_to_embed = []
    for i in range(0, len(all_chunks)):
        text_to_embed.append(all_chunks[i]['text'])

    assert len(text_to_embed) == len(all_chunks), f"Length of text_to_embed is {len(text_to_embed)} but there are {len(all_chunks)} chunks in all_chunks"


    # Embed/vectorize all text
    logger.info(f"Embedding {len(text_to_embed)} chunks...")
    text_embedding = embedding_model.encode(text_to_embed)
    logger.info(f"Finished embedding {len(text_embedding)} chunks!")


    # Check there are the correct amount of embeddings
    assert(len(all_chunks) == len(text_to_embed)), f"There are {len(text_to_embed)} chunks to embed, but {len(text_embedding)} embeddings."


    # Assign all embeddings to their relevant chunks
    for i in range(0, len(all_chunks)):
        logger.debug(f"Chunk {i}: {all_chunks[i]}\nEmbedding first four dimensions: {text_embedding[i][0:4]}\n")
        all_chunks[i]['embedding'] = text_embedding[i]


    return(all_chunks)