from typing import List, Optional
from unittest.mock import MagicMock

import herakles.jira_response_iterable as under_test


def create_mock_results(items: List, total: Optional[int] = None, start_at: int = 0):
    if not total:
        total = len(items)

    results = MagicMock(startAt=start_at, maxResults=50, total=total)
    results.__iter__.return_value = [item for item in items]
    return results


class TestJiraResponseIterable:
    def test_no_items(self):
        results = create_mock_results([])

        jira_iter = under_test.JiraResponseIterable(results, lambda x: x, lambda x: x)

        count = 0
        for i, _ in enumerate(jira_iter):
            count = i

        assert count == 0

    def test_less_than_max_results_items(self):
        result_list = [x for x in range(10)]
        results = create_mock_results(result_list)

        jira_iter = under_test.JiraResponseIterable(results, lambda x: x, lambda x: x)

        items_seen = [x for x in jira_iter]

        assert result_list == items_seen

    def test_more_than_max_results_items(self):
        result_list_0 = [x for x in range(50)]
        result_list_1 = [x for x in range(25)]
        total_items = len(result_list_0) + len(result_list_1)

        results_0 = create_mock_results(result_list_0, total=total_items)
        results_1 = create_mock_results(
            result_list_1, total=total_items, start_at=len(result_list_0)
        )

        jira_iter = under_test.JiraResponseIterable(results_0, lambda x: x, lambda _: results_1)

        items_seen = [x for x in jira_iter]

        assert result_list_0 + result_list_1 == items_seen
