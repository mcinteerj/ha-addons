# Withings Sync Addon

Syncs weight and body composition data from Withings scales to Garmin Connect.

## Setup

### 1. Start the Addon

Click **Start**. The addon will run continuously to serve the web UI.

### 2. Open the Web UI

Click **"OPEN WEB UI"** in the addon panel.

### 3. Configure Garmin

Enter your Garmin Connect email and password, then click **Save Garmin Credentials**.

### 4. Authenticate with Withings

1. Click **"Open Withings Login"** - opens Withings in a new tab
2. Log in and authorize the app
3. You'll be redirected to a page showing your authorization code
4. Copy the code and paste it into the addon web UI
5. Click **"Save Code"**
6. Click **"Sync Now"** to complete authentication and sync

## Usage

### Manual Sync
Open the Web UI and click **"Sync Now"**.

### Automated Sync

Once both services are connected, an **Automation** section appears in the Web UI with your API token.

**1. Copy your API token** from the Web UI.

**2. Add to `configuration.yaml`:**

```yaml
rest_command:
  withings_sync:
    url: "http://homeassistant.local:8099/sync"
    method: POST
    headers:
      Authorization: "Bearer YOUR_TOKEN_HERE"
```

**3. Create an automation:**

```yaml
automation:
  - alias: "Sync Withings to Garmin on Weight Update"
    trigger:
      - platform: state
        entity_id: sensor.withings_weight_kg
    action:
      - service: rest_command.withings_sync
```

Or on a schedule:

```yaml
automation:
  - alias: "Daily Withings Sync"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: rest_command.withings_sync
```

## Troubleshooting

### Re-authenticate
If tokens expire, open the Web UI and click **"Clear All Credentials"**, then set up both services again.

### Check Logs
View sync history in the Web UI or in the addon **Log** tab.

### API Returns 401
Ensure your `rest_command` has the correct `Authorization: Bearer <token>` header.

## Data Storage

Credentials are stored securely in the addon's private data directory:
- `.withings_user.json` - Withings OAuth tokens
- `.garmin_creds.json` - Garmin credentials (permissions: 600)
- `.garmin_session/` - Garmin session cache
- `.api_token` - API token for automations (permissions: 600)

## Notes

- This addon uses the [withings-sync](https://github.com/jaroslawhartman/withings-sync) project
- Withings OAuth callback is handled via the withings-sync project's GitHub Pages
