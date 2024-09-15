import os
import re
from datetime import datetime

import sqlite3
import html2text
from cacheout import Cache

cache = Cache(maxsize=1000)


def get_db_path():
    """
        Get the path to the SQLite database
    """

    return 'data/hn_jobs.db'


def backup_db_file():
    """
        Backup the SQLite database file
    """

    db_path = get_db_path()
    backup_path = f'{db_path}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.bak'

    # Check if the database exists
    db_exists = os.path.exists(db_path)

    if db_exists:
        # Copy the database file
        os.system(f'cp {db_path} {backup_path}')

        return "Database backup created at " + backup_path

    return "No database to backup"


def db_connect():
    """
        Connect to the SQLite database
    """

    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row

    return conn


def db_init():
    """
        Initialize the SQLite database
    """

    # Check if the database exists
    db_exists = os.path.exists(get_db_path())

    if db_exists:
        return "Database already exists"

    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = db_connect()
    cursor = conn.cursor()

    # Create a table to store jobs if it doesn't exist
    if not db_exists:
        cursor.execute('''
        CREATE TABLE jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_text TEXT NOT NULL,
            job_hash TEXT NOT NULL,
            inserted_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP,
            applied_at TIMESTAMP,
            status TEXT
        )
        ''')
        conn.commit()

    return "Database created"


def is_hacker_news_url(url):
    return 'news.ycombinator.com' in url


def html_to_markdown(html):
    # Convert HTML to Markdown
    markdown_converter = html2text.HTML2Text()
    markdown_converter.ignore_links = False  # Keep the links in the markdown
    markdown_content = markdown_converter.handle(html)

    return markdown_content


def get_from_cache(key):
    """ Get filters from cache """
    return cache.get(key)


def set_to_cache(key, value):
    """ Set filters in cache """
    cache.set(key, value)


def resolve_email(text):
    """
        Deobfuscate an obfuscated email address
    """

    # Regular expression to match the pattern for obfuscated email addresses like "name dot domain at domain"
    patterns = [
        r'([a-zA-Z0-9_-]+( dot [a-zA-Z0-9_-]+)? at [a-zA-Z0-9_-]+ dot [a-zA-Z0-9_-]+)',
        # similar but [at] instead of " at " and [dot] instead of " dot "
        r'([a-zA-Z0-9_-]+( ?\[dot\] ?[a-zA-Z0-9_-]+)? ?\[at\] ?[a-zA-Z0-9_-]+ ?\[dot\] ?[a-zA-Z0-9_-]+)',
        # Same but just [at] is used
        r'([a-zA-Z0-9_.-]+\s?\[at\]\s?[a-zA-Z0-9_.-]+)',
    ]

    for pattern in patterns:
        # Find the line containing the email using regex
        match = re.search(pattern, text)

        if match:
            # Extract the matched text
            obfuscated_email = match.group(0)
            # Replace " dot " with "." and " at " with "@"
            email = obfuscated_email.replace(" dot ", ".").replace(" at ", "@")
            email = email.replace(" [dot] ", ".").replace(" [at] ", "@")
            email = email.replace("[dot]", ".").replace("[at]", "@")

            # Add lime break and append email
            return text + "\n🪄 *Deobfuscated email:* " + email

    return text


def format_dt(date):
    """ Format datetime """

    if not date:
        return None

    return date.strftime('%m/%d/%Y %I:%M:%S %p')
