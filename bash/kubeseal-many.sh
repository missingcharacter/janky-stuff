#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

function encrypt() {
  local FILE="${1}"
  local TO_FILE="${FILE/decrypted/secrets}"
  kubeseal -f "${FILE}" -w "${TO_FILE}"
}

for file in $(ls *decrypted*); do
    encrypt "${file}"
done
