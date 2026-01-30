#!/usr/bin/env python3
"""Withings Sync Addon Web Server."""

import json
import os
import subprocess
import threading
from pathlib import Path
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='/templates')

# Use /data/ for persistent storage (add-on private directory)
DATA_DIR = Path("/data")
WITHINGS_USER_FILE = DATA_DIR / ".withings_user.json"
GARMIN_CREDS_FILE = DATA_DIR / ".garmin_creds.json"
GARMIN_SESSION_DIR = DATA_DIR / ".garmin_session"


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


def get_garmin_creds():
    """Read Garmin credentials from data file."""
    if GARMIN_CREDS_FILE.exists():
        try:
            with open(GARMIN_CREDS_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_garmin_creds(email, password):
    """Save Garmin credentials to data file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(GARMIN_CREDS_FILE, "w") as f:
        json.dump({"email": email, "password": password}, f)
    # Set restrictive permissions
    GARMIN_CREDS_FILE.chmod(0o600)


def is_withings_authenticated():
    """Check if Withings tokens exist."""
    if not WITHINGS_USER_FILE.exists():
        return False
    try:
        with open(WITHINGS_USER_FILE) as f:
            data = json.load(f)
            return "access_token" in data and "refresh_token" in data
    except Exception:
        return False


def is_garmin_authenticated():
    """Check if Garmin credentials exist or session is cached."""
    has_creds = GARMIN_CREDS_FILE.exists()
    has_session = GARMIN_SESSION_DIR.exists() and any(GARMIN_SESSION_DIR.iterdir())
    return has_creds or has_session


def save_withings_auth_code(code):
    """Save Withings auth code to config file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data = {"authentification_code": code}
    with open(WITHINGS_USER_FILE, "w") as f:
        json.dump(data, f, indent=2)


def run_sync(wait=False):
    """Run withings-sync. If wait=True, block until complete and return result."""
    global sync_running, sync_log
    
    if sync_running:
        return False, "Sync already running", None
    
    sync_running = True
    sync_log = []
    result = {"success": False, "output": []}
    
    def _sync():
        global sync_running, sync_log
        try:
            garmin_creds = get_garmin_creds()
            garmin_user = garmin_creds.get("email", "")
            garmin_pass = garmin_creds.get("password", "")
            
            env = os.environ.copy()
            env["HOME"] = str(DATA_DIR)
            env["WITHINGS_USER"] = str(WITHINGS_USER_FILE)
            env["GARMIN_SESSION"] = str(GARMIN_SESSION_DIR)
            
            cmd = ["withings-sync"]
            if garmin_user:
                cmd.extend(["--garmin-username", garmin_user])
            if garmin_pass:
                cmd.extend(["--garmin-password", garmin_pass])
            
            sync_log.append("Running: withings-sync")
            
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
                result["success"] = True
            else:
                sync_log.append(f"✗ Sync failed with code {process.returncode}")
                result["success"] = False
            
            result["output"] = sync_log.copy()
                
        except Exception as e:
            sync_log.append(f"✗ Error: {str(e)}")
            result["success"] = False
            result["output"] = sync_log.copy()
        finally:
            sync_running = False
    
    if wait:
        _sync()
        return result["success"], "Sync completed" if result["success"] else "Sync failed", result["output"]
    else:
        thread = threading.Thread(target=_sync)
        thread.start()
        return True, "Sync started", None


@app.route("/_status")
def health():
    """Health check for ingress."""
    return "", 200


@app.route("/")
def index():
    """Main page."""
    # Get ingress path from header for proper URL resolution
    ingress_path = request.headers.get("X-Ingress-Path", "")
    return render_template(
        "index.html",
        ingress_path=ingress_path,
        withings_auth_url=WITHINGS_AUTH_URL,
        withings_authenticated=is_withings_authenticated(),
        garmin_authenticated=is_garmin_authenticated(),
    )


@app.route("/garmin", methods=["POST"])
def save_garmin():
    """Save Garmin credentials."""
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    
    if not email or not password:
        return jsonify({"success": False, "error": "Email and password required"})
    
    try:
        save_garmin_creds(email, password)
        return jsonify({"success": True, "message": "Garmin credentials saved"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


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
    """Trigger sync. Add ?async=1 to return immediately (for web UI)."""
    is_async = request.args.get("async") == "1"
    success, message, output = run_sync(wait=not is_async)
    
    response = {"success": success, "message": message}
    if output:
        response["output"] = output
    return jsonify(response)


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
        if GARMIN_CREDS_FILE.exists():
            GARMIN_CREDS_FILE.unlink()
        if GARMIN_SESSION_DIR.exists():
            import shutil
            shutil.rmtree(GARMIN_SESSION_DIR)
        return jsonify({"success": True, "message": "Credentials cleared"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    app.run(host="0.0.0.0", port=8099)
