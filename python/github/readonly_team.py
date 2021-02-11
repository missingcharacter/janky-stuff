#!/usr/bin/env python3
import json
from lib.github import Github
from lib.argparse import team_parser


def main(
    org_name: str,
    org_team: str,
    user_token: str
) -> None:
    github = Github()
    oh_repos = {
        repo["name"]: github.ask(
            path=f"/orgs/{org_name}/teams/{org_team}/repos/{org_name}/{repo['name']}",
            body={"permission": "pull"},
            http_verb="PUT",
            token=user_token
        )
        for repo in github.ask(
            path=f"/orgs/{org_name}/repos?per_page=10&page=1",
            token=user_token
            )
    }
    print(json.dumps(oh_repos, indent=4, sort_keys=True))


if __name__ == '__main__':
    args = team_parser(
        description="Give read only access to a given team in a GitHub Organization"
    )
    main(
        org_name=args['organization'],
        org_team=args['team'],
        user_token=args['token']
    )
