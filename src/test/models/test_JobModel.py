import os
from datetime import datetime

import unittest
from unittest.mock import patch

from ...models import JobModel
from ... import helper
from ...helper import db_connect, db_init


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
                'hn_user': 'test_user',
                'job_text': 'test',
                'inserted_at': '2024-09-16T11:40:43',
                'status': 'new'
            },
            {
                'hn_id': 124,
                'hn_user': 'test_user',
                'job_text': 'other test',
                'inserted_at': '2024-09-16T11:40:43',
                'apply_at': '2024-09-16T11:40:43',
                'status': 'applied'
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
    def test_get(self, mock_get_db_path):
        # Mock get_db_path
        mock_get_db_path.return_value = self.tmp_db_path

        job = JobModel.get(1)

        self.assertEqual(job.id, 1)
        self.assertEqual(job.hn_id, 123)
        self.assertEqual(job.hn_user, 'test_user')
        self.assertEqual(job.job_text, 'test\n')
        self.assertEqual(job.status, 'new')

    @patch.object(helper, "get_db_path")
    def test_update(self, mock_get_db_path):
        # Mock get_db_path
        mock_get_db_path.return_value = self.tmp_db_path

        # Should update the status to 'applied' and set applied_at
        res = JobModel.update(1, 'applied')

        # Result should be true
        self.assertTrue(res)

        # Check the updated job
        job = JobModel.get(1)
        self.assertEqual(job.status, 'applied')
        self.assertIsInstance(job.applied_at, datetime)

        # Test updating to invalid status
        res = JobModel.update(1, 'invalid')
        self.assertFalse(res)

    @patch.object(helper, "get_db_path")
    def test_get_all(self, mock_get_db_path):
        # Mock get_db_path
        mock_get_db_path.return_value = self.tmp_db_path

        jobs = JobModel.get_all()
        self.assertEqual(len(jobs), 2)

        # Test with applied only
        jobs = JobModel.get_all(status='applied')
        self.assertEqual(len(jobs), 1)

        # Test with search=other
        jobs = JobModel.get_all(search='other')
        self.assertEqual(len(jobs), 1)

        # Test no result -> should return a default job
        jobs = JobModel.get_all(search='nothing')
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].job_text, 'No results.\n')

    @patch.object(helper, "get_db_path")
    def test_get_by_user(self, mock_get_db_path):
        # Mock get_db_path
        mock_get_db_path.return_value = self.tmp_db_path

        jobs = JobModel.get_by_user('unknown_user')
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].job_text, 'No results.\n')

        jobs = JobModel.get_by_user('test_user')
        self.assertEqual(len(jobs), 2)

    @patch.object(helper, "get_db_path")
    def test_get_to_discard(self, mock_get_db_path):
        # Mock get_db_path
        mock_get_db_path.return_value = self.tmp_db_path

        jobs_ids = JobModel.get_to_discard()
        self.assertEqual(len(jobs_ids), 1)
        for job_id in jobs_ids:
            self.assertIsInstance(job_id, int)

    def test_format_job(self):
        job = {
            'id': 1,
            'hn_id': 123,
            'hn_user': 'test'
        }
        res = JobModel.format_job(job)

        self.assertEqual(res.id, 1)
        self.assertEqual(res.hn_id, 123)
        self.assertEqual(res.hn_user, 'test')
