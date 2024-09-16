import os
from datetime import datetime

import unittest
from unittest.mock import patch, MagicMock
import sqlite3

from .. import helper


class Test(unittest.TestCase):

    def test_get_db_path(self):
        res = helper.get_db_path()
        self.assertTrue(res.endswith('data/hn_jobs.db'))

    def test_db_connect(self):
        res = helper.db_connect()
        self.assertIsInstance(res, sqlite3.Connection)

    # @patch('..helper.get_db_path')
    # @patch('..helper.db_connect')
    # def test_db_init(self, mock_db_connect, mock_get_db_path):
    #     # Mock get_db_path to return /tmp/mock.db
    #     mock_get_db_path.return_value = '/tmp/mock.db'

    #     # Mock the db_connect method to prevent actual database creation
    #     mock_conn = mock_db_connect.return_value
    #     mock_cursor = mock_conn.cursor.return_value

    #     res = helper.db_init()
    #     self.assertEqual(res, "Database created")

    def test_is_hacker_news_url(self):
        res = helper.is_hacker_news_url('https://news.ycombinator.com')
        self.assertTrue(res)

        res = helper.is_hacker_news_url('https://example.com')
        self.assertFalse(res)

    def test_html_to_markdown(self):
        html = '<p>Hello, world!</p>'
        res = helper.html_to_markdown(html)
        self.assertEqual(res, 'Hello, world!\n')

        html = '<p><a href="https://example.com">Hello, world!</a></p>'
        res = helper.html_to_markdown(html)
        self.assertEqual(res, '[Hello, world!](https://example.com)\n')

    def test_get_from_cache(self):
        res = helper.get_from_cache('test')
        self.assertIsNone(res)

        helper.set_to_cache('test', 'value')
        res = helper.get_from_cache('test')
        self.assertEqual(res, 'value')

    def test_set_to_cache(self):
        helper.set_to_cache('test', 'value')
        res = helper.get_from_cache('test')
        self.assertEqual(res, 'value')

    def test_resolve_email(self):
        text = 'Send an email to hello dot world at example dot com now'
        res = helper.resolve_email(text)
        self.assertEqual(
            res, 'Send an email to hello dot world at example dot com now\n🪄 *Deobfuscated email:* hello.world@example.com')

        text = 'Contact me at hello [at] example [dot] com'
        res = helper.resolve_email(text)
        self.assertEqual(
            res, 'Contact me at hello [at] example [dot] com\n🪄 *Deobfuscated email:* hello@example.com')

        text = 'Contact me at hello[at]example[dot]com'
        res = helper.resolve_email(text)
        self.assertEqual(
            res, 'Contact me at hello[at]example[dot]com\n🪄 *Deobfuscated email:* hello@example.com')

    def test_format_dt(self):
        dt = datetime(2021, 8, 1, 12, 0, 0)
        res = helper.format_dt(dt)
        self.assertEqual(res, '08/01/2021 12:00:00 PM')

    def test_get_link_user(self):
        res = helper.get_link_user('test')
        self.assertEqual(res, 'https://news.ycombinator.com/user?id=test')

    def test_get_link_comment(self):
        res = helper.get_link_comment('test')
        self.assertEqual(res, 'https://news.ycombinator.com/item?id=test')
