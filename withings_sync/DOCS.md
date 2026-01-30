# Withings Sync Addon

Syncs weight and body composition data from Withings scales to Garmin Connect.

## Setup

### 1. Configure Garmin Credentials

In the addon **Configuration** tab, set:
- `garmin_username`: Your Garmin Connect email
- `garmin_password`: Your Garmin Connect password

### 2. Start the Addon

Click **Start**. The addon will run continuously to serve the web UI.

### 3. Authenticate with Withings

1. Open the addon **Web UI** (click "OPEN WEB UI" button)
2. Click **"Authorize Withings"** - opens Withings login in new tab
3. Log in and authorize the app
4. You'll be redirected to a page showing your authorization code
5. Copy the code and paste it into the addon web UI
6. Click **"Save Code"**
7. Click **"Sync Now"** to complete authentication and sync

## Usage

### Manual Sync

Open the Web UI and click **"Sync Now"**.

### Automated Sync

Create an automation to trigger sync when weight updates:

```yaml
automation:
  - alias: "Sync Withings to Garmin"
    trigger:
      - platform: state
        entity_id: sensor.withings_weight_kg
    action:
      - service: hassio.addon_stdin
        data:
          addon: local_withings_sync
          input: sync
```

Or on a schedule:

```yaml
automation:
  - alias: "Daily Withings Sync"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: hassio.addon_stdin
        data:
          addon: local_withings_sync
          input: sync
```

## Troubleshooting

### Re-authenticate
If tokens expire, open the Web UI and click **"Clear All Credentials"**, then re-authenticate.

### Check Logs
View sync history in the Web UI or in the addon **Log** tab.

## Data Storage

Credentials stored in `/config/.withings_sync_data/`:
- `.withings_user.json` - Withings OAuth tokens
- `.garmin_session/` - Garmin session cache
