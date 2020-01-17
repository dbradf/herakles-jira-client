"""Iterable for jira requests."""
from typing import Any, Callable, Iterator

from jira.client import ResultList


class JiraResponseIterable(object):
    """Object to iterate over paginated jira results."""

    def __init__(
        self,
        results: ResultList,
        transform_fn: Callable[[Any], Any],
        get_more_fn: Callable[[int], ResultList],
    ):
        """
        Create a JiraResponseIterable.

        :param results: Response object from Jira.
        :param transform_fn: Function to transform Jira responses.
        :param get_more_fn: Function to get next page of data.
        """
        self.results = results
        self.transform_fn = transform_fn
        self.get_more_fn = get_more_fn

    def __iter__(self) -> Iterator:
        """Get next item from jira."""
        while True:
            for item in self.results:
                yield self.transform_fn(item)

            # Have we looked at all the results?
            if self.results.startAt + self.results.maxResults > self.results.total:
                break

            self.results = self.get_more_fn(self.results.startAt + self.results.maxResults)

    def __len__(self) -> int:
        """Get the total number of items available."""
        return self.results.total
