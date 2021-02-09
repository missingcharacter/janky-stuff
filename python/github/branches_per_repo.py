#!/usr/bin/env python3
import json
from lib.github import ask_github
from lib.argparse import base_parser


def main(
    org_name: str,
    user_token: str
) -> None:
    oh_repos = {
        repo["name"]: len(ask_github(
            path=f"/repos/{org_name}/{repo['name']}/branches?per_page=100&page=1",
            token=user_token
        )["decoded_response"])
        for repo in ask_github(
            path=f"/orgs/{org_name}/repos?per_page=100&page=1",
            token=user_token
        )["decoded_response"]
    }
    print(json.dumps(oh_repos, indent=4, sort_keys=True))


if __name__ == '__main__':
    args = base_parser(
        description="Obtain github repositories and how many branches they each have"
    )
    main(
        org_name=args['organization'],
        user_token=args['token']
    )
