
from datetime import datetime

from pydantic import BaseModel
from typing import Optional
from helper import db_connect
from . import StatusModel


class Job(BaseModel):
    id: int
    job_text: str
    inserted_at: datetime
    applied_at: Optional[datetime]
    status: str


def get(job_id):
    """
        Get a job by ID
    """
    conn = db_connect()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, job_text, inserted_at, applied_at, status
    FROM jobs
    WHERE id = ?
    ''', (job_id,))

    job = cursor.fetchone()
    conn.close()
    return Job(id=job[0], job_text=job[1], inserted_at=job[2], applied_at=job[3], status=job[4])


def update(job_id, status):
    """
        Update the status of a job
    """
    conn = db_connect()
    cursor = conn.cursor()

    # Check for valid statuses
    valid_statuses = [status.value for status in StatusModel.get_all()]
    if status not in valid_statuses:
        # raise ValueError('Invalid status')
        return False

    query_params = [status, job_id]

    # If the status is 'applied', update the 'applied_at' field
    query_part = ''
    if status == 'applied':
        query_part = ', applied_at = ?'
        query_params.insert(1, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    cursor.execute(f'''
    UPDATE jobs
    SET status = ? {query_part}
    WHERE id = ?
    ''', query_params)

    conn.commit()
    conn.close()

    return True


def get_all(status=None, search=None):
    """
        Get jobs from SQLITE
        Return them as instance of Job
    """
    conn = db_connect()
    cursor = conn.cursor()

    query_part = ''
    query_params = []
    if status:
        query_part += 'AND status = ?'
        query_params.append(status)

    if search:
        query_part += 'AND job_text LIKE ?'
        query_params.append(f'%{search}%')

    query = f"""
    SELECT id, job_text, inserted_at, applied_at, status
    FROM jobs
    WHERE 1=1
    {query_part}
    """
    cursor.execute(query, query_params)

    jobs = cursor.fetchall()
    conn.close()

    if not jobs:
        # @todo: better handling of no jobs found
        return [
            Job(id=0, job_text='No jobs found',
                inserted_at=datetime.now(), applied_at=None, status='new')
        ]

    return [Job(id=job[0], job_text=job[1], inserted_at=job[2], applied_at=job[3], status=job[4]) for job in jobs]
