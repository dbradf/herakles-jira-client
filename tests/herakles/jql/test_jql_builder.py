

import herakles.jql.jql_builder as under_test


def test_operators():
    query = {
        "project": {"=": "BF"}
    }

    assert under_test.jql_from_dict(query) == "'project' = BF"


def test_combinations():
    query = {
        "and": [
            {"project": {"=": "BF"}},
            {"createdDate": {">": "-365d"}},
        ]
    }

    jql = under_test.jql_from_dict(query)

    assert jql.strip() == "('project' = BF) AND ('createdDate' > -365d)"


def test_functions():
    query = {
        "and": [
            {"project": {"=": "BF"}},
            {"issueFunction": {"in": {
                "linkedIssueOf": {
                    "subquery": {
                        "project": {"in": ["TIG", "SERVER", "BACKPORT", "BUILD", "EVG", "MCI"]}},
                    "linktype": "is depended on by",
                }
            }}},
            {"createdDate": {">": "-365d"}},
        ]
    }

    jql = under_test.jql_from_dict(query)

    assert "('project' = BF)" in jql
    assert "('createdDate' > -365d)" in jql
    assert "AND" in jql
