import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import deque
import json

BASE = "https://harrisburg.psu.edu/counseling-psychological-services"

def is_in_desired_subtree(url: str) -> str:
    url = url.split('#', 1)[0].split('?', 1)[0]
    return url.startswith(BASE)

def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find(id="block-desired-content") or soup.body
    return main.get_text(separator="\n", strip=True) if main else ""

def crawl_desired_tree():
    visited = set()
    queue = deque([BASE])
    results = []

    while queue:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)

        print("Fetching", url)
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            continue

        text = extract_text(resp.text)
        results.append({"url": url, "text": text})

        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            next_url = urljoin(url, a["href"])
            if is_in_desired_subtree(next_url) and next_url not in visited:
                queue.append(next_url)

    with open("scraped_pages.jsonl", "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    crawl_desired_tree()