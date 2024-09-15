
from datetime import datetime

from pydantic import BaseModel, validator
from typing import Optional
from helper import db_connect, resolve_email
from . import StatusModel


class Job(BaseModel):
    id: int
    job_text: str
    inserted_at: datetime
    updated_at: Optional[datetime]
    applied_at: Optional[datetime]
    status: str


def get(job_id):
    """
        Get a job by ID
    """
    conn = db_connect()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, job_text, inserted_at, updated_at, applied_at, status
    FROM jobs
    WHERE id = ?
    ''', (job_id,))

    row = cursor.fetchone()
    conn.close()
    return format_job(row)


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

    # If the status is 'applied', update the 'applied_at' field
    query_part = ''
    if status == 'applied':
        query_part = ", applied_at = datetime('now')"

    cursor.execute(f'''
    UPDATE jobs
    SET status = ?, updated_at = datetime('now') {query_part}
    WHERE id = ?
    ''', (status, job_id))

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
    SELECT id, job_text, inserted_at, updated_at, applied_at, status
    FROM jobs
    WHERE 1=1
    {query_part}
    """
    cursor.execute(query, query_params)

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        # @todo: better handling of no jobs found
        return [
            Job(id=0, job_text='No jobs found',
                inserted_at=datetime.now(), applied_at=None, status='new')
        ]

    jobs = []
    for row in rows:
        jobs.append(format_job(row))

    return jobs


def format_job(job):
    """
        Format a job
    """

    # Resolve emails
    job_text = resolve_email(job['job_text'])

    return Job(
        id=job['id'],
        job_text=job_text,
        inserted_at=job['inserted_at'],
        updated_at=job['updated_at'],
        applied_at=job['applied_at'],
        status=job['status']
    )
