#!/bin/bash
# ============================================================
# SenOS - one-line install for macOS, no "cannot be opened" block
#
#   curl -fsSL https://raw.githubusercontent.com/thayhieumasterai/senos-os/main/packaging/macos/get-senos.sh | bash
#
# Downloads the same SenOS-macOS.dmg the website links to, copies SenOS.app into
# Applications, then runs its first-time install right here in this Terminal window.
# Why no Gatekeeper prompt: macOS only checks files a browser saved (they carry a quarantine
# flag), and the app is not signed with an Apple Developer ID yet. A file curl downloads
# carries no such flag.
# ============================================================
set -euo pipefail

URL="https://github.com/thayhieumasterai/senos-os/releases/download/desktop/SenOS-macOS.dmg"
[ "$(uname -s)" = "Darwin" ] || { echo "This installer is for macOS. On Linux run ./install.sh from the repo."; exit 1; }

TMP="$(mktemp -d)"
MNT=""
cleanup() { [ -n "${MNT}" ] && hdiutil detach -quiet "${MNT}" 2>/dev/null; rm -rf "${TMP}"; }
trap cleanup EXIT

echo ""
echo "  SenOS: dang tai bo cai... (downloading)"
curl -fL --progress-bar -o "${TMP}/SenOS-macOS.dmg" "${URL}"
MNT="$(hdiutil attach -nobrowse -readonly "${TMP}/SenOS-macOS.dmg" | awk -F'\t' '/\/Volumes\//{print $NF}')"
[ -d "${MNT}/SenOS.app" ] || { echo "The disk image has no SenOS.app"; exit 1; }

# /Applications when it is writable (an admin account), else ~/Applications.
DEST="/Applications"
[ -w "${DEST}" ] || { DEST="${HOME}/Applications"; mkdir -p "${DEST}"; }
# Replace only the app bundle; the brain lives in ~/SenOS and is never touched here.
rm -rf "${DEST}/SenOS.app"
cp -R "${MNT}/SenOS.app" "${DEST}/"
xattr -dr com.apple.quarantine "${DEST}/SenOS.app" 2>/dev/null || true
echo "  Da chep SenOS vao ${DEST} (copied to ${DEST})"

APP="${DEST}/SenOS.app"
if [ -d "${HOME}/SenOS/.git" ] && [ -x "${HOME}/SenOS/.venv/bin/python" ]; then
  echo "  SenOS da cai san, dang mo... (already installed, opening)"
  open "${APP}"
  exit 0
fi
# First install in THIS window. stdin is the curl pipe, so give the installer the keyboard
# back: install.sh asks for the SenOS admin account and may ask for the Mac password.
bash "${APP}/Contents/Resources/bootstrap.sh" < /dev/tty
