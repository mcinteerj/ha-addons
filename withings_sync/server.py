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
API_TOKEN_FILE = DATA_DIR / ".api_token"


def get_or_create_token():
    """Get existing API token or create a new one."""
    if API_TOKEN_FILE.exists():
        return API_TOKEN_FILE.read_text().strip()
    import secrets
    token = secrets.token_urlsafe(32)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    API_TOKEN_FILE.write_text(token)
    API_TOKEN_FILE.chmod(0o600)
    print(f"[INFO] API token created: {token}")
    print("[INFO] Use this token in your rest_command Authorization header")
    return token


def is_authorized():
    """Check if request is from ingress, internal network, or has valid token."""
    # Ingress requests are pre-authenticated by HA
    if request.headers.get("X-Ingress-Path"):
        return True
    # Internal HA network (supervisor, core, other addons) - trusted
    remote_ip = request.remote_addr or ""
    if remote_ip.startswith("172.30."):
        return True
    # External requests need Bearer token
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:] == get_or_create_token()
    return False

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
            
            sync_log.append(f"Running: withings-sync")
            
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
    """Trigger sync (requires auth for external requests)."""
    if not is_authorized():
        return jsonify({"success": False, "error": "Unauthorized - Bearer token required"}), 401
    success, message = run_sync()
    return jsonify({"success": success, "message": message})


@app.route("/api-token")
def api_token():
    """Get API token for automations (ingress only)."""
    if not request.headers.get("X-Ingress-Path"):
        return jsonify({"error": "Only accessible via Web UI"}), 403
    return jsonify({"token": get_or_create_token()})


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
