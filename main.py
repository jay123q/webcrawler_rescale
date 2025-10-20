import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import time

class WebCrawler:
    def __init__(self, start_url, max_pages=50, delay=1):
        """
        Initialize the web crawler.
        
        Args:
            start_url: URL to start crawling from
            max_pages: Maximum number of pages to crawl
            delay: Delay between requests in seconds (be respectful!)
        """
        self.start_url = start_url
        self.max_pages = max_pages
        self.delay = delay
        self.visited = set()
        self.to_visit = deque([start_url])
        self.domain = urlparse(start_url).netloc
        
        # Set a user agent to identify your crawler
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def is_valid_url(self, url):
        """Check if URL belongs to the same domain."""
        try:
            parsed = urlparse(url)
            return parsed.netloc == self.domain
        except:
            return False
    
    def get_links(self, url, html):
        """Extract all links from HTML content."""
        links = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(url, link['href'])
                # Remove fragments
                absolute_url = absolute_url.split('#')[0]
                if self.is_valid_url(absolute_url) and absolute_url not in self.visited:
                    links.append(absolute_url)
        except Exception as e:
            print(f"Error parsing links from {url}: {e}")
        return links
    
    def fetch_page(self, url):
        """Fetch a single page."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def process_page(self, url, html):
        """
        Process the fetched page. Override this method to extract data.
        """
        print(f"Crawled: {url}")
    
    def crawl(self):
        """Main crawling loop."""
        while self.to_visit and len(self.visited) < self.max_pages:
            url = self.to_visit.popleft()
            
            if url in self.visited:
                continue
            
            print(f"Visiting ({len(self.visited) + 1}/{self.max_pages}): {url}")
            self.visited.add(url)
            
            # Fetch the page
            html = self.fetch_page(url)
            if html is None:
                continue
            
            # Process the page
            self.process_page(url, html)
            
            # Extract and queue new links
            new_links = self.get_links(url, html)
            self.to_visit.extend(new_links)
            
            # Be respectful to the server
            time.sleep(self.delay)
        
        print(f"\nCrawling complete. Total pages visited: {len(self.visited)}")


# Example usage
if __name__ == "__main__":
    crawler = WebCrawler(
        start_url="https://example.com",
        max_pages=10,
        delay=2
    )
    crawler.crawl()