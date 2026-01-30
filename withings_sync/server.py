#!/usr/bin/env python3
"""Withings Sync Addon Web Server."""

import json
import os
import subprocess
import threading
from pathlib import Path
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='/templates')

CONFIG_DIR = Path("/config/.withings_sync_data")
OPTIONS_FILE = Path("/data/options.json")
WITHINGS_USER_FILE = CONFIG_DIR / ".withings_user.json"
GARMIN_SESSION_DIR = CONFIG_DIR / ".garmin_session"

# Withings OAuth settings (from withings-sync project)
WITHINGS_CLIENT_ID = "183e03e1f363110b3551f96765c98c10e8f1aa647a37067a1cb64bbbaf491626"
WITHINGS_CALLBACK_URL = "https://jaroslawhartman.github.io/withings-sync/contrib/withings.html"
WITHINGS_AUTH_URL = (
    f"https://account.withings.com/oauth2_user/authorize2"
    f"?response_type=code"
    f"&client_id={WITHINGS_CLIENT_ID}"
    f"&state=OK"
    f"&scope=user.metrics"
    f"&redirect_uri={WITHINGS_CALLBACK_URL}"
)

# Sync state
sync_log = []
sync_running = False


def get_options():
    """Read addon options."""
    if OPTIONS_FILE.exists():
        with open(OPTIONS_FILE) as f:
            return json.load(f)
    return {}


def is_withings_authenticated():
    """Check if Withings tokens exist."""
    if not WITHINGS_USER_FILE.exists():
        return False
    try:
        with open(WITHINGS_USER_FILE) as f:
            data = json.load(f)
            return "access_token" in data and "refresh_token" in data
    except:
        return False


def is_garmin_authenticated():
    """Check if Garmin session exists."""
    return GARMIN_SESSION_DIR.exists() and any(GARMIN_SESSION_DIR.iterdir())


def save_withings_auth_code(code):
    """Save Withings auth code to config file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data = {"authentification_code": code}
    with open(WITHINGS_USER_FILE, "w") as f:
        json.dump(data, f, indent=2)


def run_sync():
    """Run withings-sync in background."""
    global sync_running, sync_log
    
    if sync_running:
        return False, "Sync already running"
    
    sync_running = True
    sync_log = []
    
    def _sync():
        global sync_running, sync_log
        try:
            options = get_options()
            garmin_user = options.get("garmin_username", "")
            garmin_pass = options.get("garmin_password", "")
            
            env = os.environ.copy()
            env["HOME"] = str(CONFIG_DIR)
            env["WITHINGS_USER"] = str(WITHINGS_USER_FILE)
            env["GARMIN_SESSION"] = str(GARMIN_SESSION_DIR)
            
            cmd = ["withings-sync"]
            if garmin_user:
                cmd.extend(["--garmin-username", garmin_user])
            if garmin_pass:
                cmd.extend(["--garmin-password", garmin_pass])
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
                text=True
            )
            
            for line in process.stdout:
                sync_log.append(line.strip())
                print(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                sync_log.append("✓ Sync completed successfully!")
            else:
                sync_log.append(f"✗ Sync failed with code {process.returncode}")
                
        except Exception as e:
            sync_log.append(f"✗ Error: {str(e)}")
        finally:
            sync_running = False
    
    thread = threading.Thread(target=_sync)
    thread.start()
    return True, "Sync started"


@app.route("/_status")
def health():
    """Health check for ingress."""
    return "", 200


@app.route("/")
def index():
    """Main page."""
    return render_template(
        "index.html",
        withings_auth_url=WITHINGS_AUTH_URL,
        withings_authenticated=is_withings_authenticated(),
        garmin_authenticated=is_garmin_authenticated(),
        garmin_username=get_options().get("garmin_username", ""),
    )


@app.route("/authorize", methods=["POST"])
def authorize():
    """Save Withings auth code."""
    code = request.form.get("code", "").strip()
    if not code:
        return jsonify({"success": False, "error": "No code provided"})
    
    save_withings_auth_code(code)
    return jsonify({"success": True, "message": "Auth code saved. Click 'Sync Now' to complete authentication."})


@app.route("/sync", methods=["POST"])
def sync():
    """Trigger sync."""
    success, message = run_sync()
    return jsonify({"success": success, "message": message})


@app.route("/status")
def status():
    """Get current status."""
    return jsonify({
        "withings_authenticated": is_withings_authenticated(),
        "garmin_authenticated": is_garmin_authenticated(),
        "sync_running": sync_running,
        "sync_log": sync_log[-50:],  # Last 50 lines
    })


@app.route("/clear", methods=["POST"])
def clear():
    """Clear stored credentials."""
    try:
        if WITHINGS_USER_FILE.exists():
            WITHINGS_USER_FILE.unlink()
        if GARMIN_SESSION_DIR.exists():
            import shutil
            shutil.rmtree(GARMIN_SESSION_DIR)
        return jsonify({"success": True, "message": "Credentials cleared"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


if __name__ == "__main__":
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    app.run(host="0.0.0.0", port=8099)
