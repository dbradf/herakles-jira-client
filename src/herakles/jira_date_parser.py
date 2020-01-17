"""Convert Jira dates to python datetime objects."""
from datetime import datetime

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.000+0000"


def convert_jira_date(jira_date: str) -> datetime:
    """
    Convert the given jira dates to a datetime.

    :param jira_date: Date from jira.
    :return: Datetime of given date.
    """
    return datetime.strptime(jira_date, DATETIME_FORMAT)
