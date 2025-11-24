
# Define chunker
## Pure hard character limit, or using tiktoken
def chunker(text, max_tokens=800, overlap=120):
    # This is the full python, text-insensitive loop. 800 characters per 
    return text