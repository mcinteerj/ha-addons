#!/bin/bash
set -e

# Source bashio library
source /usr/lib/bashio/bashio.sh

CONFIG_DIR="/config/.withings_sync_data"
GARMIN_USER=$(bashio::config 'garmin_username')
GARMIN_PASS=$(bashio::config 'garmin_password')

# Ensure config directory exists
mkdir -p "$CONFIG_DIR"

bashio::log.info "Starting Withings Sync..."
bashio::log.info "Config directory: $CONFIG_DIR"

# Check if Withings auth exists
if [ ! -f "$CONFIG_DIR/.withings_user.json" ]; then
    bashio::log.warning "Withings not authenticated. Running interactive setup..."
    bashio::log.warning "Check the addon logs and follow the OAuth flow."
fi

# Run sync
if [ -n "$GARMIN_USER" ] && [ -n "$GARMIN_PASS" ]; then
    bashio::log.info "Syncing to Garmin account: $GARMIN_USER"
    withings-sync \
        --config-folder "$CONFIG_DIR" \
        --garmin-username "$GARMIN_USER" \
        --garmin-password "$GARMIN_PASS"
elif [ -n "$GARMIN_USER" ]; then
    # Password might be cached in session
    bashio::log.info "Using cached Garmin session for: $GARMIN_USER"
    withings-sync \
        --config-folder "$CONFIG_DIR" \
        --garmin-username "$GARMIN_USER"
else
    bashio::log.error "Garmin username not configured!"
    exit 1
fi

bashio::log.info "Sync complete!"
