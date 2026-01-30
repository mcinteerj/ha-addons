# Withings Sync Addon

Syncs weight and body composition data from Withings scales to Garmin Connect.

## Setup

### 1. Configure Garmin Credentials

In the addon configuration, set:
- `garmin_username`: Your Garmin Connect email
- `garmin_password`: Your Garmin Connect password

### 2. Authenticate with Withings

On first run, the addon will prompt for Withings OAuth authentication:

1. Start the addon
2. Check the addon logs
3. Open the URL shown in a browser
4. Authorize the app on Withings website
5. Copy the token from the callback page
6. Paste it into the addon logs (stdin)

This is a one-time setup. Tokens are stored in `/config/.withings_sync_data/`.

### 3. Trigger Sync

**From Automation:**
```yaml
service: hassio.addon_start
data:
  addon: local_withings_sync
```

**Manual:** Click "Start" in the addon UI.

## Automation Example

Sync when weight sensor updates:
```yaml
automation:
  - alias: "Sync Withings to Garmin"
    trigger:
      - platform: state
        entity_id: sensor.withings_weight
    action:
      - service: hassio.addon_start
        data:
          addon: local_withings_sync
```

## Troubleshooting

### Token Expired
Delete `/config/.withings_sync_data/.withings_user.json` and re-run the addon for fresh OAuth.

### Garmin Session Expired  
Delete `/config/.withings_sync_data/.garmin_session/` folder. The addon will re-authenticate using your configured password.

## Data Storage

All credentials and tokens stored in:
```
/config/.withings_sync_data/
├── .withings_user.json   # Withings OAuth tokens
└── .garmin_session/      # Garmin session cache
```
