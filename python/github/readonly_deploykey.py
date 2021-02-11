#!/usr/bin/env python3
import json
import logging
from lib.github import Github
from lib.argparse import deploykey_parser


class DeployKey:
    log = logging.getLogger(__name__)


    def __init__(
        self,
        key_name: str,
        org_name: str,
        public_key: str,
        user_token: str,
        github_url: str = "https://api.github.com"
    ) -> None:
        self.key_name = key_name
        self.org_name = org_name
        self.public_key = public_key
        self.user_token = user_token
        self.github_url = github_url
        self.github = Github(github_url=self.github_url)


    def add(self, repo_name: str, read_only: bool = True) -> dict:
        self._removing_key_if_exists(repo_name=repo_name)
        self.log.info("I will try to add key %s with value %s to repo %s", self.key_name, self.public_key, repo_name)
        return self.github.ask(
            path=f"/repos/{self.org_name}/{repo_name}/keys",
            body={"title": self.key_name, "key": self.public_key, "read_only": read_only},
            http_verb="POST",
            token=self.user_token
        )


    def _removing_key_if_exists(self, repo_name: str) -> None:
        self.log.info("Checking if key %s exists in repository %s", self.key_name, repo_name)
        for key in self.github.ask(
            path=f"/repos/{self.org_name}/{repo_name}/keys?per_page=10&page=1",
            token=self.user_token
        ):
            self.log.info("key id: [%s] has name %s or public key %s, I will remove it", key["id"], self.key_name, self.public_key)
            self.github.ask(
                path=f"{self.path}/{key['id']}",
                http_verb="DELETE",
                token=self.user_token
            )


def main(
    key_name: str,
    org_name: str,
    public_key: str,
    user_token: str
) -> None:
    github = Github()
    deploy_key = DeployKey(
        key_name=key_name,
        org_name=org_name,
        public_key=public_key,
        user_token=user_token
    )
    #oh_repos = {
    #    repo["name"]: deploy_key.add(repo_name=repo["name"])
    #    for repo in github.ask(
    #        path=f"/orgs/{org_name}/repos?per_page=10&page=1",
    #        token=user_token
    #    )
    #}
    oh_repos = {
        repo["name"]: deploy_key.add(repo_name=repo["name"])
        for repo in [
            {
                "name": "***REMOVED***"
            },
            {
                "name": "***REMOVED***"
            }
        ]
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
