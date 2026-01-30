#!/bin/bash
set -e

CONFIG_DIR="/config/.withings_sync_data"

# Read config from /data/options.json
GARMIN_USER=$(jq -r '.garmin_username' /data/options.json)
GARMIN_PASS=$(jq -r '.garmin_password' /data/options.json)

# Ensure config directory exists
mkdir -p "$CONFIG_DIR"

echo "[INFO] Starting Withings Sync..."
echo "[INFO] Config directory: $CONFIG_DIR"

# Check if Withings auth exists
if [ ! -f "$CONFIG_DIR/.withings_user.json" ]; then
    echo "[WARN] Withings not authenticated. Running interactive setup..."
    echo "[WARN] Check the addon logs and follow the OAuth flow."
fi

# Run sync
if [ -n "$GARMIN_USER" ] && [ "$GARMIN_USER" != "null" ] && [ -n "$GARMIN_PASS" ] && [ "$GARMIN_PASS" != "null" ]; then
    echo "[INFO] Syncing to Garmin account: $GARMIN_USER"
    withings-sync \
        --config-folder "$CONFIG_DIR" \
        --garmin-username "$GARMIN_USER" \
        --garmin-password "$GARMIN_PASS"
elif [ -n "$GARMIN_USER" ] && [ "$GARMIN_USER" != "null" ]; then
    echo "[INFO] Using cached Garmin session for: $GARMIN_USER"
    withings-sync \
        --config-folder "$CONFIG_DIR" \
        --garmin-username "$GARMIN_USER"
else
    echo "[ERROR] Garmin username not configured!"
    exit 1
fi

echo "[INFO] Sync complete!"
