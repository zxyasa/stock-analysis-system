#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if pgrep -f "stock1.*python|stock1.*main.py" >/dev/null; then
  echo "stock1: running"
  exit 0
fi
echo "stock1: not running"
exit 1
