import os

import sqlite3
import html2text


def get_db_path():
    """
        Get the path to the SQLite database
    """

    return 'data/hn_jobs.db'


def db_connect():
    """
        Connect to the SQLite database
    """

    return sqlite3.connect(get_db_path())


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
