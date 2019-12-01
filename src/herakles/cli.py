import click

from herakles import JiraAuthOAuth, JiraWrapper


@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)


@cli.command()
def get_bfgs():
    query = {
        "or": [
            {
                "and": [
                    {"project": {"=": "BFG"}},
                    {"resolution": "is empty"},
                    # {"labels": "is empty"},
                    {"summary": {"!~": '"System Failure"'}},
                    {"summary": {"!~": '"Setup Failure"'}},
                    {"summary": {"!~": '"System Unresponsive"'}},
                    {"summary": {"!~": '"System Timed Out"'}},
                    {"Failing Tasks": {"!=": "package"}},
                    {"key": {">=": "BFG-10296"}},
                    {
                        "Evergreen Project": {
                            "in": [
                                "mongodb-mongo-master",
                                "mongodb-mongo-v4.2",
                                "mongodb-mongo-v4.0",
                                "mongodb-mongo-v3.6",
                                "mongodb-mongo-v3.4",
                            ]
                        }
                    },
                ]
            },
            {
                "and": [
                    {
                        "issueFunction": {
                            "in": {
                                "issuefieldmatch": {
                                    "subquery": {
                                        "and": [
                                            {"project": {"=": "BFG"}},
                                            {"resolution": "is empty"},
                                            {"labels": "is empty"},
                                            {"key": {">=": "BFG-10296"}},
                                            {
                                                "Evergreen Project": {
                                                    "in": [
                                                        "mongodb-mongo-master",
                                                        "mongodb-mongo-v4.2",
                                                        "mongodb-mongo-v4.0",
                                                        "mongodb-mongo-v3.6",
                                                        "mongodb-mongo-v3.4",
                                                    ]
                                                }
                                            },
                                        ]
                                    },
                                    "field": "Failing Tasks",
                                    "value": "jepson",
                                }
                            }
                        }
                    },
                    {"summary": {"~": '"System Failure"'}},
                ]
            },
        ]
    }

    auth = JiraAuthOAuth.from_yaml_file("config.yml")
    jira = JiraWrapper.connect("https://jira.mongodb.org", auth)
    jira.add_custom_fields_from_file("config.yml")

    issues = jira.search_issues(query)
    for issue in issues:
        print(f"{issue.key}: {issue.summary}: {issue.score}")


@cli.command()
@click.option("--days-back", default=365, type=int)
def get_bfs(days_back: int):
    query = {
        "and": {
            "project": {"=": "BF"},
            "issueFunction": {
                "in": {
                    "linkedIssuesOf": {
                        "subquery": {
                            "project": {"in": ["TIG", "SERVER", "BACKPORT", "BUILD", "EVG", "MCI"]}
                        },
                        "linktype": "is depended on by",
                    }
                }
            },
            "createdDate": {">": f"-{days_back}d"},
        }
    }

    auth = JiraAuthOAuth.from_yaml_file("config.yml")
    jira = JiraWrapper.connect("https://jira.mongodb.org", auth)
    jira.add_custom_fields_from_file("config.yml")

    issues = jira.search_issues(query)
    for issue in issues:
        print(f"{issue.key}: {issue.summary}: {issue.score}")


@cli.command()
@click.option("--issue", required=True)
def get_issue(issue: str):
    """Get a jira issue."""
    auth = JiraAuthOAuth.from_yaml_file("config.yml")
    jira = JiraWrapper.connect("https://jira.mongodb.org", auth)

    jira_issue = jira.get_issue(issue)
    print(jira_issue.fields.description)


def main():
    """Entry point into commandline."""
    return cli(obj={})
