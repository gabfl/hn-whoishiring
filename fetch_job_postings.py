import requests
from bs4 import BeautifulSoup
import argparse
import hashlib
from datetime import datetime

from helper import db_connect, db_init, backup_db_file, is_hacker_news_url, html_to_markdown


def main(url):
    """
    Fetch job postings from a Hacker News page and store them in a SQLite database.
    """

    # Check if the URL is a valid Hacker News URL
    if not is_hacker_news_url(url):
        print('Invalid Hacker News URL')
        return

    # Backup the database
    res = backup_db_file()
    print(f'$ {res}')

    # Initialize the database
    res = db_init()
    print(f'$ {res}')

    # Send a GET request to fetch the page content
    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful

    # Parse the page content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all comments (jobs) in the page
    comments = soup.find_all('div', class_='commtext')

    # Extract job postings
    # jobs = [comment.get_text() for comment in comments]
    jobs = [str(comment) for comment in comments]

    # Connect to the SQLite database
    conn = db_connect()

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Insert job postings into the database with the current timestamp
    count = 0
    for job in jobs:
        # Skip items that don't contain a | character
        # @todo: This is a temporary fix to avoid adding non-job items to the database, improve me!
        if '|' not in job:
            continue

        # Convert HTML to Markdown
        job = html_to_markdown(job)

        # Calculate the hash of the job text
        job_hash = hashlib.sha256(job.encode()).hexdigest()

        # Check if the job already exists in the database
        cursor.execute(
            'SELECT COUNT(*) FROM jobs WHERE job_hash = ?', (job_hash,))
        job_exists = cursor.fetchone()[0] > 0
        if not job_exists:
            count += 1
            inserted_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute(
                'INSERT INTO jobs (job_text, job_hash, inserted_at, status) VALUES (?, ?, ?, ?)', (job, job_hash, inserted_at, 'new'))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print(f'$ {count} new jobs added')


if __name__ == '__main__':
    # Get URL from command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--url', '-u', help='URL of the Hacker News page with job postings', required=True)
    args = parser.parse_args()

    main(args.url)
