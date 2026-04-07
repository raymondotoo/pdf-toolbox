#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -n "${PDF_TOOLBOX_DYLD_FRAMEWORK_PATH:-}" ]]; then
  export DYLD_FRAMEWORK_PATH="${PDF_TOOLBOX_DYLD_FRAMEWORK_PATH}"
fi

if [[ -n "${PDF_TOOLBOX_DYLD_LIBRARY_PATH:-}" ]]; then
  export DYLD_LIBRARY_PATH="${PDF_TOOLBOX_DYLD_LIBRARY_PATH}"
fi

if [[ -n "${PYTHON_BIN:-}" ]]; then
  SELECTED_PYTHON="${PYTHON_BIN}"
elif command -v python3.8 >/dev/null 2>&1; then
  SELECTED_PYTHON="$(command -v python3.8)"
else
  SELECTED_PYTHON="python3"
fi

PYTHON_ARCH="$("${SELECTED_PYTHON}" - <<'PY'
import platform
print(platform.machine())
PY
)"
PYTHON_VERSION="$("${SELECTED_PYTHON}" - <<'PY'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}")
PY
)"

if [[ "${PYTHON_ARCH}" != "x86_64" ]]; then
  echo "Legacy Intel builds should be created with an x86_64 Python environment."
  echo "Use an Intel Mac or a true Rosetta/x86_64 Python 3.8 environment, then rerun."
  exit 1
fi

if [[ "${PYTHON_VERSION}" != "3.8" ]]; then
  echo "Legacy Intel builds for macOS 10.14 currently expect Python 3.8."
  echo "Set PYTHON_BIN to an x86_64 Python 3.8 interpreter and rerun."
  exit 1
fi

export PYTHON_BIN="${SELECTED_PYTHON}"
export PDF_TOOLBOX_TARGET_ARCH="x86_64"
export PDF_TOOLBOX_RELEASE_LABEL="Legacy-Intel"
export PDF_TOOLBOX_RELEASE_DIR="legacy-intel"
export PDF_TOOLBOX_MIN_MACOS="${PDF_TOOLBOX_MIN_MACOS:-10.14.0}"
export PDF_TOOLBOX_REQUIREMENTS_FILE="${ROOT_DIR}/requirements-mac-app-legacy.txt"
export PDF_TOOLBOX_BUILD_ENV_NAME=".venv-mac-app-legacy-x86_64"

"${ROOT_DIR}/scripts/build_macos_release.sh"
