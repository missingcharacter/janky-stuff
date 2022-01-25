#!/usr/bin/env python
import argparse
import boto3
import logging
import sys

from mypy_boto3_ec2 import EC2Client


LOG_LEVEL_STRINGS = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}


def route_is_present(cidr: str, routes: list[dict], log: logging.Logger) -> bool:
    for route in routes:
        if "DestinationCidrBlock" in route.keys():
            if route["DestinationCidrBlock"] == cidr:
                log.info(f"Route {cidr} is present")
                return True
    log.info(f"Route {cidr} is not present")
    return False


def update_route_tables(
    client: EC2Client, vpc_id: str, vgw: str, cidr: str, log: logging.Logger
) -> None:
    try:
        log.info(f"Getting all route tables in VPC {vpc_id}")
        route_tables = {
            table["RouteTableId"]: table["Routes"]
            for page in client.get_paginator("describe_route_tables").paginate(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
            )
            for table in page["RouteTables"]
        }
        for route_table_id, routes in route_tables.items():
            log.info(f"Will create route to {cidr} via {vgw} in route table {route_table_id} if not present")
            if not route_is_present(cidr, routes, log):
                client.create_route(DestinationCidrBlock=cidr, RouteTableId=route_table_id, GatewayId=vgw)
    except Exception as e:
        log.exception(f"Error updating VPC {vpc_id}: {e}")


def set_log_level(args: argparse.Namespace) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s (%(threadName)s) [%(name)s] %(message)s"
    )
    log = logging.getLogger()  # Gets the root logger
    log.setLevel(LOG_LEVEL_STRINGS[args.log_level])


def route_table_parser() -> (dict, logging.Logger):
    parser = argparse.ArgumentParser(description="Updates route tables in a VPC")
    parser.add_argument(
        "--vpc-id",
        type=str,
        required=True,
        help="VPC ID to update route tables in",
    )
    parser.add_argument(
        "--vgw",
        type=str,
        required=True,
        help="VPN Gateway ID",
    )
    parser.add_argument(
        "--cidr",
        type=str,
        required=True,
        help="VPN connection route CIDR",
    )
    parser.add_argument(
        "-l",
        "--log-level",
        type=str,
        default="INFO",
        choices=LOG_LEVEL_STRINGS.keys(),
        help="Set the logging output level",
    )
    args = parser.parse_args(sys.argv[1:])
    set_log_level(args)
    log = logging.getLogger(__name__)
    return vars(args), log


if __name__ == "__main__":
    args, log = route_table_parser()
    client: EC2Client = boto3.client("ec2")
    update_route_tables(client, args["vpc_id"], args["vgw"], args["cidr"], log)
