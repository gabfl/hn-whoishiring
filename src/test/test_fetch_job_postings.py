import os
from datetime import datetime

import unittest
from bs4 import BeautifulSoup

from .. import fetch_job_postings


class Test(unittest.TestCase):

    thread_html_path = os.path.dirname(__file__) + '/assets/thread.html'
    comment_html_path = os.path.dirname(__file__) + '/assets/comment.html'

    def test_load_url(self):
        res = fetch_job_postings.load_url('http://perdu.com')
        self.assertTrue(res.startswith('<html><head>'))

    def test_load_file(self):
        res = fetch_job_postings.load_file(self.thread_html_path)
        self.assertTrue(res.startswith('<html lang="en" op="item">'))

    def test_get_all_comments(self):
        source = fetch_job_postings.load_file(self.thread_html_path)
        soup = fetch_job_postings.BeautifulSoup(source, 'html.parser')
        res = fetch_job_postings.get_all_comments(soup)
        self.assertEqual(len(res), 474)

    def test_is_reply(self):
        raw = fetch_job_postings.load_file(self.comment_html_path)

        # Create soup from sample comment
        soup = BeautifulSoup(raw, 'html.parser')

        res = fetch_job_postings.is_reply(soup)
        self.assertFalse(res)

        # replace indent="0 with indent="1"
        soup = BeautifulSoup(raw.replace('indent="0"', 'indent="1"'), 'html.parser')

        res = fetch_job_postings.is_reply(soup)
        self.assertTrue(res)

    def test_parse_from_comment(self):
        raw = fetch_job_postings.load_file(self.comment_html_path)

        # Create soup from sample comment
        soup = BeautifulSoup(raw, 'html.parser')

        (comment, hn_user, hn_id) = fetch_job_postings.parse_from_comment(soup)

        self.assertEqual(
            comment, '<div class="commtext c00">Sealth | Designer &amp; Back end Course Designer| Full-Time </div>')
        self.assertEqual(hn_user, 'OnjaMadagascar')
        self.assertEqual(hn_id, '41555035')
