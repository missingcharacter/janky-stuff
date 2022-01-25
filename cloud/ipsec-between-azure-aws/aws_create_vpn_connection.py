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


tunel_opts = {
    "Phase1EncryptionAlgorithms": [{"Value": "AES256"}],
    "Phase2EncryptionAlgorithms": [{"Value": "AES256"}],
    "Phase1IntegrityAlgorithms": [{"Value": "SHA2-256"}],
    "Phase2IntegrityAlgorithms": [{"Value": "SHA2-256"}],
    "Phase1DHGroupNumbers": [{"Value": 14}],
    "Phase2DHGroupNumbers": [{"Value": 14}],
    "IKEVersions": [{"Value": "ikev2"}],
}


def create_vpn(
    client: EC2Client, name: str, cgw: str, vgw: str, cidr: str, log: logging.Logger
) -> None:
    try:
        vpn = client.create_vpn_connection(
            CustomerGatewayId=cgw,
            Type="ipsec.1",
            VpnGatewayId=vgw,
            DryRun=False,
            Options={
                "StaticRoutesOnly": True,
                "TunnelInsideIpVersion": "ipv4",
                "TunnelOptions": [tunel_opts, tunel_opts],
            },
        )
        vpn_id = vpn["VpnConnection"]["VpnConnectionId"]
        log.info(
            f"VPN ID {vpn_id} for {name} created, but no Name tag has been created"
        )
        client.create_vpn_connection_route(
            DestinationCidrBlock=cidr, VpnConnectionId=vpn_id
        )
        log.info(f"VPN connection route cidr {cidr} has been associated to {vpn_id}")
        client.create_tags(
            DryRun=False,
            Resources=[
                vpn_id,
            ],
            Tags=[
                {"Key": "Name", "Value": name},
            ],
        )
        log.info(f"VPN ID {vpn_id} now has Tag Name {name} ")
    except Exception as e:
        log.exception(f"Error creating VPN {name}: {e}")


def set_log_level(args: argparse.Namespace) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s (%(threadName)s) [%(name)s] %(message)s"
    )
    log = logging.getLogger()  # Gets the root logger
    log.setLevel(LOG_LEVEL_STRINGS[args.log_level])


def vpn_parser() -> (dict, logging.Logger):
    parser = argparse.ArgumentParser(description="Creates an AWS managed IPSec Tunnel")
    parser.add_argument(
        "-n",
        "--vpn-name",
        type=str,
        required=True,
        help="Name for the VPN connection",
    )
    parser.add_argument(
        "--cgw",
        type=str,
        required=True,
        help="Customer Gateway ID",
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
    args, log = vpn_parser()
    client: EC2Client = boto3.client("ec2")
    create_vpn(client, args["vpn_name"], args["cgw"], args["vgw"], args["cidr"], log)
