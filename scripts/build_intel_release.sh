#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
PYTHON_ARCH="$("${PYTHON_BIN}" - <<'PY'
import platform
print(platform.machine())
PY
)"

if [[ "${PYTHON_ARCH}" != "x86_64" ]]; then
  echo "Intel builds should be created with an x86_64 Python environment."
  echo "Use an Intel Mac or a true Rosetta/x86_64 Python environment, then rerun."
  exit 1
fi

export PDF_TOOLBOX_TARGET_ARCH="x86_64"
export PDF_TOOLBOX_RELEASE_LABEL="Intel"
export PDF_TOOLBOX_RELEASE_DIR="intel"
export PDF_TOOLBOX_MIN_MACOS="${PDF_TOOLBOX_MIN_MACOS:-11.0}"

"${ROOT_DIR}/scripts/build_macos_release.sh"
