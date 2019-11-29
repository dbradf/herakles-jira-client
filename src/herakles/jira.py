"""Wrapper for jira object."""
from jira import JIRA
from typing import Dict

from herakles.auth import JiraAuth
from herakles.jql.jql_builder import jql_from_dict

DEFAULT_NETWORK_TIMEOUT = 120


class JiraWrapper(object):
    """Make calls to Jira."""

    def __init__(self, jira: JIRA):
        self._jira = jira

    @classmethod
    def connect(
        cls, jira_server: str, auth: JiraAuth, network_timeout: int = DEFAULT_NETWORK_TIMEOUT
    ):
        """
        Connect to the specified Jira instance.

        :param jira_server: Hostname of jira instance.
        :param auth: Authentication information.
        :param network_timeout: Seconds until network timeout.
        :return: Wrapper to connect with Jira.
        """
        options = {"server": jira_server}

        return auth._connect(cls, options, network_timeout)

    def get_issue(self, jira_issue: str):
        return self._jira.issue(jira_issue)

    def search(self, search: Dict):
        # jql = "(project = BF) AND (issueFunction in linkedIssueOf(\"project in (TIG,SERVER,BACKPORT,BUILD,EVG,MCI)\", \"is depended on by\")) AND (createdDate > -14d)"
        jql = jql_from_dict(search)
         # self._jira.search_issues(jql_from_dict(search))

        return self._jira.search_issues(jql)




