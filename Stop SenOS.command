#!/bin/bash
# Double-click in Finder to stop SenOS.
cd "$(dirname "$0")" || exit 1
bash "bin/senos-stop.sh"
echo ""
echo "You can close this window."
