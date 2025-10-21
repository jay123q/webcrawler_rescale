from bs4 import BeautifulSoup #https://www.crummy.com/software/BeautifulSoup/bs4/doc/#translating-this-documentation
from urllib.parse import urljoin, urlparse #https://docs.python.org/3/library/urllib.parse.html
import urllib.robotparser as rp #https://docs.python.org/3/library/urllib.robotparser.html
from collections import deque #https://www.geeksforgeeks.org/python/queue-in-python
import requests as req # https://pypi.org/project/requests
import time

class WebCrawler:
    def __init__( self, starter_url:str , delay:int ):
        """
        We are going to take in the 'start_url' and some default parameters for delay, later, I will swap out the delay here if there is something in 'robots.txt'

        Args:
            start_url -> parse the query, fragment, path, params out of the domain name ( urllib parse )
            delay -> time sleep to avoid overloading servers

`       Things done:
            csv -> created to log the domains we have been to and what happened and how many href its happened
            domains_visted -> set of places we have been, using a SET to avoid dups
            self.headers -> idenity myself as a agent
        """

        self.starter_url = starter_url

        #TODO validate the data for delay using robots.txt

        #self.max_pages = 100 # hard stop at 100 hrefs queried
        self.delay = delay

        self.list_domains_to_visit = [] #TODO add a parser
        self.list_domains_to_visit.append(starter_url)
        
        self.q_domains_to_visit = deque(self.list_domains_to_visit)

        #set up self of domains to visit
        self.domains_visited = set()

        #set up CSV metrics to view, defaulting to no for robots
        self.metrics = {"site":starter_url,"total_links_on_page":0, "status_code":200}
        self.list_domains_to_visit = []

        # Current Domain name use this to valiate later the subdomain!
        self.urlParsedintoPieces = urlparse(self.starter_url)
        
        '''
        https://docs.python.org/3/library/urllib.parse.html
        urlparse("scheme://netloc/path;parameters?query#fragment")
        ParseResult(scheme='scheme', netloc='netloc', path='/path;parameters', params='',
                    query='query', fragment='fragment')
        o = urlparse("http://docs.python.org:80/3/library/urllib.parse.html?"
                    "highlight=params#url-parsing")
        o
        ParseResult(scheme='http', netloc='docs.python.org:80',
                    path='/3/library/urllib.parse.html', params='',
                    query='highlight=params', fragment='url-parsing')
        '''

        #identify robots
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }


        return None

    def robots_validate( self ):
        '''
        This is a strech function, it will be used if we are going to validate the delay, or the URL that we cannot crawl in robots.txt
        '''
        return None

    def fetch_page( self, url:str ):
        """
        We are going to use the 'requests' library to get if we can access this data
        Fetch a single page.
        """
        print("fetching url ", url )
        try:
            response = req.get( url, headers=self.headers, timeout=10 )
            response.status_code
            '''
            https://requests.readthedocs.io/en/latest
            r = requests.get('https://api.github.com/user', auth=('user', 'pass'))
            r.status_code
            200
            r.headers['content-type']
            'application/json; charset=utf8'
            r.encoding
            'utf-8'
            r.text
            '{"type":"User"...'
            r.json()
            {'private_gists': 419, 'total_private_repos': 77, ...}
            '''
            return response.text,response.status_code
        except req.RequestException as e:
            print("Error fetching "+ url+ " : ", e , " ")
            return None,response.status_code

    def process_page(self, url:str ):
        '''
        process page
            -> first handle metrics
            -> second we are going to fetch the URL and get the status code
            
        '''
        url_response_text, status_code_for_fetch_page = self.fetch_page( url )

        self.metrics["site"] = url

        #TODO STRECH check robots.txt if we are allowed to parse the URL here
        # self.metrics["Allowed to Parse?"] = url

        self.metrics["status_code"] = status_code_for_fetch_page
        
        if status_code_for_fetch_page == None:
            return None
        
        soup = BeautifulSoup(url_response_text,'html.parser')

        #TODO validate the subdomains somewhere in here, and add a error message to metrics
        #TODO enque the new hrefs found in the soup
        #TODO count the number of total links found
        print(soup)

        # to filter on soup, we are going to use the 'find_all' command
        '''
        # <p class="story">Once upon a time there were three little sisters; and their names were
        #  <a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>,
        #  <a class="sister" href="http://example.com/lacie" id="link2">Lacie</a> and
        #  <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>;
        #  and they lived at the bottom of a well.</p>
        '''
        # i think we can also use the sieve filter / select filter
        # [tag['id'] for tag in soup.css.iselect(".sister")]



        

        

    def crawl( self ):
        """
        Setting up main while loop and driver here

        we will be checking if the queues length is 0 of set_domains_to_vist since if its empty, everything must be in list_domains_to_vist
        """

        while( len( self.q_domains_to_visit ) > 0 ):
            curr_url = self.q_domains_to_visit.popleft()
            
            #TODO STRECH validate this domain in the URL / input the issue with it the metrics

            if curr_url in self.domains_visited:
                # if we have seen this URL before, leave it
                continue
            
            print(" we are working on URL ", curr_url )
            self.process_page( curr_url )

            print("sleeping for ", self.delay, " seconds ")
            time.sleep(self.delay)


        print( "done crawling! ") 
        return None


            
    

