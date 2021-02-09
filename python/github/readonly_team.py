#!/usr/bin/env python3
import json
from lib.github import ask_github
from lib.argparse import team_parser


def main(
    org_name: str,
    org_team: str,
    user_token: str
) -> None:
    oh_repos = {
        repo["name"]: ask_github(
            path=f"/orgs/{org_name}/teams/{org_team}/repos/{org_name}/{repo['name']}",
            body={"permission": "pull"},
            http_verb="PUT",
            token=user_token
        )["status_code"]
        for repo in ask_github(
            path=f"/orgs/{org_name}/repos?per_page=100&page=1",
            token=user_token
        )["decoded_response"]
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
