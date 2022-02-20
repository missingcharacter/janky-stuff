#!/usr/bin/env bash
# Enable bash's unofficial strict mode
GITROOT=$(git rev-parse --show-toplevel)
# shellcheck disable=SC1090,SC1091
. "${GITROOT}"/bash/lib/strict-mode/strict-mode
# shellcheck disable=SC1090,SC1091
. "${GITROOT}"/cloud/asg-instance-refresh/lib/utils
strictMode

THIS_SCRIPT=$(basename "${0}")
PADDING=$(printf %-${#THIS_SCRIPT}s " ")

function usage () {
  echo "Usage:"
  echo "${THIS_SCRIPT} -s <Pulumi stack name. Examples: k8s-agents, k8s-controllers. REQUIRED>"
  echo "${PADDING} -r <Use this flag to indicate instance should be replaced. if NOT used desired capacity will be decreased>"
  echo "${PADDING} -y <Use this flag to answer 'Yes' to all questions>"
  echo
  echo "Retire instances NOT using current Launch Template version"
  exit 1
}

# Ensure dependencies are present
if ! command -v aws &> /dev/null || ! command -v git &> /dev/null || ! command -v jq &> /dev/null || ! command -v kubectl &> /dev/null; then
  msg_fatal "[-] Dependencies unmet. Please verify that the following are installed and in the PATH: aws, git, jq, kubectl. Check README for requirements"
fi

ACTION='terminate'
ASK='yes'
while getopts ":s:ry" opt; do
  case ${opt} in
    s)
      STACK_NAME=${OPTARG} ;;
    r)
      ACTION='replace' ;;
    y)
      ASK='no' ;;
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

msg_info "I will ${ACTION} instance(s)"

declare -a ASGS
ASGS=()
while IFS= read -r line; do
  if [[ -n ${line} ]]; then
    ASGS+=("${line}")
  fi
done < <(get_asgs "${STACK_NAME}" "${TMP_DIR}")

msg_info "${STACK_NAME} has ${#ASGS[@]} Auto Scaling Group(s)"

IS_K8S_AVAILABLE="$(is_k8s_available)"
msg_info "Is kubernetes reachable? ${IS_K8S_AVAILABLE}"

for asg in "${ASGS[@]}"; do
  retire_instances_in_asg "${asg}" "${TMP_DIR}" "${ACTION}" "${ASK}" "${IS_K8S_AVAILABLE}"
done
