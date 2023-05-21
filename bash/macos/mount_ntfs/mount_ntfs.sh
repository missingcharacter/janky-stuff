#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

function is_ntfs_readonly() {
  local DISK="${1}"
  local RET_VALUE='1'
  local DISK_INFO
  DISK_INFO="$(diskutil info "${DISK}")"
  if grep -q 'File System Personality:   NTFS' <<<"${DISK_INFO}" \
       && grep -q 'Volume Read-Only:          Yes' <<<"${DISK_INFO}"; then
    RET_VALUE='0'
  fi
  return "${RET_VALUE}"
}

function mount_ntfs() {
  local DISK="${1}"
  local DISK_NUMBER="${2}"
  if is_ntfs_readonly "${DISK}"; then
    sudo diskutil unmount "/dev/${DISK}"
    sudo /usr/local/bin/ntfs-3g \
      "/dev/${DISK}" \
      "/Volumes/NTFS${DISK_NUMBER}" \
      -o local \
      -o allow_other \
      -o auto_xattr \
      -o auto_cache \
      -o noappledouble
  fi
}

counter=0
while IFS= read -r disk; do
  if [[ -n ${disk} ]]; then
    mount_ntfs "${disk}" "${counter}"
    ((counter=counter+1))
  fi
done < <(diskutil list external | grep "Windows_NTFS\|Microsoft Basic Data" | rev | awk '{ print $1 }' | rev)
