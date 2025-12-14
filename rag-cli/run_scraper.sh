cd /universal_crawler
echo "Running website crawl..."
scrapy crawl universal --loglevel=INFO -a base=${SCRAPE_URL} -a subtree=1 -O "web_pages.jsonl" 

# Copy the results into the persisting docker volume
cp web_pages.jsonl /data/web_pages.jsonl