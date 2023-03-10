# Getting Started

First, run `init_db.py` so your SQLite3 file is up to spec.
Then, you can alter the `test_url` in `spidey.py` to start wherever you want.
Finally, run `spidey.py`, answer the prompt, and let it run.

# Dependencies

The following can be installed using `pip3`:

 * pandas
 * bs4
 * sqlite3

# TODO

 * Load dynamic pages fully before scraping URLs
 * Better keyword identification (Filter out articles, symbols, find words that are more likely of interest to a user)
 * Prevent duplicate values from entering the DB
     * This largely occurs when the script is run on separate intsances
