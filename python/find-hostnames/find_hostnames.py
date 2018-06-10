#!/usr/bin/env python
"""Reverse DNS lookup for a list of IPs separated by a new line
Should work with python 2.7.15 and 3.6.5"""

import argparse
import json
import os
import socket
import sys

PARSER = argparse.ArgumentParser(
    description="Reverse DNS lookup for a list of IPs separated by a new line"
)
PARSER.add_argument(
    "-i",
    "--input",
    required=True,
    help="Input file with a list of IPs separated by a new line",
)
PARSER.add_argument(
    "-o",
    "--output",
    help="Output file with a list of IP:hostname pairs separated by a new line",
)
ARGS = PARSER.parse_args()

if not os.path.isfile(ARGS.input):
    print("{} does not exist".format(ARGS.input))
    sys.exit(1)

F = open(ARGS.input, "r")
CONTENTS = F.readlines()

IPS_HOSTNAMES = {}

for ip in CONTENTS:
    ip = ip.rstrip()
    if not ip == "":
        try:
            hostname, alias, addresslist = socket.gethostbyaddr(ip)
        except (socket.error, socket.herror, socket.gaierror):
            hostname = ""

        IPS_HOSTNAMES[ip] = hostname
        if ARGS.output is None:
            print("{}:{}".format(ip, hostname))

if ARGS.output:
    with open(ARGS.output, "w") as a_file:
        a_file.write(json.dumps(IPS_HOSTNAMES, indent=2))
