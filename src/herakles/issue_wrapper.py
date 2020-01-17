"""Wrapper for Jira Issues."""
from datetime import datetime
from typing import Any, Dict, Iterable, Optional

from jira import Issue

from herakles.jira_date_parser import convert_jira_date


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
            return getattr(self, f"customfield_{self._custom_field_map[item]}")

        if hasattr(self._issue, item):
            return getattr(self._issue, item)

        return getattr(self._issue.fields, item)

    @property
    def key(self) -> str:
        """Jira key of issue."""
        return self._issue.key

    @property
    def created(self) -> datetime:
        """Date issue created."""
        return convert_jira_date(self._issue.created)

    @property
    def updated(self) -> datetime:
        """Date issue last updated."""
        return convert_jira_date(self._issue.created)

    def history_iter(self) -> Iterable:
        """Iterate over the changelog history."""
        changelog = self.changelog
        for history in changelog.histories:
            for item in history.items:
                yield HistoryItem(history, item)


class HistoryItem(object):
    """Representation of an item in a history event."""

    def __init__(self, history: Any, item: Any):
        """
        Create a new HistoryItem.

        :param history: History of history item.
        :param item: Item of history item.
        """
        self.history = history
        self.item = item

    @property
    def author_id(self) -> str:
        """ID of the author."""
        return self.history.author.key

    @property
    def created_date(self) -> datetime:
        """Date the history item created."""
        return convert_jira_date(self.history.created)

    def __getattr__(self, attrib: str) -> Any:
        """
        Lookup an attribute on the given HistoryItem.

        :param attrib: attribute to lookup.
        :return: Value of attribute.
        """
        if hasattr(self.item, attrib):
            return getattr(self.item, attrib)

        if hasattr(self.history, attrib):
            return getattr(self.history, attrib)

        raise TypeError(f"No attribute '{attrib}' found.")
