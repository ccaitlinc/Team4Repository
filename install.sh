#!/usr/bin/env bash
# install.sh - sets up everything needed to run Photon Laser Tag on the Debian VM
set -euo pipefail

cd "$(dirname "$0")"

echo "Step 1/4: Installing system packages (enter the VM password if asked)..."
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip git

echo "Step 2/4: Creating a fresh virtual environment in .venv ..."
rm -rf .venv
python3 -m venv .venv

echo "Step 3/4: Installing Python packages from requirements.txt ..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

echo "Step 4/4: Checking that everything installed correctly ..."
.venv/bin/python -c "import pygame, psycopg2; print('pygame and psycopg2 are installed')"

echo ""
echo "Install complete! Run the app with:"
echo "    .venv/bin/python main.py"