import scrapy
from bs4 import BeautifulSoup

## SET BASE URL BEFORE FEEDING IN SCRIPT!
## This script can also be modified to be generalized away from Penn State, but to get a Min Viable Product up and running, I am using this.

BASE = "https://harrisburg.psu.edu/counseling-psychological-services"

class CapsSpider(scrapy.Spider):
    name = "caps_crawler"
    allowed_domains = ["harrisburg.psu.edu"]
    start_urls = [BASE]

    custom_settings = {
        "DOWNLOAD_DELAY": 0.5,
        "AUTOTHROTTLE_ENABLED": True,
        "FEEDS": {
            "caps_pages.jsonl": {
                "format": "jsonlines",
                "encoding": "utf8",
                "overwrite": True,
            }
        },
    }

    def is_in_caps_subtree(self, url: str) -> bool:
        url = url.split('#', 1)[0].split('?', 1)[0]
        return url.startswith(BASE)

    def parse(self, response):
        # Extract readable text using BeautifulSoup as a quick pass
        soup = BeautifulSoup(response.text, "html.parser")

        main = soup.find(id="block-pennstate-content") or soup.body

        text = main.get_text(separator="\n", strip=True) if main else ""

        yield {
            "url": response.url,
            "title": soup.title.string.strip() if soup.title else "",
            "text": text,
        }


        # Follow links within subtree
        for href in response.css("a::attr(href)").getall():
            next_url = response.urljoin(href)
            if self.is_in_caps_subtree(next_url):
                yield scrapy.Request(next_url, callback=self.parse)