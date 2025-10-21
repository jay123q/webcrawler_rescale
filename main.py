import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import time
import webcrawler_ai
import webcrawler_person

# Example usage
if __name__ == "__main__":
    print('Hello world')
    crawler = webcrawler_person.WebCrawler(
        starter_url="https://docs.python.org/3/library/urllib.parse.html",
        delay=2
    )
    crawler.crawl()