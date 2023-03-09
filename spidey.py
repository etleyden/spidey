from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import sqlite3
from datetime import datetime
test_url = "https://www.geeksforgeeks.org/"

"""
The Page class loads a page and stores the following: 
self.url: the given URL of that page
self.urls_on_page: Any URL that we found in the content of that page
self.keywords: The top 10 keywords that were potentially visible to the user
"""
class Page:
    def __init__(self, page_id, url):
        self.page_id = page_id
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
            if link == None: continue
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

        # get top 10 most common words, TODO: find a way to preserve keywords with the quantity of each found on the page
        visible_text = re.split("\s+", soup.getText())
        self.keywords = pd.Series(visible_text).value_counts()[:10].index.tolist()

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
A basic web crawler that starts at your given start_url, and stores the data in
db/spidey_db.db
"""
class Spidey:
    def __init__(self, start_url, db):
        self.source = start_url
        self.pages = []
        self.queued_urls = []
        self.visited_urls = []
        self.num_pages = 0
        self.db = db

    """
    Ends the crawler. Writes the URLs that are next to a .txt file.
    """
    def abort(self):
        self.write_to_db("pages")
        self.write_to_db("queued_urls")
        self.write_to_db("visited_urls")

    def write_to_db(self, table):
        # connect to the db
        sqldb = sqlite3.connect(self.db)
        cursor = sqldb.cursor()

        # build the appropriate sql command with our new data
        insert_cmd = "INSERT INTO " + table + " VALUES "
        first = True
        if table == "queued_urls" or table == "visited_urls":
            for url in getattr(self, table):
                if not first: insert_cmd += ", \n"
                else: first = False
                insert_cmd += "('{val}')".format(val=url)
            setattr(self, table, [])
        elif table == "pages":
            for page in self.pages:
                page_str = """('{page_id}', '{url}', '{keywords}')""".format(
                    page_id=page.page_id, 
                    url=page.url, 
                    keywords=', '.join(page.keywords))
                if not first: insert_cmd += ", \n"
                else: first = False
                insert_cmd += page_str
            self.pages = []


        # DO the INSERT
        file = open(table + ".txt", "w")
        file.write(insert_cmd)
        file.close()



    """
    Starts crawling webpages at the value stored in source.
    Stores pages, and keeps lists of visited and not-visited URLs it found.
    """
    def spin_web(self):
        self.queued_urls.append(self.source) 
        while len(self.queued_urls) > 0:
            # deqeue the first URL
            current_url = self.queued_urls[0]

            # create page object
            current_page = Page(datetime.now(), current_url)

            # Load the page
            current_page.read_page()

            # Extract the urls
            urls = current_page.urls_on_page
            for url in urls:
                if url not in self.visited_urls:
                    self.queued_urls.append(url)

            # Mark it as visited
            self.pages.append(current_page)
            self.visited_urls.append(self.queued_urls.pop(0))
            self.num_pages += 1

            if self.num_pages % 10 == 0:
                print("We've visited %d webpages. Continue? (y/n)" % (self.num_pages))
                user_continue = input()
                if user_continue == "n":
                    self.abort()


Spidey(test_url, "db/spidey_db.db").spin_web()
