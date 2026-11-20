#!/bin/bash
# Double-click in Finder to start SenOS and open the dashboard.
cd "$(dirname "$0")" || exit 1
bash "bin/senos-start.sh"
echo ""
echo "SenOS is running at http://127.0.0.1:7777"
echo "This window can be closed - the server keeps running in the background."
