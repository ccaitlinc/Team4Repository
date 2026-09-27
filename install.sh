#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is required. On Debian: sudo apt install python3 python3-venv" >&2
    exit 1
fi

if ! python3 -m venv --help >/dev/null 2>&1; then
    echo "Python venv is required. On Debian: sudo apt install python3-venv" >&2
    exit 1
fi

python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

echo "Installed Python dependencies in .venv. Run: .venv/bin/python main.py"
