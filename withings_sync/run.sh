#!/usr/bin/with-contenv bashio
set -e

bashio::log.info "Starting Withings Sync addon..."
bashio::log.info "Data directory: /data"

# Start the web server
exec python3 /server.py
