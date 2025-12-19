from ollama import Client
import gradio as gr
import logging


DO_TOKEN_STREAM = None
HISTORY_REUSE_CAP = None
LLM_MODEL_NAME = None
OLLAMA_ADDRESS = None

logger = logging.getLogger(__name__)


# Create the chat interaction function
# This function is treated as a generator function in either case since the 'yield' keyword is present in it
def chat_fn(message, history):
    # Set up ollama interaction
    client = Client(host=OLLAMA_ADDRESS)
    

    # If there is a message history, append all of the messages together in a list
    messages = []

    logger.info(f"Current history is: {history}")

    # Have a parameter that limits the amount of messages fed back in during the history to save performance.
    # Iterate backwards through the history to ONLY take the most recent history items.
    for msg in reversed(history):
        if(len(messages) >= HISTORY_REUSE_CAP):
            break
        messages.append({"role": msg['role'], "content": msg['content'][0]['text']})
        #messages.append({"role": "assistant", "content": assistant_msg})


    # Do RAG retrieval of K closest context pieces, append that content to the messages history


    messages.append({'system': 'system', 'content': 'You are a concise assistant. User provided context or previous answers to respond to the user, if relevant. ' +
    'If you do not know some peice of information, just say you do not know, do NOT make up an answer.'})


    messages.reverse() # List is created backwards, so flip it forwards to maintain correct flow.
    # So the final order of messages is: System, Context, Chat history


    # Append the new message to the conversation
    messages.append({"role": "user", "content": message})
    logger.info(f"Finalized chat log to feed to bot is: {messages}")
    logging.info(f"User asks: {message}")


    full_response = ''
    if(DO_TOKEN_STREAM):
        stream = client.chat(
            model=LLM_MODEL_NAME,
            messages=messages,
            stream=True
        )

        full_response = ""
        for part in stream:
            # token = part['message']['content']
            token = part.message.content
            full_response += token
            yield full_response
        return # end generator function

    else:
        resp = client.chat(
            model=LLM_MODEL_NAME,
            messages=messages,
            stream=False
        )

        full_response = resp.message.content
        logging.info(f"Full LLM Response: {full_response}")
        yield full_response
        return # end generator function
    

# Create the interaction service, and host it on the specified port
def launch_LLM_interaction_service(server_name='0.0.0.0', port=7860, do_token_stream=False, history_reuse_cap=4,
                                   model_name='mistral', ollama_address='http://ollama:11434'):
    # Need to use the GLOBAL keyword to edit scriptwide variables
    global DO_TOKEN_STREAM
    global HISTORY_REUSE_CAP
    global LLM_MODEL_NAME
    global OLLAMA_ADDRESS
    
    DO_TOKEN_STREAM = do_token_stream
    HISTORY_REUSE_CAP = history_reuse_cap
    LLM_MODEL_NAME = model_name
    OLLAMA_ADDRESS = ollama_address

    
    gr.ChatInterface(
        fn=chat_fn,
        title=f"Local Ollama Chat ({"Streamed Reponse" if DO_TOKEN_STREAM else "Wait For Full Response"})",
    ).launch(server_name=server_name, server_port=port)


