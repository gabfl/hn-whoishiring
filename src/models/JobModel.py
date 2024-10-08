
from datetime import datetime

from pydantic import BaseModel
from typing import Optional
from ..helper import db_connect, resolve_email, html_to_markdown
from . import StatusModel


class Job(BaseModel):
    id: int
    hn_id: Optional[int]
    hn_user: Optional[str]
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
    SELECT j.id, j.hn_id, j.hn_user, j.job_text, j.inserted_at, j.updated_at, j.applied_at, j.status
    FROM jobs j
    WHERE id = ?
    ''', (job_id,))

    row = cursor.fetchone()
    conn.close()
    return format_job(dict(row) or {})


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
    SELECT id, hn_id, hn_user, job_text, inserted_at, updated_at, applied_at, status
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
            format_job({
                'id': 0,
                'job_text': 'No results.',
            })
        ]

    jobs = []
    for row in rows:
        jobs.append(format_job(dict(row)))

    return jobs


def get_by_user(hn_user):
    """
        Get jobs by user
    """
    conn = db_connect()
    cursor = conn.cursor()

    query = '''
    SELECT j.id, j.hn_id, j.hn_user, j.job_text, j.inserted_at, j.updated_at, j.applied_at, j.status
    FROM jobs j
    WHERE hn_user = ?
    '''

    cursor.execute(query, [hn_user])

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        # @todo: better handling of no jobs found
        return [
            format_job({
                'id': 0,
                'job_text': 'No results.',
            })
        ]

    jobs = []
    for row in rows:
        jobs.append(format_job(dict(row)))

    return jobs


def get_to_discard():
    """
        Get jobs that can be discarded because the user is matched with another job
    """
    conn = db_connect()
    cursor = conn.cursor()

    query = '''
    SELECT j.id
    FROM jobs j
    WHERE status = 'new'
        AND EXISTS (
            SELECT 1
            FROM jobs
            WHERE hn_user = j.hn_user
                AND id != j.id
                AND status IN ('applied', 'discarded', 'interviewed', 'rejected-pre', 'rejected-post')
            );
    '''

    cursor.execute(query)

    rows = cursor.fetchall()
    conn.close()

    return [row['id'] for row in rows]


def format_job(job):
    """
        Format a job
    """

    # Resolve emails
    job_text = resolve_email(job.get('job_text', ''))

    # Convert HTML to Markdown
    job_text = html_to_markdown(job_text)

    return Job(
        id=job.get('id', 0),
        hn_id=job.get('hn_id'),
        hn_user=job.get('hn_user'),
        job_text=job_text,
        inserted_at=job.get(
            'inserted_at', datetime.now().replace(microsecond=0)),
        updated_at=job.get('updated_at'),
        applied_at=job.get('applied_at'),
        status=job.get('status', 'n/a'),
    )
