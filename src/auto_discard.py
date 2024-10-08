import sys

from .models import JobModel


def discard_jobs():
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
    prompt = "This tool will discard any post by a user previouly applied to, interviewed at or discarded. Do you want to proceed? (y/N): "
    response = input(prompt)

    if response.lower() != 'y':
        print("Exiting...")
        sys.exit(1)

    discard_jobs()


if __name__ == "__main__":
    main()
