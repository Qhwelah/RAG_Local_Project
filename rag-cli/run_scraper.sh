#!/bin/bash
URL_LOCATION=$1
CACHE_LOCATION=$2

# If URL location is not set, use the container default set in docker-compose.yaml
if [ -z "$URL_LOCATION"]; then
    URL_LOCATION=$SCRAPE_URL
fi

# If a cache location is not provided, use a default name, and store in the bind mount.
if [ -z "$CACHE_LOCATION" ]; then
    CACHE_LOCATION="/data/web_pages.jsonl"
fi

# Run scraper program
cd /universal_crawler
echo "Scraping from root URL: '$1'"
scrapy crawl universal --loglevel=INFO -a base="$1" -a subtree=1 -O "web_pages.jsonl" 

# Copy the results into the persisting docker volume
cp web_pages.jsonl $CACHE_LOCATION
echo "Cached webpage content at $CACHE_LOCATION"