import os

import unittest
from unittest.mock import patch

from .. import auto_discard
from .. import helper
from ..helper import db_connect, db_init


class Test(unittest.TestCase):

    tmp_db_path = '/tmp/mock.db'

    def setUp(self) -> None:
        # Initialize the database
        self.initialize_db()

        # Create jobs
        self.create_jobs()

    def tearDown(self) -> None:
        # Delete the mock database
        if os.path.exists(self.tmp_db_path):
            os.remove(self.tmp_db_path)

    @patch.object(helper, "get_db_path")
    def initialize_db(self, mock_get_db_path):
        # Mock get_db_path
        mock_get_db_path.return_value = self.tmp_db_path

        # Initialize the database
        db_init()

    @patch.object(helper, "get_db_path")
    def create_jobs(self, mock_get_db_path):
        # Mock get_db_path
        mock_get_db_path.return_value = self.tmp_db_path

        conn = db_connect()
        cursor = conn.cursor()

        jobs = [
            {
                'hn_id': 123,
                'hn_user': 'test_user2',
                'job_text': 'test',
                'inserted_at': '2024-09-16T11:40:43',
                'status': 'new'
            },
            {
                'hn_id': 124,
                'hn_user': 'test_user2',
                'job_text': 'other test',
                'inserted_at': '2024-09-16T11:40:43',
                'apply_at': '2024-09-16T11:40:43',
                'status': 'discarded'
            }
        ]

        for job in jobs:
            cursor.execute("""
            INSERT INTO jobs (hn_id, hn_user, job_text, inserted_at, status)
            VALUES (?, ?, ?, ?, ?)
            """, (job['hn_id'], job['hn_user'], job['job_text'], job['inserted_at'], job['status']))

        conn.commit()
        conn.close()

    @patch.object(helper, "get_db_path")
    def test_get_count(self, mock_get_db_path):
        # Mock get_db_path
        mock_get_db_path.return_value = self.tmp_db_path

        res = auto_discard.get_count()
        self.assertEqual(res, 1)

    @patch.object(helper, "get_db_path")
    def test_auto_discard(self, mock_get_db_path):
        # Mock get_db_path
        mock_get_db_path.return_value = self.tmp_db_path

        res = auto_discard.discard_jobs()
        self.assertEqual(res, 1)

        # Second call should return 0
        res = auto_discard.discard_jobs()
        self.assertEqual(res, 0)
