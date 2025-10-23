import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import time
import webcrawler_ai
import webcrawler_person

# Example usage
if __name__ == "__main__":
    crawler = webcrawler_person.WebCrawler(
        # starter_url="https://docs.python.org/3/library/urllib.parse.html",
        # starter_url="https://www.geeksforgeeks.org/python/writing-csv-files-in-python",
        starter_url="https://www.python.org/psf/",
        delay=2
    )
    crawler.crawl()