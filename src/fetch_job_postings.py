import requests
from bs4 import BeautifulSoup
import argparse

from .helper import db_connect, db_init, backup_db_file, is_hacker_news_url, html_to_markdown


def load_url(url):
    """ Load the content of a URL """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Check if the request was successful
    return response.text


def load_file(file):
    """ Load the content of a file (for tests) """

    with open(file) as f:
        return f.read()


def get_all_comments(soup):
    """ Get all comments from the page """

    # Find all comments (jobs) in the page
    items = soup.find_all('tr', class_='athing comtr')

    return items


def is_reply(item):
    """ Check if the item is a reply """

    # Check if there is a td with attribute "indent" in the item and the value is greater than 0
    # Example:  <td class='ind' indent='3'>
    res = item.find(
        lambda tag: tag.name == 'td' and tag.get('indent') and int(tag['indent']) > 0)

    if res:
        return True

    return False


def parse_from_comment(item):
    """ Parse the comment and extract the job details """

    # Get comment from commtext div
    comment = str(item.find('div', class_='commtext'))

    # Get link with class hnuser
    user = item.find('a', class_='hnuser')
    hn_user = None
    if user:
        hn_user = user.get_text()

    # Get URL in spam class
    span = item.find('span', class_='age')
    hn_id = None
    if span:
        # extract URL
        url = span.find('a')
        if url:
            url = url.get('href')
            # id if after the =
            hn_id = url.split('=')[-1]

    return (comment, hn_user, hn_id)


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

    # Setup the database connection
    conn = db_connect()
    cursor = conn.cursor()

    # Fetch source code of the page
    source = load_url(url)
    # source = load_file('data/hn.html')

    # Parse the page content using BeautifulSoup
    soup = BeautifulSoup(source, 'html.parser')

    # Insert job postings into the database with the current timestamp
    count = 0
    for item in get_all_comments(soup):
        # Skip replies
        if is_reply(item):
            continue

        (comment, hn_user, hn_id) = parse_from_comment(item)

        # Check if the job already exists in the database
        cursor.execute(
            'SELECT id FROM jobs WHERE hn_id = ?', (hn_id,))
        job_exists = cursor.fetchone()

        if job_exists:
            # We will update the job text if it has changed
            cursor.execute(
                'UPDATE jobs SET job_text = ? WHERE hn_id = ?', (comment, hn_id))
        else:
            count += 1

            cursor.execute("""
            INSERT INTO jobs (hn_id, hn_user, job_text, inserted_at, status)
                           VALUES (?, ?, ?, datetime('now'), 'new')
            """, (hn_id, hn_user, comment))

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
