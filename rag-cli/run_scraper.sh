cd /universal
echo "Running website crawl..."
scrapy crawl universal --loglevel=INFO -a base="https://harrisburg.psu.edu/counseling-psychological-services" -a subtree=1 -O "web_pages.jsonl" 

# Copy the results into the persisting docker volume
cp web_pages.jsonl /data/web_pages.jsonl