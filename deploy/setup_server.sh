#!/usr/bin/env bash
set -euo pipefail

APP_DIR=/opt/ecotech-parser
REPO_URL=${1:-""}

if [[ -z "$REPO_URL" ]]; then
  echo "Usage: $0 <repo_url>"
  exit 1
fi

sudo apt-get update
sudo apt-get install -y python3 python3-venv git

if [[ ! -d "$APP_DIR/.git" ]]; then
  sudo git clone "$REPO_URL" "$APP_DIR"
else
  sudo git -C "$APP_DIR" pull --ff-only
fi

sudo chown -R ubuntu:ubuntu "$APP_DIR"
cd "$APP_DIR"

python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
if [[ -s requirements.txt ]]; then
  pip install -r requirements.txt
fi

sudo cp deploy/ecotech-parser.service /etc/systemd/system/ecotech-parser.service
sudo cp deploy/ecotech-parser.timer /etc/systemd/system/ecotech-parser.timer
sudo systemctl daemon-reload
sudo systemctl enable --now ecotech-parser.timer
sudo systemctl start ecotech-parser.service
