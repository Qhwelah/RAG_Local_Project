from transformers import AutoTokenizer
import logging

SENTENCE_TRANSFORMER_MODEL = "BAAI/bge-base-en-v1.5"
CHUNKER_MAX_TOKENS = 450
CHUNKER_TOKEN_OVERLAP = 75
ASSERT_TOKEN_MAX = 512


logger = logging.getLogger(__name__)

tokenizer = AutoTokenizer.from_pretrained(
    SENTENCE_TRANSFORMER_MODEL,
    use_fast = True
)


# Chunker function, which is a token-based splitting function.
#  Uses the HuggingFace AutoTokenizer, which auto detects settings based on the embedding model you are using (see tokenizer declaration above).
def token_chunker(text: str, chunk_size: int = CHUNKER_MAX_TOKENS, chunk_overlap: int = CHUNKER_TOKEN_OVERLAP) -> list[str]:

    tokens = tokenizer.encode(text, add_special_tokens=False)

    step = max(1, chunk_size - chunk_overlap)
    chunks = []

    for i in range(0, len(tokens), step):
        chunk_tokens = tokens[i:i + chunk_size]
        chunk_text = tokenizer.decode(chunk_tokens, skip_special_tokens=True)
        chunks.append(chunk_text)

    longest_chunk = max([len(tokenizer.encode(chunk, add_special_tokens=True)) for chunk in chunks])
    logger.debug(f"Max chunk length for this doc is {longest_chunk}")
    assert longest_chunk <= ASSERT_TOKEN_MAX, f"All chunks must be less than or equal {ASSERT_TOKEN_MAX} tokens, but one was {longest_chunk} tokens."

    return chunks