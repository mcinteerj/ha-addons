# Withings Sync Home Assistant Addon

[![License](https://img.shields.io/github/license/mcinteerj/withings-sync-ha-addon)](LICENSE)

Home Assistant addon that syncs Withings weight/body composition data to Garmin Connect.

## Features

- Syncs weight, body fat %, muscle mass, bone mass, hydration
- Uses [withings-sync](https://github.com/jaroslawhartman/withings-sync) under the hood
- Runs on-demand (no background process)
- Persistent OAuth tokens (one-time setup)
- Garmin session caching (fewer logins)

## Installation

### As Local Addon

1. Copy this repository to `/config/addons/withings_sync/` on your HA instance
2. Go to **Settings → Add-ons → Add-on Store**
3. Click **⋮ → Check for updates** (top right)
4. Find "Withings Sync" under **Local add-ons**
5. Install and configure

### From Repository (coming soon)

Add repository URL to HA addon store.

## Configuration

| Option | Required | Description |
|--------|----------|-------------|
| `garmin_username` | Yes | Garmin Connect email |
| `garmin_password` | Yes | Garmin Connect password |

## Usage

See [DOCS.md](DOCS.md) for setup and automation examples.

## Credits

- [withings-sync](https://github.com/jaroslawhartman/withings-sync) by @jaroslawhartman
