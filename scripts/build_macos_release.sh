#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_NAME="${PDF_TOOLBOX_APP_NAME:-PDF Toolbox}"
APP_NAME_SLUG="${PDF_TOOLBOX_APP_NAME_SLUG:-PDF-Toolbox}"
VERSION="${PDF_TOOLBOX_VERSION:-$(<"${ROOT_DIR}/VERSION")}"
TARGET_ARCH="${PDF_TOOLBOX_TARGET_ARCH:-$(uname -m)}"
RELEASE_LABEL="${PDF_TOOLBOX_RELEASE_LABEL:-${TARGET_ARCH}}"
RELEASE_DIR="${PDF_TOOLBOX_RELEASE_DIR:-${TARGET_ARCH}}"
MIN_MACOS="${PDF_TOOLBOX_MIN_MACOS:-12.0}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
REQUIREMENTS_FILE="${PDF_TOOLBOX_REQUIREMENTS_FILE:-${ROOT_DIR}/requirements-mac-app.txt}"
BUILD_ENV="${ROOT_DIR}/${PDF_TOOLBOX_BUILD_ENV_NAME:-.venv-mac-app-${TARGET_ARCH}}"
APP_BUNDLE="${ROOT_DIR}/dist/${APP_NAME}.app"
FRAMEWORKS_DIR="${APP_BUNDLE}/Contents/Frameworks"
RESOURCES_DIR="${APP_BUNDLE}/Contents/Resources"
DIST_ZIP="${ROOT_DIR}/dist/${APP_NAME_SLUG}-macOS-${RELEASE_LABEL}-${VERSION}.zip"
STAGED_ZIP="${ROOT_DIR}/release-assets/${RELEASE_DIR}/${APP_NAME_SLUG}-macOS-${RELEASE_LABEL}-${VERSION}.zip"

if [[ -n "${PDF_TOOLBOX_DYLD_FRAMEWORK_PATH:-}" ]]; then
  export DYLD_FRAMEWORK_PATH="${PDF_TOOLBOX_DYLD_FRAMEWORK_PATH}"
fi

if [[ -n "${PDF_TOOLBOX_DYLD_LIBRARY_PATH:-}" ]]; then
  export DYLD_LIBRARY_PATH="${PDF_TOOLBOX_DYLD_LIBRARY_PATH}"
fi

copy_if_exists() {
  local source_path="$1"
  if [[ ! -f "${source_path}" ]]; then
    echo "Skipping missing framework: ${source_path}"
    return
  fi

  local target_name
  target_name="$(basename "${source_path}")"
  cp "${source_path}" "${FRAMEWORKS_DIR}/${target_name}"
  chmod u+w "${FRAMEWORKS_DIR}/${target_name}"
}

copy_dir_if_exists() {
  local source_path="$1"
  local target_path="$2"
  if [[ ! -d "${source_path}" ]]; then
    echo "Skipping missing resource directory: ${source_path}"
    return
  fi

  rm -rf "${target_path}"
  cp -R "${source_path}" "${target_path}"
}

python_value() {
  local code="$1"
  "${BUILD_ENV}/bin/python" - <<PY
${code}
PY
}

if [[ ! -d "${BUILD_ENV}" ]]; then
  "${PYTHON_BIN}" -m venv "${BUILD_ENV}"
fi

if [[ "${PDF_TOOLBOX_UPGRADE_PIP:-0}" == "1" ]]; then
  "${BUILD_ENV}/bin/python" -m pip install --upgrade pip
fi
"${BUILD_ENV}/bin/pip" install -r "${REQUIREMENTS_FILE}"

export PDF_TOOLBOX_APP_NAME="${APP_NAME}"
export PDF_TOOLBOX_VERSION="${VERSION}"
export PDF_TOOLBOX_MIN_MACOS="${MIN_MACOS}"

"${BUILD_ENV}/bin/python" "${ROOT_DIR}/setup.py" py2app

mkdir -p "${FRAMEWORKS_DIR}" "${RESOURCES_DIR}" "${ROOT_DIR}/release-assets/${RELEASE_DIR}"

PYTHON_PREFIX="$(python_value 'import sys; print(sys.prefix)')"
SITE_PACKAGES="$(python_value 'import sysconfig; print(sysconfig.get_paths()["purelib"])')"

copy_if_exists "${PYTHON_PREFIX}/lib/libffi.8.dylib"
copy_if_exists "${PYTHON_PREFIX}/lib/libexpat.1.dylib"
copy_if_exists "${PYTHON_PREFIX}/lib/libbz2.dylib"
copy_if_exists "${PYTHON_PREFIX}/lib/liblzma.5.dylib"
copy_if_exists "${PYTHON_PREFIX}/lib/libssl.3.dylib"
copy_if_exists "${PYTHON_PREFIX}/lib/libcrypto.3.dylib"
copy_if_exists "${PYTHON_PREFIX}/lib/libz.1.dylib"
copy_if_exists "${PYTHON_PREFIX}/lib/libtk8.6.dylib"
copy_if_exists "${PYTHON_PREFIX}/lib/libtcl8.6.dylib"
copy_dir_if_exists "${PYTHON_PREFIX}/lib/tcl8.6" "${RESOURCES_DIR}/tcl8.6"
copy_dir_if_exists "${PYTHON_PREFIX}/lib/tk8.6" "${RESOURCES_DIR}/tk8.6"
copy_if_exists "${SITE_PACKAGES}/pymupdf/libmupdf.dylib"
copy_if_exists "${SITE_PACKAGES}/pymupdf/libmupdfcpp.so"

codesign --force --deep --sign - "${APP_BUNDLE}"

if [[ "${PDF_TOOLKIT_RUN_SELFTEST:-1}" == "1" ]]; then
  PDF_TOOLKIT_SELFTEST=1 "${APP_BUNDLE}/Contents/MacOS/${APP_NAME}"
fi

ditto -c -k --sequesterRsrc --keepParent "${APP_BUNDLE}" "${DIST_ZIP}"
cp "${DIST_ZIP}" "${STAGED_ZIP}"

echo
echo "Build finished."
echo "App bundle: ${APP_BUNDLE}"
echo "Zip file: ${DIST_ZIP}"
echo "Release asset: ${STAGED_ZIP}"
