import sqlite3
import os

# connect to the table. This will create it if it doesn't exist
db = sqlite3.connect("db/spidey_db.db")

c = db.cursor() #Cursor

# get existing tables
c.execute(''' SELECT name FROM sqlite_master WHERE type='table' ''')
existing_tables = c.fetchone()

# tables we need and the command to create them.
# the command to create any table at index n in 'required_tables' is 
# located in 'create_table_cmd[n]'
required_tables = ['pages','visited_urls','queued_urls']
create_table_cmd = ['CREATE TABLE pages (datetime TEXT, url TEXT, keywords TEXT)',
                    'CREATE TABLE visited_urls (url TEXT)',
                    'CREATE TABLE queued_urls (url TEXT)']

# Check if the table exists, if not, create it
for table in required_tables:
    if table not in existing_tables:
        table_idx = required_tables.index(table)
        c.execute(create_table_cmd[table_idx])


db.close()
