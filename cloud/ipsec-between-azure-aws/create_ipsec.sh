#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

THIS_SCRIPT=$(basename "${0}")
PADDING=$(printf %-${#THIS_SCRIPT}s " ")

function usage () {
    echo "Usage:"
    echo "${THIS_SCRIPT} --azure-cidr <Azure subnet to peer, example: 10.10.10.0/16>"
    echo "${PADDING} --azure-ip <Public IP Address for the Azure Virtual Network Gateway, can be used multiple times>"
    echo "${PADDING} --azure-location <Location for IPSec tunnel, example: eastus>"
    echo "${PADDING} --azure-prefix <Azure resources prefix, optional, defaults to 'aws-'>"
    echo "${PADDING} --azure-resource-group <Azure resource group where to create resources under>"
    echo "${PADDING} --aws-cidr <AWS subnet to peer, example: 10.10.11.0/16>"
    echo "${PADDING} --aws-vpc-id <AWS VPC ID>"
    echo "${PADDING} --aws-prefix <AWS resources prefix, optional. Defaults to 'azure-'>"
    echo "${PADDING} --aws-vgw-name <VGW name, optional. Defaults to azure-to-aws>"
    echo
    echo "Does the following:"
    echo "  - Creates VPN Gateway (VGW)"
    echo "  - Attaches VGW to VPC"
    echo "  - Creates Customer Gateway (CGW) per IP"
    echo "  - Creates AWS IPsec Tunnel per IP"
    echo "  - Creates Azure IPsec Tunnel per AWS tunnel IP"
    echo "  - Adds Azure subnet to all route tables in VPC"
    exit 1
}

function azure_ipsec() {
  local NAME RG LOCATION AWS_CIDR GW_IP SHARED_KEY
  NAME="${1}"
  RG="${2}"
  LOCATION="${3}"
  AWS_CIDR="${4}"
  GW_IP="${5}"
  SHARED_KEY="${6}"
  echo "I will create azure IPsec tunnel with name ${NAME}"
  az network local-gateway create --name "${NAME}" --resource-group "${RG}" \
    --gateway-ip-address "${GW_IP}" --location "${LOCATION}" \
    --local-address-prefixes "${AWS_CIDR}"
  az network vpn-connection create --name "${NAME}" --resource-group "${RG}" \
    --vnet-gateway1 "${RG}" --shared-key "${SHARED_KEY}" \
    --local-gateway2 "${NAME}" --location "${LOCATION}"
  az network vpn-connection ipsec-policy add \
    --resource-group "${RG}" --connection-name "${NAME}" \
    --dh-group DHGroup14 --ike-encryption AES256 --ike-integrity SHA256 \
    --ipsec-encryption AES256 --ipsec-integrity SHA256 --pfs-group PFS2048 \
    --sa-lifetime 3600 --sa-max-size 1024
  sleep 3
  az network vpn-connection ipsec-policy list \
    --resource-group "${RG}" --connection-name "${NAME}"
}

function create_temp_dir() {
  case "$(uname)" in
  Linux)
    echo -n "$(mktemp -dt "${THIS_SCRIPT}.XXXX")"
    ;;
  Darwin)
    echo -n "$(/usr/bin/mktemp -dt "${THIS_SCRIPT}")"
    ;;
  *)
    echo "Sorry, $(uname) is not supported." >&2
    exit 1
    ;;
  esac
}

function create_aws_vpn_gateway() {
  local VGW_NAME
  VGW_NAME="${1}"
  VGW_TAG_SPEC="[{\"ResourceType\": \"vpn-gateway\",\"Tags\":[{\"Key\": \
\"Name\",\"Value\": \
\"${VGW_NAME}\"}]}]"
  echo "I will now create VPN Gateway ${VGW_NAME}"
  aws ec2 create-vpn-gateway --type 'ipsec.1' --tag-specifications "${VGW_TAG_SPEC}" \
    --query 'VpnGateway.VpnGatewayId' --output 'text'
}

# Ensure dependencies are present
if ! command -v aws &> /dev/null || ! command -v az &> /dev/null; then
  echo "[-] Dependencies unmet.  Please verify that the following are installed and in the PATH: aws" >&2
  exit 1
fi

if [[ -z ${VIRTUAL_ENV:-""} ]]; then
  echo "[-] Run this script after your sourced a python virtual environment (example: . ./venv/bin/activate)" >&2
  exit 1
fi

while [[ $# -gt 0 ]]; do
  case "${1}" in
    --azure-cidr)
      AZURE_CIDR="${2}"
      shift # past argument
      shift # past value
      ;;
    --azure-ip)
      IPS+=("${2}")
      shift # past argument
      shift # past value
      ;;
    --azure-location)
      AZURE_LOCATION="${2}"
      shift # past argument
      shift # past value
      ;;
    --azure-prefix)
      AZURE_NAME_PREFIX="${2}"
      shift # past argument
      shift # past value
      ;;
    --azure-resource-group)
      AZURE_RG="${2}"
      shift # past argument
      shift # past value
      ;;
    --aws-cidr)
      AWS_CIDR="${2}"
      shift # past argument
      shift # past value
      ;;
    --aws-prefix)
      AWS_NAME_PREFIX="${2}"
      shift # past argument
      shift # past value
      ;;
    --aws-vgw-name)
      VGW_NAME="${2}"
      shift # past argument
      shift # past value
      ;;
    --aws-vpc-id)
      VPC_ID="${2}"
      shift # past argument
      shift # past value
      ;;
    -h|--help)
      usage
      ;;
    -*)
      echo "Unknown option ${1}"
      usage
      ;;
  esac
done

if [[ -z ${IPS:-""} ]] || [[ -z ${AZURE_CIDR:-""} ]] || [[ -z ${VPC_ID:-""} ]] || [[ -z ${AZURE_LOCATION:-""} ]] || [[ -z ${AZURE_RG:-""} ]] || [[ -z ${AWS_CIDR:-""} ]]; then
  usage
fi

if [[ -z ${AWS_NAME_PREFIX:-""} ]]; then
  AWS_NAME_PREFIX='azure'
fi

if [[ -z ${AZURE_NAME_PREFIX:-""} ]]; then
  AZURE_NAME_PREFIX='aws'
fi

if [[ -z ${VGW_NAME:-""} ]]; then
  VGW_NAME='azure-to-aws'
fi

# Create temp directory
TMP_DIR="$(create_temp_dir)"
function cleanup() {
  echo "Deleting ${TMP_DIR}"
  rm -rf "${TMP_DIR}"
}
# Make sure cleanup runs even if this script fails
trap cleanup EXIT

# Get the directory where script is located at
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Create AWS VPN gateway
VGW="$(create_aws_vpn_gateway "${VGW_NAME}")"
echo "ID for ${VGW_NAME} is ${VGW}"

echo "I will now attach VPC ${VPC_ID} to VPN GATEWAY ${VGW}"
aws ec2 attach-vpn-gateway --vpc-id "${VPC_ID}" --vpn-gateway-id "${VGW}"

for ip in "${IPS[@]}"; do
  AWS_VPN="${AWS_NAME_PREFIX}-$(tr  '.'  '-' <<<"${ip}")"
  TMP_JSON="${TMP_DIR}/${AWS_VPN}.json"
  TAG_SPEC="[{\"ResourceType\": \"customer-gateway\",\"Tags\":[{\"Key\": \"Name\",\"Value\": \"${AWS_VPN}\"}]}]"
  echo "I will now create customer gateway ${AWS_VPN}"
  CGW="$(aws ec2 create-customer-gateway --bgp-asn '65000' \
           --type 'ipsec.1' --public-ip "${ip}" \
           --device-name 'Azure' --tag-specifications "${TAG_SPEC}" \
           --query 'CustomerGateway.CustomerGatewayId' --output 'text')"
  echo "I will now create IPsec tunnel ${AWS_VPN}"
  "${SCRIPT_DIR}"/aws_create_vpn_connection.py -n "${AWS_VPN}" --cgw "${CGW}" \
      --vgw "${VGW}" --cidr "${AZURE_CIDR}"
  sleep 3
  aws ec2 describe-vpn-connections --filters "Name=tag:Name,Values=${AWS_VPN}" \
      --query 'VpnConnections[0].Options.TunnelOptions' &> "${TMP_JSON}"
  AZURE_VPN00="${AZURE_NAME_PREFIX}-$(jq -r '.[0].OutsideIpAddress' "${TMP_JSON}" | tr  '.'  '-')"
  AZURE_VPN01="${AZURE_NAME_PREFIX}-$(jq -r '.[1].OutsideIpAddress' "${TMP_JSON}" | tr  '.'  '-')"
  azure_ipsec "${AZURE_VPN00}" "${AZURE_RG}" "${AZURE_LOCATION}" "${AWS_CIDR}" \
    "$(jq -r '.[0].OutsideIpAddress' "${TMP_JSON}")" "$(jq -r '.[0].PreSharedKey' "${TMP_JSON}")"
  azure_ipsec "${AZURE_VPN01}" "${AZURE_RG}" "${AZURE_LOCATION}" "${AWS_CIDR}" \
    "$(jq -r '.[1].OutsideIpAddress' "${TMP_JSON}")" "$(jq -r '.[1].PreSharedKey' "${TMP_JSON}")"
done

# I'm doing this at the end be cause the route table will NOT be updated
# until after the VPN Gateway is attached to the VPC
echo "I will now add ${AZURE_CIDR} to all route tables in ${VPC_ID}"
"${SCRIPT_DIR}"/aws_update_route_tables.py --vpc-id "${VPC_ID}" --vgw "${VGW}" \
    --cidr "${AZURE_CIDR}"
