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

Open the Web UI and click **"Sync Now"** to sync your latest Withings data to Garmin Connect.

## Troubleshooting

### Re-authenticate
If tokens expire, open the Web UI and click **"Clear All Credentials"**, then set up both services again.

### Check Logs
View sync history in the Web UI or in the addon **Log** tab.

## Data Storage

Credentials are stored securely in the addon's private data directory:
- `.withings_user.json` - Withings OAuth tokens
- `.garmin_creds.json` - Garmin credentials (permissions: 600)
- `.garmin_session/` - Garmin session cache

## Notes

- This addon uses the [withings-sync](https://github.com/jaroslawhartman/withings-sync) project
- Withings OAuth callback is handled via the withings-sync project's GitHub Pages
