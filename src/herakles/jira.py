"""Wrapper for jira object."""
from __future__ import annotations

from typing import Dict, Optional, Any, Iterable

from jira import JIRA, Issue

from herakles.auth import JiraAuth
from herakles.jql.jql_builder import jql_from_dict
from herakles.util.file_utils import read_yaml_file

DEFAULT_NETWORK_TIMEOUT = 120
DEFAULT_LABEL = "jira_custom_fields"


class JiraWrapper(object):
    """Make calls to Jira."""

    def __init__(self, jira: JIRA, custom_field_map: Optional[Dict] = None):
        """
        Create a wrapper for Jira API.

        :param jira: Jira client to wrap.
        :param custom_field_map: Dictionary mapping custom fields.
        """
        self.jira = jira
        self._custom_field_map = custom_field_map

    @classmethod
    def connect(
        cls,
        jira_server: str,
        auth: JiraAuth,
        network_timeout: int = DEFAULT_NETWORK_TIMEOUT,
        custom_field_map: Optional[Dict] = None,
    ) -> JiraWrapper:
        """
        Connect to the specified Jira instance.

        :param jira_server: Hostname of jira instance.
        :param auth: Authentication information.
        :param network_timeout: Seconds until network timeout.
        :param custom_field_map: Dictionary with mapping of custom fields.
        :return: Wrapper to connect with Jira.
        """
        connect_args = {
            "options": {"server": jira_server},
            "validate": True,
            "timeout": network_timeout,
        }
        connect_args.update(auth.auth_dict())
        jira = JIRA(**connect_args)
        return cls(jira, custom_field_map)

    def add_custom_fields_from_file(self, file_path: str, label: str = DEFAULT_LABEL) -> None:
        """
        Add a mapping of custom fields from a yaml file.

        :param file_path: Yaml file containing custom fields.
        :param label: Key the custom fields are under.
        """
        self._custom_field_map = read_yaml_file(file_path)[label]

    def get_issue(self, jira_issue: str) -> IssueWrapper:
        """
        Retrieve the given jira issue.

        :param jira_issue: Jira issue to query.
        :return: Jira Issue.
        """
        return IssueWrapper(self.jira.issue(jira_issue), self._custom_field_map)

    def search_issues(self, search: Dict, **kwargs: Optional[Dict]) -> Iterable[IssueWrapper]:
        """
        Search for jira issues.

        :param search: Dictionary specifying search parameters.
        :return: Iterable of issues found.
        """
        jql = jql_from_dict(search)
        results = self.jira.search_issues(jql, **kwargs)
        for issue in results:
            yield IssueWrapper(issue, self._custom_field_map)

    def sprints_by_name(self, name: str) -> Dict:
        """
        Get sprint with the given name.

        :param name: Name of sprint to get.
        :return: Sprint with given name.
        """
        return self.jira.sprints_by_name(name)


class IssueWrapper(object):
    """Jira issue."""

    def __init__(self, jira_issue: Issue, custom_field_map: Optional[Dict] = None):
        """
        Create an IssueWrapper for the given issue.

        :param jira_issue: Issue from jira client.
        :param custom_field_map: Dictionary with mappings of custom fields.
        """
        self._issue = jira_issue
        if custom_field_map is None:
            custom_field_map = {}
        self._custom_field_map = custom_field_map

    def __getattr__(self, item: str) -> Any:
        """
        Lookup an attribute on the given issue.

        :param item: attribute to lookup.
        :return: Value of attribute.
        """
        if item in self._custom_field_map:
            return getattr(self, self._custom_field_map[item])

        if hasattr(self._issue, item):
            return getattr(self._issue, item)

        return getattr(self._issue.fields, item)

    @property
    def key(self) -> str:
        """Jira key of issue."""
        return self._issue.key
