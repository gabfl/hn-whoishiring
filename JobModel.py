
from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional
from helper import db_connect


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
    if status not in ['new', 'applied', 'discarded', 'interviewed']:
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
    query_params = ()
    if status:
        query_part = 'WHERE status = ?'
        query_params = (status,)

    if search:
        query_part = 'WHERE job_text LIKE ?'
        query_params = (f'%{search}%',)

    query = f"""
    SELECT id, job_text, inserted_at, applied_at, status
    FROM jobs
    {query_part}
    """
    cursor.execute(query, query_params)

    jobs = cursor.fetchall()
    conn.close()
    return [Job(id=job[0], job_text=job[1], inserted_at=job[2], applied_at=job[3], status=job[4]) for job in jobs]
