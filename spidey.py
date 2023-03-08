from bs4 import BeautifulSoup
import requests
import re
import pandas as pd

test_url = "https://www.geeksforgeeks.org/"

"""
The Page class loads a page and stores the following: 
self.url: the given URL of that page
self.urls_on_page: Any URL that we found in the content of that page
self.keywords: The top 10 keywords that were potentially visible to the user
"""
class Page:
    def __init__(self, url):
        self.urls_on_page = []
        self.url = url
        self.keywords = None

    """Calls requests.get(self.url).text to get the text served at this URL"""
    def get_raw_text(self):
        return requests.get(self.url).text

    """Returns the BeautifulSoup object generated from the text on at this URL"""
    def load_page_as_soup(self):
        text = self.get_raw_text()
        return BeautifulSoup(text, "html.parser")

    """
    Retrives all http(s) values found in href attributes on the page. 
    Stores the list in self.urls_on_page, and returns it
    """
    def get_urls(self, soup=-1):
        # Retrieve text
        if soup == -1: soup = self.load_page_as_soup()
        
        # Filter 'a' elements
        link_elements = soup("a")

        # Filter href attributes that are http(s) links
        for element in link_elements:
            link = element.get("href")
            match = re.search("http", link)
            if match is not None and match.span()[0] == 0:
                self.urls_on_page.append(link)

        return self.urls_on_page

    """
    Retrieves the top 10 whitespace separated strings on the page by frequency
    Does NOT do a fuzzy match
    Stores as a pandas Series object
    """
    def get_keywords(self, soup=-1):
        # Get text if we haven't yet
        if soup == -1: soup = self.load_page_as_soup()

        # get top 10 most common words
        visible_text = re.split("\s+", soup.getText())
        self.keywords = pd.Series(visible_text).value_counts()[:10]

        return self.keywords

    """
    Loads all data that this object can hold from the URL attribute
    """
    def read_page(self):
        print("Accessing: " + str(self.url))
        soup = self.load_page_as_soup()
        self.get_urls(soup)
        self.get_keywords(soup)

"""
A basic web crawler that starts at your given start_url
"""
class Spidey:
    def __init__(self, start_url):
        self.source = start_url
        self.pages = []
        self.queue = []
        self.visited = []

    """
    Starts crawling webpages at the value stored in source.
    Stores pages, and keeps lists of visited and not-visited URLs it found.
    """
    def spin_web(self):
        self.queue.append(self.source) 
        while len(self.queue) > 0:
            current_url = self.queue[0]
            current_page = Page(current_url)
            current_page.read_page()
            urls = current_page.urls_on_page
            for url in urls:
                if url not in self.visited:
                    self.queue.append(url)
            self.pages.append(current_page)
            self.visited.append(self.queue.pop(0))


Spidey(test_url).spin_web()
