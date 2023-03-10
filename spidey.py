from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import sqlite3
from datetime import datetime
from datetime import timezone
import hashlib
test_url = "https://www.geeksforgeeks.org/"

"""
The Page class loads a page and stores the following: 
self.url: the given URL of that page
self.urls_on_page: Any URL that we found in the content of that page
self.keywords: The top 10 keywords that were potentially visible to the user
"""
class Page:
    def __init__(self, url):
        self.page_id = Page.generate_page_id(url)
        self.urls_on_page = []
        self.url = url
        self.keywords = None
        self.date_visited = ""

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
        soup = None
        try:
            soup = self.load_page_as_soup()
        except Exception as e:
            print("We couldn't access that page: " + str(type(e)))
            return False
        self.get_urls(soup)
        self.get_keywords(soup)
        self.date_visited = datetime.now(timezone.utc)
        return True

    def generate_page_id(url):
        return hashlib.md5(url.encode()).hexdigest()
"""
A basic web crawler that starts at your given start_url, and stores the data in
db/spidey_db.db
"""
class Spidey:
    def __init__(self, start_url, db):
        self.source = start_url
        self.pages = []
        self.visited_urls = []
        self.num_pages = 0
        self.db = sqlite3.connect(db)
        cursor = self.db.cursor()
        # fetch queued_urls
        cursor.execute("SELECT url FROM queued_urls")
        db_queue_as_series = pd.DataFrame.from_records(cursor.fetchall()).squeeze()
        if len(db_queue_as_series) == 0:
            self.queued_urls = []
        else:
            self.queued_urls = db_queue_as_series.tolist()
        # fetch visited urls
        cursor.execute("SELECT page_id FROM pages")
        hashed_urls_as_series = pd.DataFrame.from_records(cursor.fetchall()).squeeze()
        if len(hashed_urls_as_series) == 0:
            self.hashed_urls = []
        else:
            self.hashed_urls = hashed_urls_as_series.tolist()
        
        # if the hash of the start url isn't in here, then queue that one first
        if Page.generate_page_id(start_url) not in self.hashed_urls:
            self.queued_urls.insert(0, start_url)
    """
    Ends the crawler. Writes the URLs that are next to a .txt file.
    """
    def abort(self):
        self.write_to_db("pages")
        self.write_to_db("queued_urls")

    def write_to_db(self, table):
        # connect to the db
        cursor = self.db.cursor()

        # build the appropriate sql command with our new data
        insert_cmd = "INSERT INTO " + table + " VALUES "
        first = True
        if table == "queued_urls":
            for url in getattr(self, table):
                if not first: insert_cmd += ", \n"
                else: first = False
                insert_cmd += "('{val}')".format(val=url)
            setattr(self, table, [])
        elif table == "pages":
            for page in self.pages:
                page_str = """('{page_id}', '{date}', '{url}', '{keywords}')""".format(
                    page_id=page.page_id, 
                    date=page.date_visited,
                    url=page.url, 
                    keywords=', '.join(page.keywords))
                if not first: insert_cmd += ", \n"
                else: first = False
                insert_cmd += page_str
            self.pages = []
        
        # insert the values
        cursor.execute(insert_cmd)
        self.db.commit()




    """
    Starts crawling webpages at the value stored in source.
    Stores pages, and keeps lists of visited and not-visited URLs it found.
    """
    def spin_web(self):
        print("How many pages would you like to scrape? (Recommended: 30)")
        pages_to_scrape = int(input())
        while len(self.queued_urls) > 0:
            # deqeue the first URL
            current_url = self.queued_urls.pop(0)

            # create page object
            current_page = Page(current_url)

            # Load the page
            if current_page.read_page():

                # Add the url to visited so we can filter it out 
                # when the page references itself
                self.hashed_urls.append(current_page.page_id)

                # Extract the urls
                urls = current_page.urls_on_page
                for url in urls:
                    if Page.generate_page_id(url) not in self.hashed_urls:
                        self.queued_urls.append(url)

                # Mark it as visited
                self.pages.append(current_page)
                self.num_pages += 1

                if self.num_pages % pages_to_scrape == 0:
                    print("We've visited %d webpages. Continue? (y/n)" % (self.num_pages))
                    user_continue = input()
                    if user_continue == "n":
                        self.abort()
                        return

        print("Wow! The queue is empty. I guess you scoured the ENTIRE internet?")
Spidey(test_url, "db/spidey_db.db").spin_web()
