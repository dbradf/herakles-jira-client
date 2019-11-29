"""Wrapper for jira object."""
from jira import JIRA, Issue
from typing import Dict, Optional

from herakles.auth import JiraAuth
from herakles.jql.jql_builder import jql_from_dict
from herakles.util.file_utils import read_yaml_file

DEFAULT_NETWORK_TIMEOUT = 120
DEFAULT_LABEL = "jira_custom_fields"


class JiraWrapper(object):
    """Make calls to Jira."""

    def __init__(self, jira: JIRA, custom_field_map: Optional[Dict] = None):
        self._jira = jira
        self._custom_field_map = custom_field_map

    @classmethod
    def connect(
        cls,
        jira_server: str,
        auth: JiraAuth,
        network_timeout: int = DEFAULT_NETWORK_TIMEOUT,
        custom_field_map: Optional[Dict] = None,
    ):
        """
        Connect to the specified Jira instance.

        :param jira_server: Hostname of jira instance.
        :param auth: Authentication information.
        :param network_timeout: Seconds until network timeout.
        :return: Wrapper to connect with Jira.
        """
        options = {"server": jira_server}

        return auth._connect(cls, options, network_timeout, custom_field_map)

    def add_custom_fields_from_file(self, file_path: str, label: str = DEFAULT_LABEL):
        self._custom_field_map = read_yaml_file(file_path)[DEFAULT_LABEL]

    def get_issue(self, jira_issue: str):
        return self._jira.issue(jira_issue)

    def search_issues(self, search: Dict):
        jql = jql_from_dict(search)
        results = self._jira.search_issues(jql)
        for issue in results:
            yield IssueWrapper(issue, self._custom_field_map)


class IssueWrapper(object):
    """Jira issue."""

    def __init__(self, jira_issue: Issue, custom_field_map: Optional[Dict] = None):
        self._issue = jira_issue
        self._custom_field_map = custom_field_map

    def __getattr__(self, item):
        if item in self._custom_field_map:
            return getattr(self, self._custom_field_map[item])

        return getattr(self._issue.fields, item)

    @property
    def key(self):
        return self._issue.key
