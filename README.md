# hn-whoishiring

A FastUI/FastAPI app to manage and interact with Hacker News’s “Who is Hiring” postings.

## Overview

This application allows you to scrape, store, and interactively explore job postings from Hacker News’s “Who is Hiring?” threads. It uses FastAPI for the backend, FastUI for the frontend, and SQLite for data storage.

## Features

 - **Scraping:** Fetch job listings from the “Who is Hiring?” thread on Hacker News.
 - **Storage:** Store job postings in a local SQLite database.
 - **Search & Filter:** Search and filter job postings through a simple web interface.
 - **FastUI Integration:** Provides an interactive UI for managing and exploring the job listings.

## Prerequisites

 - Python 3.12+
 - Virtualenv (optional, but recommended)

## Usage

```bash
virtualenv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Use the fetch_job_postings.py script to scrape and store job postings from the latest “Who is Hiring?” thread. 
# eplace the URL with the current “Who is Hiring?” thread URL.
python3 fetch_job_postings.py --url https://news.ycombinator.com/item?id=41425910
$ Database created
$ 283 new jobs added

# Run the FastAPI server with Uvicorn:
uvicorn app:app
```

Then simply visit [http://127.0.0.1:8000](http://127.0.0.1:8000)

![Main page](img/main.png)
![Job posting](img/posting.png)

## Contributing

Contributions are welcome! If you’d like to improve this project, please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.
