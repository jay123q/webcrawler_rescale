from bs4 import BeautifulSoup #https://www.crummy.com/software/BeautifulSoup/bs4/doc/#translating-this-documentation
from urllib.parse import urljoin, urlparse #https://docs.python.org/3/library/urllib.parse.html
import urllib.robotparser #https://docs.python.org/3/library/urllib.robotparser.html
from collections import deque #https://www.geeksforgeeks.org/python/queue-in-python
import requests as req # https://pypi.org/project/requests
import time
import csv # used for metrics https://www.geeksforgeeks.org/python/writing-csv-files-in-python

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
            robots_hostname -> to avoid re-calling for robots.txt if the hostname say 'geeks_for_geeks' is the same
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
        self.metrics = [
           # {"site":starter_url,"total_links_on_page":0, "status_code":0}
        ]


        self.max_url_hard_stop = 5

        #identify robots
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        self.robots_hostname = ""
        self.robots_url = ""

        self.rp = urllib.robotparser.RobotFileParser()

        return None

    def robots_populator( self, url ):
        '''
        We are going to play nice with the server, we are going to validate if we can_fetch the current page we are on and check it against the other
        https://docs.python.org/3/library/urllib.robotparser.html


        Args:
            URL -> used to pull out the DNS name, and check to see if the DNS / hostname is different from the one stored, if it is we will update the robots_url storage as well

        Things done:
            We parsed the URL, and created the https://hostname/robots.txt, we will store the URL and the host name for later use in the validation function
            
            We checked if robots.txt contains a crawler delay, and if it does, we update our sleep parameter

        '''
        print( "Robots running! ")
        
        # https://docs.python.org/3/library/urllib.parse.html#url-parsing-security
        url_pieces = urlparse(url)

        if self.robots_hostname == url_pieces.hostname:
            # no change to the host name, do not re-execute
            print( " no change to the hostname, do not execute a new robots.txt call! ")
            return None

        robots_url = url_pieces.scheme + "://" # set up the basics for a robot request
        
        robots_url += url_pieces.hostname + '/robots.txt'

        # removing this right now, and testing if we can just grab the hostname directly
        # if url_pieces.netloc != '':
        #     # if netloc is empty, then we need to split on the path and take the first parameter
        #     path_parts = url_pieces.split('/')
        #     DNS_name = path_parts.at(0)
        #     robots_url += DNS_name + '/robots.txt'

        # else:
        #     # some logic to remove 80 / the port, and then preform the same addition
        
        print(" the created robots URL is ", robots_url )

        self.robots_url = robots_url
        self.robots_hostname = url_pieces.hostname

        self.rp.set_url(self.robots_url)
        self.rp.read()
        

        if self.rp.crawl_delay("*") != None:
            self.delay = self.rp.crawl_delay("*")


        

        return None

    def fetch_page( self, url:str ):
        """
        We are going to use the 'requests' library to get if we can access this data
                
        If we can, then we are going to fetch a single page, and pass the TXT to process_page so it can html via bs4

        Args:
            URL -> used validate if we can 'get' request the object, and if so, take the TXT and pass it into BS4

        Things done:
            if the page does not respond, assume it was a 404 ( likely could do some other err )

            if the page does respond take the status code and the response.txt and pass it onward

        """
        print("fetching url ", url )
        try:
            response = req.get( url, headers=self.headers, timeout=10 )
            response.raise_for_status()
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
            #TODO work on a better method of error handling and finding the right status code here, this will bother me

            print("Error fetching "+ url+ " : ", e , " , returning status code 504")
            return None,504
        
    def validate_url(self, url:str ):
        '''
        This function will validate the inputed URL in the parameter, and it will then decide if it should be enqued or thrown out
        
        STRECH, validate the robots.txt of the new page as well

        Args:
            URL -> used to check if the URL cleaned up, existrs in the domains_visited set

        Things done:
            #check if the url exists in the set
            #check if we can_fetch the link using the stored robots.txt value


        #TODO add support for Robots.txt if its in the can_fetch
        '''
        print()
        print()
        print("WARNING, YOU ARE VALIDATING HOSTNAME ", self.robots_populator, " against a URL that might not share the same name ", url )
        print(" we likely need to either stop going out of bounds on the same hostname, or have a if statement to catch this ")
        print()
        print()


        if self.rp.can_fetch("*",url) == False:
            print("robots has fetched that we cannot fetch this URL ", url )

            return False


        if url in self.domains_visited:
            return False
        
        return True

    def process_page(self, url:str ):
        '''
        make the actual get request for the page, and then handle its URL

        process page
            -> first handle metrics
            -> second we are going to fetch the URL and get the status code

        Args:
            URL -> used to check if the URL cleaned up, existrs in the domains_visited set

        Things done:
            -> first call if this page is even active, if the page does repond, pass it into BS4
            -> filter BS4 to remove fragments, and check if the URL has been seen before, before enqueing it
                        
        '''
        url_response_text, status_code_for_fetch_page = self.fetch_page( url )
      
        if status_code_for_fetch_page == 404:
            print("process_page saw a 404 from fetch_page() ")
            # add this to metrics
            self.metrics.append({"site":url,"total_links_on_page":0, "status_code":status_code_for_fetch_page})

            return None
        
        soup = BeautifulSoup(url_response_text,'html.parser')
        '''
        <a href="internet.html">Internet Protocols and Support</a>
        <a href=""><code class="xref py py-mod docutils literal notranslate"><span class="pre">urllib.parse</span></code> â Parse URLs into components</a>
        <a href="../copyright.html">Copyright</a>
        <a href="/license.html">History and License</a>
        '''

        # filter just for the href part, and then combine to the proper URL, this is done uisng '.get(href)'

        # to filter on soup, we are going to use the 'find_all' command
        '''
        # <p class="story">Once upon a time there were three little sisters; and their names were
        #  <a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>,
        #  <a class="sister" href="http://example.com/lacie" id="link2">Lacie</a> and
        #  <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>;
        #  and they lived at the bottom of a well.</p>
        '''
        counting_links = 0

        for link in soup.find_all('a'):
            # print(link.get('href'))
            whole_url = urljoin( url, link.get('href') )
            # removing the fragments as it is a reference to a header on the same page
            new_url = whole_url.split('#')[0]
        
            # print( " new url made from fragments ", new_url, " old whole url is ", whole_url )

            if "javascript:;" in link:
                print("found invalid javascript:; line in link from soup! here is link! ", link)
                
            # eneque the new URLs to query on
            if self.validate_url(url) == True:
                self.q_domains_to_visit.append(new_url)

            # increase the number of links countered for the metrics
            counting_links+=1

        # print("Counter of all links found on page ", counting_links )

        '''
        From documentation: 

        urllib.parse.urljoin(base, url, allow_fragments=True)
        Construct a full (“absolute”) URL by combining a “base URL” (base) with another URL (url). 
        Informally, this uses components of the base URL, in particular the addressing scheme, the network location and (part of) the path, to provide missing components in the relative URL. For example:
        '''


        self.metrics.append({"site":url,"total_links_on_page":counting_links, "status_code":status_code_for_fetch_page})

        return 1

    def metrics_csv(self):
        """
        We are using this for output metrics and to provide a digestable overview

        see:
        https://www.geeksforgeeks.org/python/writing-csv-files-in-python

        Args:
            NA, using self.metrics

        Things done:
            break the Dict into its three keys and present them orderly:
            site -> the URL we are currently on
            total_links_on_page -> the other things to href and check
            status_code -> could we access the website?

        #TODO strech, include some metrics on how many hrefs we parsed per second, could be flashy
        """

        csv_header = self.metrics[0].keys() # pull the hdrs out

        with open("cvs_folder_of_sites/"+"metrics_output.csv", 'w', newline='' ) as csvfile:
            writer = csv.DictWriter( csvfile, fieldnames=csv_header )
            writer.writeheader()
            writer.writerows(self.metrics)

        print("csv writing complete")




        

    def crawl( self ):
        """
        Setting up main while loop and driver here

        we will be checking if the queues length is 0 of set_domains_to_vist since if its empty, everything must be in list_domains_to_vist
        """
        round_counter = 0
        while( ( len( self.q_domains_to_visit ) > 0 ) and ( self.max_url_hard_stop > round_counter ) ):
            curr_url = self.q_domains_to_visit.popleft()

            #populate the robots.txt
            self.robots_populator( curr_url )
            
            #TODO STRECH validate this domain in the URL / input the issue with it the metrics
            # you can likely just call validate domain perhaps? or call it before the while loop and input something into the metrics

            if curr_url in self.domains_visited:
                # if we have seen this URL before, leave it
                continue
            
            print(" we are working on URL ", curr_url )
            self.process_page( curr_url )
        
            # we have not seen this URL before, add it onto our list
            self.domains_visited.add( curr_url )

            print("sleeping for ", self.delay, " seconds ")
            time.sleep(self.delay)

            print("Presently, we are on URL number ", round_counter, " there are currently ", len(self.q_domains_to_visit) ," more URLs to go through " )
            print()
            print()
            print()
            round_counter +=1
            
            #TODO somehow this javascript;; is getting into my parser to make a request, I need to understand how, or find a way to exclude it
            '''
            Presently, we are on URL number  35  there are currently  15320  more URLs to go through 
            we are working on URL  javascript:;
            '''

        # write metrics from RAM
        self.metrics_csv()

        print( "done crawling! ") 
        return None


            
    

