#!/usr/bin/env python3
import json
import logging
from lib.github import Github
from lib.argparse import deploykey_parser


class DeployKey:
    log = logging.getLogger(__name__)


    def __init__(
        self,
        user_token: str,
        github_url: str = "https://api.github.com"
    ) -> None:
        self.github_url = github_url
        self.github = Github(github_url=self.github_url)
        self.user_token = user_token


    def add(
        self,
        key_name: str,
        org_name: str,
        public_key: str,
        repo_name: str,
        read_only: bool = True
    ) -> str:
        self.github.ask(
            path=f"/repos/{org_name}/{repo_name}/keys",
            body={"title": key_name, "key": public_key, "read_only": read_only},
            http_verb="POST",
            token=self.user_token
        )


    def is_key_in_repo(
        self,
        key_name: str,
        org_name: str,
        public_key: str,
        repo_name: str,
    ) -> bool:
        for key in self.github.ask(
            path=f"/repos/{org_name}/{repo_name}/keys?per_page=10&page=1",
            token=self.user_token
        ):
        if any(key_name == item["title"] or public_key == item["key"] for item in keys):
            return True
        else:
            return False


def main(
    key_name: str,
    org_name: str,
    public_key: str,
    user_token: str
) -> None:
    github = Github()
    oh_repos = {
        repo["name"]: github.ask(
            path=f"/orgs/{org_name}/teams/{org_team}/repos/{org_name}/{repo['name']}",
            body={"title": key_name, "key": public_key, "read_only": True},
            http_verb="POST",
            token=user_token
        )
        for repo in github.ask(
            path=f"/orgs/{org_name}/repos?per_page=10&page=1",
            token=user_token
        )
    }
    print(json.dumps(oh_repos, indent=4, sort_keys=True))


if __name__ == '__main__':
    args = deploykey_parser(
        description="Give read only access to a public key in a GitHub Organization"
    )
    main(
        key_name=args['key_name'],
        org_name=args['organization'],
        public_key=args['public_key'],
        user_token=args['token']
    )
