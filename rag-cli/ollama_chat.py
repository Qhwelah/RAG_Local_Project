from ollama import Client
import gradio as gr
import logging


DO_TOKEN_STREAM = None
LLM_MODEL_NAME = None
OLLAMA_ADDRESS = None

logger = logging.getLogger(__name__)


# Create the chat interaction function, 
def chat_fn(message, history):
    # Set up ollama interaction
    client = Client(host=OLLAMA_ADDRESS)
    

    # If there is a message history, append all of the messages together in a list
    messages = []

    logger.info(f"Current history is: {history}")

    for user_msg, assistant_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})


    # Append the new message to the conversation
    messages.append({"role": "user", "content": message})
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

    else:
        resp = client.chat(
            model=LLM_MODEL_NAME,
            messages=messages,
            stream=False
        )

        full_response = resp.message.content
        return full_response
    
    logging.info(f"Full LLM Response: {full_response}")
    

# Create the interaction service, and host it on the specified port
def launch_LLM_interaction_service(server_name='0.0.0.0', port=7860, do_token_stream=False, model_name='mistral', ollama_address='http://ollama:11434'):
    # Need to use the GLOBAL keyword to edit scriptwide variables
    global DO_TOKEN_STREAM
    global LLM_MODEL_NAME
    global OLLAMA_ADDRESS
    
    DO_TOKEN_STREAM = do_token_stream
    LLM_MODEL_NAME = model_name
    OLLAMA_ADDRESS = ollama_address

    
    gr.ChatInterface(
        fn=chat_fn,
        title=f"Local Ollama Chat ({"Streamed Reponse" if DO_TOKEN_STREAM else "Wait For Full Response"})",
    ).launch(server_name=server_name, server_port=port)


