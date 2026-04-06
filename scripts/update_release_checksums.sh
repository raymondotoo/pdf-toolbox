#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_FILE="${ROOT_DIR}/release-assets/checksums.sha256"

cd "${ROOT_DIR}"

find "release-assets" -type f -name "*.zip" -print0 \
  | sort -z \
  | while IFS= read -r -d '' file; do
      shasum -a 256 "${file}"
    done > "${OUTPUT_FILE}"

echo "Wrote ${OUTPUT_FILE}"
