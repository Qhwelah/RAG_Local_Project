FROM python:3.12

# Program Prerequisites
COPY requirements.txt .
RUN pip install -r requirements.txt

# Utilities
RUN apt-get update && apt-get install nano sudo -y

# Startup and Entry script
COPY . .
RUN chmod +x *.py && chmod +x *.sh

# Set up web scraper
RUN scrapy startproject universal_crawler
RUN mv universal_spider.py /universal_crawler/universal_crawler/spiders/universal_crawler.py 

# Run startup script, which includes scraping and db setup
#  Eventually will include full ingestion (chunking/embedding) and the ollama calls
CMD [ "bash", "startup.sh" ]