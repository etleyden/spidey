import sqlite3
from datetime import datetime
import pandas as pd
import hashlib
print(datetime.now())

db = sqlite3.connect("db/spidey_db.db")
cursor = db.cursor()
cursor.execute("SELECT url FROM queued_urls")
string_to_concat = "TestStringaskdlj sad;lj"
hashed_urls = pd.DataFrame.from_records(cursor.fetchall())

print(hashlib.md5(string_to_concat.encode()).hexdigest())
