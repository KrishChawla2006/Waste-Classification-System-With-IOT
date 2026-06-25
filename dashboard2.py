from flask import Flask, render_template, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# =============================
# CONFIG
# =============================
ESP_IP = "http://10.176.6.34"  # <-- Replace with your ESP8266 IP address
bin_counts = {"wet": 0, "dry": 0, "hazardous": 0}
last_level = 0

# =============================
# ROUTES
# =============================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_level")
def get_level():
    """Fetch latest dry bin level percentage from ESP8266"""
    global last_level
    try:
        r = requests.get(f"{ESP_IP}/level", timeout=3)
        if r.status_code == 200:
            val = r.text.strip()
            if val.isdigit():
                last_level = int(val)
    except Exception as e:
        print(f"[ERROR] Unable to get level: {e}")
    return jsonify({"level": last_level})

@app.route("/update_bin/<bin_type>")
def update_bin(bin_type):
    """Update count from classifier instantly"""
    if bin_type in bin_counts:
        bin_counts[bin_type] += 1
        print(f"[INFO] {bin_type.upper()} count updated → {bin_counts[bin_type]}")
    # Immediately return new data so the dashboard updates right away
    return jsonify(bin_counts)

@app.route("/get_bin_counts")
def get_bin_counts():
    """Return current bin counts for dashboard"""
    return jsonify(bin_counts)

@app.route("/admin/open/<bin_type>")
def admin_open(bin_type):
    """Send open command to ESP8266"""
    try:
        requests.get(f"{ESP_IP}/admin/open?bin={bin_type}", timeout=3)
        print(f"[ADMIN] Open {bin_type.upper()} bin")
        return jsonify({"status": "opened", "bin": bin_type})
    except Exception as e:
        print(f"[ERROR] Open failed: {e}")
        return jsonify({"status": "error", "bin": bin_type})

@app.route("/admin/close/<bin_type>")
def admin_close(bin_type):
    """Send close command to ESP8266"""
    try:
        requests.get(f"{ESP_IP}/admin/close?bin={bin_type}", timeout=3)
        print(f"[ADMIN] Close {bin_type.upper()} bin")
        return jsonify({"status": "closed", "bin": bin_type})
    except Exception as e:
        print(f"[ERROR] Close failed: {e}")
        return jsonify({"status": "error", "bin": bin_type})

# =============================
# MAIN
# =============================
if __name__ == "__main__":
    # Accessible from other devices in your Wi-Fi network
    app.run(host="0.0.0.0", port=5000, debug=True)
