#!/usr/bin/env python3
import argparse
import os
import sys

def base_arguments(
    parser: argparse.ArgumentParser
) -> None:
    parser.add_argument(
        "-t", "--token",
        type=str,
        help="GitHub user token or use environment variable GITHUB_TOKEN"
    )
    parser.add_argument(
        "-o", "--organization",
        type=str,
        help="GitHub Organization name or use environment variable GITHUB_ORGANIZATION"
    )

def base_environment_variables(
    args: argparse.Namespace
) -> None:
    if os.environ.get('GITHUB_TOKEN'):
        args.token = os.environ['GITHUB_TOKEN']
    if os.environ.get('GITHUB_ORGANIZATION'):
        args.organization = os.environ['GITHUB_ORGANIZATION']


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
