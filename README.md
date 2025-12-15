# Locally Hosted RAG LLM Project
### Created initially for COMP 519 - Advanced Datastructures

## Startup
- Create `.env` file:
```.env
# Postgres
POSTGRES_USER = postgres 
POSTGRES_PASSWORD = devpassword

# URL to pull information from in the Web Scraper
SCRAPE_URL = "https://harrisburg.psu.edu/counseling-psychological-services"

# LLM Model to pull in Ollama for RAG generation
LLM_MODEL = mistral
```

- cd into project directory

- Run docker compose startup command:
    - `docker compose up --build`

- To stop the docker environment and delete the containers, do:
    - Control+C to cancel the docker run
    - `Docker compose down` to delete the containers

- The client container `rag-cli`'s main running script, `app.py`, is configured to allow parameters to be fed in for specific behaviors.
    - `-i` or `--do-ingestion`, if present, will tell the script to take the cached web scraping data, and chunk, embed, and push the data to the RAG database (which will also be cleared beforehand)
    - `-s` or `--scrape-url` with a string url like `ttps://harrisburg.psu.edu/counseling-psychological-services` will tell the program to scrape data from the website specified and all subdomains, and also run the ingestion process described above with the new data. 
    - Currently the only way to feed in these flags is from inside the `rag-cli` container, but that will be resolved later on in development.


## PostgreSQL database commands
- Inside of the pgvector container, do: `psql -U your_username -d your_database`
    - The database name for this network is `rag`
- You could also do `psql -U your_username` and use the following commands in the psql terminal:
    - `\q`: Quit the psql session and return to the Linux shell.
    - `\?`: Display help information about all available psql internal commands.
    - `\l`: List all available databases.
    - `\dt`: List tables in the current database.
    - `SELECT version();`: Execute an SQL query (must end with a semicolon ;) to check the PostgreSQL version. 
