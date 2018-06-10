#!/usr/bin/env python
# Should work with python 2.7.15 and 3.6.5

import argparse
import json
import os
import socket
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", required=True,
                    help="Input file with a list of IPs separated by a new line")
parser.add_argument("-o", "--output",
                    help="Output file with a list of IP:hostname pairs separated by a new line")
args = parser.parse_args()

if not os.path.isfile(args.input):
    print("{} does not exist".format(args.input))
    sys.exit(1)

f = open(args.input, "r")
contents = f.readlines()

ips_hostnames = {}

for ip in contents:
    ip = ip.rstrip()
    if not ip == '':
        try:
            hostname, alias, addresslist = socket.gethostbyaddr(ip)
        except (socket.error, socket.herror, socket.gaierror):
            hostname = ''

        ips_hostnames[ip] = hostname
        if args.output == None:
            print("{}:{}".format(ip, hostname))

if args.output:
    with open(args.output, 'w') as file:
        file.write(json.dumps(ips_hostnames, indent=2))
