import scrapy
from bs4 import BeautifulSoup
from urllib.parse import urldefrag, urlsplit, urlunsplit

REMOVE_TAGS = ["header", "nav", "footer", "aside", "form", "script", "style", "noscript"]
SKIP_EXTENSIONS = (".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".zip", ".mp4", ".mp3")
MIN_TEXT_LEN = 150  

def canonical_url(url: str) -> str:
    url, _frag = urldefrag(url)
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def normalize_text(text: str) -> str:
    # Collapse repeated blank lines and trim lines
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines)


def extract_main_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Remove all non-content sections of the page
    for tag in soup(REMOVE_TAGS):
        tag.decompose()

    # If there is a "main" tag of some kind
    semantic = soup.find("main") or soup.find("article")
    if semantic:
        text = semantic.get_text(separator="\n", strip=True)
        if text and len(text) > MIN_TEXT_LEN:
            return normalize_text(text)
    
    # Else If there is a div tag with some sort of main content section
    cms_candidates = [
        soup.select_one("div#content"),
        soup.select_one("div#main-content"),
        soup.select_one("main#main-content"),
        soup.select_one("div.content"),
        soup.select_one("div.entry-content"),
        soup.select_one("div.post-content"),
        soup.select_one("div.node__content"),
    ]
    for c in cms_candidates:
        if c:
            text = c.get_text(separator="\n", strip=True)
            if text and len(text) > MIN_TEXT_LEN:
                return normalize_text(text)
    
    # Else, just split everything apart by newlines.
    if soup.body:
        text = soup.body.get_text(separator="\n", strip=True)
        return normalize_text(text)

    return ""


class UniversalSpider(scrapy.Spider):
    """
    Usage:
        scrapy crawl universal -a base=https://example.com/some/path
        scrapy crawl universal -a base=https://example.com -a subtree=0
        scrapy crawl universal -a base=https://example.com/docs -O "output_file.jsonl"

    'Base' is the url to start the web crawl at.

    `Subtree` tells the crawler to either limit searched of that domain to:
        1 -> only those under the FULL specified `base` subdomain (example.com/some/path)
        0 -> to ANY url with the same ROOT domain name (example.com)

    -O denotes the jsonl file name to export data to.
    """

    name = "universal"

    def __init__(self, base=None, subtree="1", *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not base:
            raise ValueError("You must pass -a base=<url>")
        
        self.base = canonical_url(base.strip())
        self.subtree_only = str(subtree).lower() not in ("0", "false", "no")

        host = urlsplit(self.base).netloc
        self.allowed_domains = [host]

        self.start_urls = [self.base]

        self.custom_settings = {
            "DOWNLOAD_DELAY": 0.5,
            "AUTOTHROTTLE_ENABLED": True,
        }


    def in_scope(self, url: str) -> bool:
        u = canonical_url(url)

        if urlsplit(u).netloc != urlsplit(self.base).netloc:
            return False
        
        if self.subtree_only and not u.startswith(self.base):
            return False
        
        return True
    

    # Checking that the file specified is a text file, and is part of the url tree we want
    def should_follow(self, url: str) -> bool:
        u = canonical_url(url)

        if not (u.startswith("http://") or u.startswith("https://")):
            return False
        
        # Skip non-pages
        if u.lower().endswith(SKIP_EXTENSIONS):
            return False
        
        # Skip outside subtree
        return self.in_scope(u)
    

    def parse(self, response):
        page_url = canonical_url(response.url)

        # extract text
        text = extract_main_text(response.text)

        # Extract readable text using BeautifulSoup as a quick pass
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else ""

        yield {
            "url": page_url,
            "title": title,
            "text": text,
        }

        for href in response.css("a::attr(href)").getall():
            if not href:
                continue

            h = href.strip().lower()
            if h.startswith(("mailto:", "tel:", "javascript:")):
                continue

            next_url = response.urljoin(href)
            if self.should_follow(next_url):
                yield scrapy.Request(canonical_url(next_url), callback=self.parse)