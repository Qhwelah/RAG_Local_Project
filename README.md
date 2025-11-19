# Locally Hosted RAG LLM Project
### Created initially for COMP 519 - Advanced Datastructures

## Startup
- Create `.env` file:
```.env
# Postgres
POSTGRES_USER = postgres 
POSTGRES_PASSWORD = devpassword
```

- cd into project directory

- Run docker compose startup command:
    - `docker compose up --build`

- To stop the docker environment and delete the containers, do:
    - Control+C to cancel the docker run
    - `Docker compose down` to delete the containers