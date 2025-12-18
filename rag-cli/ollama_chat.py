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
    for user_msg, assistant_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})


    # Append the new message to the conversation
    messages.append({"role": "user", "content": message})


    if(DO_TOKEN_STREAM):
        pass
    else:
        resp = client.chat(
            model=LLM_MODEL_NAME,
            messages=messages,
            stream=False
        )

        return resp.message.content
    

# Create the interaction service, and host it on the specified port
def launch_LLM_interaction_service(server_name='0.0.0.0', port=7860, do_token_stream=False, model_name='mistral', ollama_address='http://ollama:11434'):
    DO_TOKEN_STREAM = do_token_stream
    LLM_MODEL_NAME = model_name
    OLLAMA_ADDRESS = ollama_address

    logger.info(f"Launching LLM interaction service at {server_name}:{port} {'using' if DO_TOKEN_STREAM else 'witnout using'} live token stream.")

    
    gr.ChatInterface(
        fn=chat_fn,
        title="Local Ollama Chat (Client SDK)",
    ).launch(server_name=server_name, server_port=port)


