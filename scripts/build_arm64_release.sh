#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export PDF_TOOLBOX_TARGET_ARCH="arm64"
export PDF_TOOLBOX_RELEASE_LABEL="Apple-Silicon"
export PDF_TOOLBOX_RELEASE_DIR="apple-silicon"
export PDF_TOOLBOX_MIN_MACOS="${PDF_TOOLBOX_MIN_MACOS:-12.0}"

"${ROOT_DIR}/scripts/build_macos_release.sh"
