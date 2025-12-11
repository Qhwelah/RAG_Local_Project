import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import deque
import json


BASE = "https://harrisburg.psu.edu/counseling-psychological-services"


def is_in_desired_subtree(url: str) -> str:
    return url.startswith(BASE)


def get_canonical_url(url: str) -> str:
    return url.split('#', 1)[0].split('?', 1)[0]


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Remove all non-content sections of the page
    for tag in soup(["header", "nav", "footer", "form", "script", "style", "noscript"]):
        tag.decompose()

    # Search for only 'main' content of page. If cannot find, just use the html 'body' tag
    main = (
        soup.find("main") or
        soup.find(attrs={"role": "main"}) or
        soup.body
    )

    if not main:
        return ""

    text = main.get_text(separator="\n", strip=True) 

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


    # main = soup.find(id="block-desired-content") or soup.body
    # return main.get_text(separator="\n", strip=True) if main else ""



def crawl_desired_tree():
    visited = set()
    queue = deque([BASE])
    results = []

    while queue:
        url = queue.popleft()
        url = get_canonical_url(url)

        # if site already visited, ignore it
        if url in visited:
            continue
        visited.add(url)

        print("Fetching", url)
        resp = ""
        try:
            resp = requests.get(url, timeout=10)
        
            if resp.status_code != 200:
                continue

            text = extract_text(resp.text)
            results.append({"url": url, "text": text})
            #print(f"Text from this page is: {text}\n")

            # Find all the linked urls in this page and push them to the queue
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.find_all("a", href=True):
                next_url = urljoin(url, a["href"])
                if is_in_desired_subtree(next_url) and next_url not in visited:
                    queue.append(next_url)

        except Exception as e:
            print(f"CAUGHT error: {e} \nContinuing:")
            continue

    with open("scraped_pages.jsonl", "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    crawl_desired_tree()