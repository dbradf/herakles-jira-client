# herakles jira tool

Tools for working with the [Jira API](https://jira.readthedocs.io/en/master/index.html).


## Usage

### Initialize

```python
from herakles import JiraAuthBasic, JiraWrapper
auth = JiraAuthBasic("username", "password")
jira = JiraWrapper.connect("https://server.jira.com", auth)

# optional add map of custom fields.
jira.add_custom_fields_from_file("custom_fields.yml")
```

### Use jql builder to programmatically build jql queries

See how many tickets a user resolved in the past number days:
```python
query = {
            "and": [
                {"assignee": {"=": team_member}},
                {"resolved": {">": f"-{days}d"}},
                {"project": {"not in": ["'Unrelated Project'"]}},
            ]
        }
```

## Contributors Guide

### Testing

Testing is done via pytest.

```
$ pip install -r requirements.txt
$ pytest
```

To get code coverage information, you can run pytest directly.

```
$ pip install -r requirements.txt
$ pytest --cov=src --cov-report=html
```

This will generate an html coverage report in `htmlcov/` directory.
