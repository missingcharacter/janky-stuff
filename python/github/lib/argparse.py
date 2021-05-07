#!/usr/bin/env python3
import argparse
import logging
import os
import sys

from lib.github import Github


LOG_LEVEL_STRINGS = {
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG
}


def set_log_level(
    args: argparse.Namespace
) -> None:
    logging.basicConfig(format="%(asctime)s %(levelname)s (%(threadName)s) [%(name)s] %(message)s")
    log = logging.getLogger()  # Gets the root logger
    log.setLevel(LOG_LEVEL_STRINGS[args.log_level])


def base_arguments(
    parser: argparse.ArgumentParser
) -> None:
    parser.add_argument(
        "-l", "--log-level",
        type=str,
        default='INFO',
        choices=LOG_LEVEL_STRINGS.keys(),
        help="Set the logging output level"
    )
    parser.add_argument(
        "-o", "--organization",
        type=str,
        help="GitHub Organization name or use environment variable GITHUB_ORGANIZATION"
    )
    parser.add_argument(
        "-t", "--token",
        type=str,
        help="GitHub user token or use environment variable GITHUB_TOKEN"
    )

def base_environment_variables(
    args: argparse.Namespace
) -> None:
    if os.environ.get('GITHUB_ORGANIZATION'):
        args.organization = os.environ['GITHUB_ORGANIZATION']
    if os.environ.get('GITHUB_TOKEN'):
        args.token = os.environ['GITHUB_TOKEN']
    if os.environ.get('LOG_LEVEL'):
        args.log_level = os.environ['LOG_LEVEL']
    set_log_level(args)
    log = logging.getLogger(__name__)
    gh = Github()
    user = gh.ask(
        path='/user',
        token=args.token
    )
    log.debug("You are currently acting as login %s of type %s from company %s, is site_admin: %s", user['login'], user['type'], user['company'], user['site_admin'])


def base_parser(
    description: str
) -> dict:
    parser = argparse.ArgumentParser(
        description=description
    )
    base_arguments(parser=parser)
    args = parser.parse_args(sys.argv[1:])
    base_environment_variables(args)
    return vars(args)

def deploykey_parser(
    description: str
) -> dict:
    parser = argparse.ArgumentParser(
        description=description
    )
    base_arguments(parser=parser)
    parser.add_argument(
        "-n", "--key-name",
        type=str,
        help="A name for the deploy key within GitHub repo or use environment variable GITHUB_KEY_NAME"
    )
    parser.add_argument(
        "-k", "--public-key",
        type=str,
        help="The contents of the public key to add to all GitHub repos or use environment variable GITHUB_PUBLIC_KEY"
    )
    args = parser.parse_args(sys.argv[1:])
    base_environment_variables(args)
    if os.environ.get('GITHUB_KEY_NAME'):
        args.key_name = os.environ['GITHUB_KEY_NAME']
    if os.environ.get('GITHUB_PUBLIC_KEY'):
        args.public_key = os.environ['GITHUB_PUBLIC_KEY']
    return vars(args)

def team_parser(
    description: str
) -> dict:
    parser = argparse.ArgumentParser(
        description=description
    )
    base_arguments(parser=parser)
    parser.add_argument(
        "--team",
        type=str,
        help="Team name within GitHub org token or use environment variable GITHUB_TEAM"
    )
    args = parser.parse_args(sys.argv[1:])
    base_environment_variables(args)
    if os.environ.get('GITHUB_TEAM'):
        args.team = os.environ['GITHUB_TEAM']
    return vars(args)
