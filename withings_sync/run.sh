#!/bin/bash
set -e

CONFIG_DIR="/config/.withings_sync_data"
mkdir -p "$CONFIG_DIR"

echo "[INFO] Starting Withings Sync addon..."
echo "[INFO] Config directory: $CONFIG_DIR"

# Start the web server
exec python3 /server.py
