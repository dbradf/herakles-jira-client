"""
Builder for jql queries.

Make it easy to programmatically build jira queries.
"""
from __future__ import annotations

from enum import Enum, auto
from typing import Any, Dict, Iterable, Tuple

COMPARE = {"=", "!=", ">", ">=", "<", "<=", "~", "!~"}
COMPARE_LIST = {"IN", "NOT IN"}
COMPARE_EMPTY = {"IS", "IS NOT"}
CONNECTORS = {"AND", "OR"}
FUNCTIONS = {"linkedissuesof", "membersOf", "issuefieldmatch"}


class _OpType(Enum):
    COMPARE = auto()
    COMPARE_LIST = auto()
    COMPARE_EMPTY = auto()
    CONNECTOR = auto()
    FUNCTION = auto()
    UNKNOWN = auto()

    @classmethod
    def get_type(cls, symbol: str) -> _OpType:
        symbol = symbol.upper()
        if symbol in COMPARE:
            return _OpType.COMPARE
        if symbol in COMPARE_LIST:
            return _OpType.COMPARE_LIST
        if symbol in COMPARE_EMPTY:
            return _OpType.COMPARE_EMPTY
        if symbol in CONNECTORS:
            return _OpType.CONNECTOR
        if symbol in FUNCTIONS:
            return _OpType.FUNCTION
        return _OpType.UNKNOWN


def _single_entry(entry: dict) -> Tuple[Any, Any]:
    assert len(entry) == 1
    return [(k, v) for k, v in entry.items()][0]


def _parse_value(value: Any) -> str:
    if isinstance(value, list):
        return f"({','.join(value)})"

    if isinstance(value, dict):
        key, value = _single_entry(value)
        return _parse_function(key, value)

    return str(value)


def _parse_function(key: str, value: Dict) -> str:
    def arg_joiner() -> str:
        return '", "'

    if key.lower() == "linkedissuesof":
        args = [_parse(value["subquery"])]
        if "linktype" in value:
            args.append(value["linktype"])

        return f'linkedIssuesOf("{arg_joiner().join(args)}")'

    if key.lower() == "issuefieldmatch":
        args = [_parse(value["subquery"]), value["field"], value["value"]]
        return f'issueFieldMatch("{arg_joiner().join(args)}")'
    return ""


def _parse_comparison_list(query: Dict) -> str:
    assert len(query) == 1
    operator, values = _single_entry(query)

    return f"{operator} {_parse_value(values)}"


def _parse_comparison_empty(query: Dict) -> str:
    assert len(query) == 1
    operator, values = _single_entry(query)

    value = _parse_value(values)

    if value.lower() != "empty":
        raise ValueError("'IS' and 'IS NOT' must by follow by 'EMPTY'")

    return f"{operator} {value}"


def _parse_comparison(query: Dict) -> str:
    assert len(query) == 1
    operator, value = _single_entry(query)

    return f"{operator} {value}"


def _parse_operator(query: Dict) -> str:
    operator, values = _single_entry(query)
    key_type = _OpType.get_type(operator)
    if key_type == _OpType.COMPARE:
        return _parse_comparison(query)
    if key_type == _OpType.COMPARE_LIST:
        return _parse_comparison_list(query)
    if key_type == _OpType.COMPARE_EMPTY:
        return _parse_comparison_empty(query)
    return ""


def _parse_field_search(field: str, search: Any) -> str:
    if isinstance(search, dict):
        return f"'{field}' {_parse_operator(search)}"
    return f"'{field}' {_parse_value(search)}"


def _parse_connector(connector: str, values: Iterable) -> str:
    return connector.upper().join([f" ({_parse(item)}) " for item in values])


def _parse_item(key: str, value: Any) -> str:
    key_type = _OpType.get_type(key)
    if key_type == _OpType.COMPARE:
        return _parse_comparison({key: value})
    if key_type == _OpType.CONNECTOR:
        return _parse_connector(key, value)
    return _parse_field_search(key, value)


def _parse(query: Dict) -> str:
    return " ".join([_parse_item(k, v) for k, v in query.items()])


def jql_from_dict(query_dict: Dict) -> str:
    """
    Convert the dictionary to a jql query.

    :param query_dict: Dictionary containing query.
    :return: jql query.
    """
    return _parse(query_dict)
