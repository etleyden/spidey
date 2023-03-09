import sqlite3
from datetime import datetime

print(datetime.now())

db = sqlite3.connect("db/spidey_db.db")
cursor = db.cursor()
cursor.execute("CREATE TABLE pages (datetime TEXT, url TEXT, keywords TEXT)")

print(db.total_changes)
