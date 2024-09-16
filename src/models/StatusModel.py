from pydantic import BaseModel


class Status(BaseModel):
    value: str
    label: str


def get_all():
    """ Returns all accepted statuses """

    statuses = [
        Status(value='new', label='New'),
        Status(value='applied', label='Applied'),
        Status(value='discarded', label='Discarded'),
        Status(value='interviewed', label='In interview'),
        Status(value='rejected-pre', label='Rejected (pre-interview)'),
        Status(value='rejected-post', label='Rejected (post-interview)'),
    ]

    return statuses
