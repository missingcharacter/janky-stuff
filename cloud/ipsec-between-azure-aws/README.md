# Setup IPsec tunnel between AWS and Azure managed by each cloud provider

## Requirements

### Software requirements

- Azure CLI (tested on version `2.32.0`)
  - [MacOS](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-macos)
  - [Linux](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=apt)
- Python `3.10`

### Cloud requirements

- Create Active-Active Virtual Network Gateway in Azure
  - Remember the Public IP Addresses, we will need them later
  - If you do NOT know how to make one read
    [here](https://hackernoon.com/how-to-connect-between-azure-and-aws-with-managed-services-4b03ec334e8a)
- Get VPC ID for the network you want to connect in AWS
- Get the Subnets you want to peer
  - AWS
  - Azure

## IPsec tunnel creation

### Setup virtual environment

```shell
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Create IPsec tunnels

```shell
AWS_PROFILE=your-profile ./create_ipsec.sh --azure-cidr <azure CIDR> \
  --azure-ip <public-ip1> --azure-ip <public-ip2> \
  --azure-location eastus --azure-resource-group <Resource Group> \
  --aws-cidr <aws CIDR> --aws-vpc-id <VPC ID>
```

## `./create_ipsec.sh` help

<!-- markdownlint-disable MD013 -->

```shell
./create_ipsec.sh -h
Usage:
create_ipsec.sh --azure-cidr <Azure subnet to peer, example: 10.10.10.0/16>
                --azure-ip <Public IP Address for the Azure Virtual Network Gateway, can be used multiple times>
                --azure-location <Location for IPSec tunnel, example: eastus>
                --azure-prefix <Azure resources prefix, optional, defaults to 'aws-'>
                --azure-resource-group <Azure resource group where to create resources under>
                --aws-cidr <AWS subnet to peer, example: 10.10.11.0/16>
                --aws-vpc-id <AWS VPC ID>
                --aws-prefix <AWS resources prefix, optional. Defaults to 'azure-'>
                --aws-vgw-name <VGW name, optional. Defaults to azure-to-aws>

Does the following:
  - Creates VPN Gateway (VGW)
  - Attaches VGW to VPC
  - Creates Customer Gateway (CGW) per IP
  - Creates AWS IPsec Tunnel per IP
  - Creates Azure IPsec Tunnel per AWS tunnel IP
  - Adds Azure subnet to all route tables in VPC
```

<!-- markdownlint-enable MD013 -->
