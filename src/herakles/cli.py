import click

from herakles import JiraAuthOAuth, JiraWrapper


@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)


@cli.command()
@click.option("--days-back", default=365, type=int)
def get_bfs(days_back: int):
    query = {
        "and": {
            "project": {"=": "BF"},
            "issueFunction": {"in": {
                "linkedIssuesOf": {
                    "subquery": {
                        "project": {"in": ["TIG", "SERVER", "BACKPORT", "BUILD", "EVG", "MCI"]}},
                    "linktype": "is depended on by",
                }
            }},
            "createdDate": {">": f"-{days_back}d"}
        }
    }

    auth = JiraAuthOAuth.from_yaml_file("config.yml")
    jira = JiraWrapper.connect("https://jira.mongodb.org", auth)
    issues = jira.search(query)
    for issue in issues:
        print(f"{issue.key}: {issue.fields.summary}")


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
