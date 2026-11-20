#!/bin/bash
# ============================================================
# SenOS.app (the one inside SenOS-macOS.dmg) - what a double-click runs.
#
# First run (no SenOS in ~/SenOS yet): opens Terminal on bootstrap.sh, which checks the Mac,
# installs what is missing and starts SenOS. Terminal on purpose: the first install takes
# minutes and may ask for the Mac password once, so the person must SEE what happens.
# Every run after that: bin/senos-start.sh, which only opens the window when SenOS is already
# up and starts it first when it is not. It never restarts a running server.
#
# Unlike the in-repo "SenOS.app" (which must stay inside the repo folder), this bundle can
# live in /Applications: it finds SenOS through SENOS_HOME, default ~/SenOS.
# ============================================================
SENOS_HOME="${SENOS_HOME:-$HOME/SenOS}"
RES="$(cd "$(dirname "$0")/../Resources" && pwd)"

if [ -d "${SENOS_HOME}/.git" ] && [ -x "${SENOS_HOME}/.venv/bin/python" ] && [ -x "${SENOS_HOME}/bin/senos-start.sh" ]; then
  exec "${SENOS_HOME}/bin/senos-start.sh"
fi

# macOS asks once whether "SenOS" may control Terminal. If the person clicks Don't Allow
# (or the prompt never shows), osascript fails and nothing would happen at all: fall back to
# putting the command on the clipboard, opening Terminal, and saying "paste it".
# Not `open -a Terminal bootstrap.sh`: a script copied off the downloaded .dmg carries the
# quarantine flag, and Gatekeeper blocks it when it is opened through LaunchServices.
if ! osascript - "${RES}/bootstrap.sh" "${SENOS_HOME}" <<'AS' >/dev/null 2>&1
on run argv
  tell application "Terminal"
    activate
    do script "SENOS_HOME=" & quoted form of (item 2 of argv) & " bash " & quoted form of (item 1 of argv)
  end tell
end run
AS
then
  # %q escapes spaces and quotes in a form both bash and zsh (the Terminal default) accept.
  printf 'SENOS_HOME=%q bash %q\n' "${SENOS_HOME}" "${RES}/bootstrap.sh" | pbcopy
  open -a Terminal
  osascript -e 'display alert "SenOS" message "Terminal is open. Paste (Cmd+V) and press Enter to install SenOS.\n\nTerminal da mo. Dan (Cmd+V) roi bam Enter de cai SenOS."' >/dev/null 2>&1 || true
fi
