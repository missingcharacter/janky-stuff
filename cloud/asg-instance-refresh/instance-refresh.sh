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
  echo "${THIS_SCRIPT} -s <Auto Scaling Group(s) prefix. Examples: k8s-agents, k8s-controllers. REQUIRED>"
  echo "${PADDING} -r <Use this flag to indicate instances should be replaced. if NOT used desired capacity will be decreased>"
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

declare -a INSTANCES
INSTANCES=()
while IFS= read -r i; do
  INSTANCES+=("${i}")
done < <(get_old_instances "${STACK_NAME}" "${TMP_DIR}")

if [[ ${#INSTANCES[@]} -eq 0 ]]; then
  msg_info 'bye bye!'
  exit 0
fi

IS_K8S_AVAILABLE="$(is_k8s_available)"
msg_info "Is kubernetes reachable? ${IS_K8S_AVAILABLE}"

# Cordon all instances
if [[ "${IS_K8S_AVAILABLE}" == 'yes' ]]; then
  for instance in "${INSTANCES[@]}"; do
    cordon_or_drain_instance "${instance}" "${ASK}" 'cordon'
  done
fi

for instance in "${INSTANCES[@]}"; do
  retire_instance "${instance}" "${ACTION}" "${ASK}" "${IS_K8S_AVAILABLE}"
done
