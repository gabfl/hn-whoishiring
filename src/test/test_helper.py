import os
from datetime import datetime

import unittest
from unittest.mock import patch
import sqlite3

from .. import helper


class Test(unittest.TestCase):

    tmp_db_path = '/tmp/mock.db'

    def tearDown(self) -> None:
        # Delete the mock database
        if os.path.exists(self.tmp_db_path):
            os.remove(self.tmp_db_path)

    def test_get_db_path(self):
        res = helper.get_db_path()
        self.assertTrue(res.endswith('data/hn_jobs.db'))

    @patch.object(helper, "get_db_path")
    def test_backup_db_file(self, mock_get_db_path):
        # Mock get_db_path
        mock_get_db_path.return_value = self.tmp_db_path

        res = helper.backup_db_file()
        self.assertEqual(res, "No database to backup")

        # Create a mock database
        with open(self.tmp_db_path, 'w') as f:
            f.write('mock')

        res = helper.backup_db_file()
        self.assertTrue(res.startswith('Database backup created at'))

    def test_db_connect(self):
        res = helper.db_connect()
        self.assertIsInstance(res, sqlite3.Connection)

    @patch.object(helper, "get_db_path")
    def test_db_init(self, mock_get_db_path):
        # Mock get_db_path
        mock_get_db_path.return_value = self.tmp_db_path

        res = helper.db_init()
        self.assertEqual(res, "Database created")

        # Second call
        res = helper.db_init()
        self.assertEqual(res, "Database already exists")

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

        # Test with no email to format
        text = 'This is my posting'
        res = helper.resolve_email(text)
        self.assertEqual(res, text)

    def test_format_dt(self):
        dt = datetime(2021, 8, 1, 12, 0, 0)
        res = helper.format_dt(dt)
        self.assertEqual(res, '08/01/2021 12:00:00 PM')

        res = helper.format_dt(None)
        self.assertIsNone(res)

    def test_get_hn_link_user(self):
        res = helper.get_hn_link_user('test')
        self.assertEqual(res, 'https://news.ycombinator.com/user?id=test')

    def test_get_hn_link_comment(self):
        res = helper.get_hn_link_comment('test')
        self.assertEqual(res, 'https://news.ycombinator.com/item?id=test')
