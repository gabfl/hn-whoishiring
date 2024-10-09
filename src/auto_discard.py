import sys

from .models import JobModel

"""
    This utility helps discard any post from a user who previously posted a job that was applied to, interviewed for, or discarded
    While it's currently undocumented, it's a useful tool to keep the job board clean.

    To run this tool, execute the following command:
    python -m src.auto_discard
"""


def get_count():
    """ Get the count of jobs to discard. """

    job_ids = JobModel.get_to_discard()

    return len(job_ids)


def discard_jobs():
    """ Discard all jobs that have been applied to, interviewed at or discarded. """

    job_ids = JobModel.get_to_discard()

    if not job_ids:
        print("No posts to discard.")
        return 0

    count = 0
    for job_id in job_ids:
        res = JobModel.update(job_id, 'discarded')
        print('Discarding job:', job_id)
        if not res:
            print(f"Failed to discard job {job_id}")
            return
        count += 1

    print(f"Discarded {count} jobs.")

    return count


def main():
    counts = get_count()
    print(f"Found {counts} jobs to discard.")

    if counts == 0:
        print("Exiting...")
        sys.exit(0)

    print("This tool will discard any post from a user who previously posted a job that was applied to, interviewed for, or discarded.")
    response = input("Do you want to proceed? (y/N):")

    if response.lower() != 'y':
        print("Exiting...")
        sys.exit(1)

    discard_jobs()


if __name__ == "__main__":
    main()
