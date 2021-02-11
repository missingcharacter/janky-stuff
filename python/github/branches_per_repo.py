#!/usr/bin/env python3
import json
from lib.github import Github
from lib.argparse import base_parser


def main(
    org_name: str,
    user_token: str
) -> None:
    github = Github()
    oh_repos = {
        repo["name"]: len(github.ask(
            path=f"/repos/{org_name}/{repo['name']}/branches?per_page=10&page=1",
            token=user_token
        ))
        for repo in github.ask(
            path=f"/orgs/{org_name}/repos?per_page=10&page=1",
            token=user_token
        )
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
