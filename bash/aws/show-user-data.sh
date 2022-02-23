#!/usr/bin/env bash
# Enable bash's unofficial strict mode
GITROOT=$(git rev-parse --show-toplevel)
# shellcheck disable=SC1090,SC1091
. "${GITROOT}"/bash/lib/strict-mode/strict-mode
# shellcheck disable=SC1090,SC1091
. "${GITROOT}"/bash/aws/lib/utils
strictMode

THIS_SCRIPT=$(basename "${0}")
PADDING=$(printf %-${#THIS_SCRIPT}s " ")

function usage () {
  echo "Usage:"
  echo "${THIS_SCRIPT} -s <Pulumi stack name. Examples: k8s-agents, k8s-controllers. REQUIRED>"
  echo "${PADDING} -f <Use this flag to pick the first Auto Scaling Group>"
  echo
  echo "Print base64 decoded and gunzip decompressed user-data for a given stack"
  exit 1
}

# Ensure dependencies are present
if ! command -v aws &> /dev/null || ! command -v git &> /dev/null || \
   ! command -v jq &> /dev/null || ! command -v base64 &> /dev/null || \
   ! command -v gunzip &> /dev/null; then
  msg_fatal "[-] Dependencies unmet. Please verify that the following are installed and in the PATH: aws, base64, git, gunzip, jq. Check README for requirements"
fi

FIRST='no'
while getopts ":fs:" opt; do
  case ${opt} in
    f)
      FIRST='yes' ;;
    s)
      STACK_NAME=${OPTARG} ;;
    *)
      usage ;;
  esac
done

if [[ -z ${STACK_NAME:-""} ]] ; then
  usage
fi

# Create temp directory
TMP_DIR="$(create_temp_dir "${THIS_SCRIPT}")"
function cleanup() {
  echo "Deleting ${TMP_DIR}"
  rm -rf "${TMP_DIR}"
}
# Make sure cleanup runs even if this script fails
trap cleanup EXIT


ASG_FILE="$(select_asg "${STACK_NAME}" "${TMP_DIR}" "${FIRST}")"

get_user_data "${ASG_FILE}" "${TMP_DIR}"
