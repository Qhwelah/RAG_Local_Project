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



- Once the postgres vectorized database is up and running with the Chunking and Embedding, I won't have to keep re-querying the website every time I start the container.
    - So when I get to that point, remove the auto-scraping script from the `startup.sh` bash script.
    - Could also just put the `caps_pages.jsonl` in a mounted volume for this container and call it a day.


## PostgreSQL database commands
- Inside of the pgvector container, do: `psql -U your_username -d your_database`
    - The database name for this network is `rag`
- You could also do `psql -U your_username` and use the following commands in the psql terminal:
    - `\q`: Quit the psql session and return to the Linux shell.
    - `\?`: Display help information about all available psql internal commands.
    - `\l`: List all available databases.
    - `\dt`: List tables in the current database.
    - `SELECT version();`: Execute an SQL query (must end with a semicolon ;) to check the PostgreSQL version. 
