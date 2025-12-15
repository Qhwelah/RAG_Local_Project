#!/bin/bash

# Start Ollama in the background, capture process id
/bin/ollama serve &
pid=$!

# Wait for service to be active
echo "Waiting for ollama service to be active..."
while ! ollama list | grep -q 'NAME'; do
    sleep 1
done
echo "Ollama service is running."

# Pull model
echo "Pulling model $LLM_MODEL from Ollama..."
ollama pull $LLM_MODEL
echo "Done pulling $LLM_MODEL!"

# Wait for background Ollama process to close... 
# (keep container open until Ollama stops) 
wait $pid