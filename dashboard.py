from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

ESP_IP = "http://10.176.6.34"  # <-- Replace with your ESP8266 IP
bin_counts = {"wet": 0, "dry": 0, "hazardous": 0}
last_level = 0

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_level")
def get_level():
    global last_level
    try:
        r = requests.get(f"{ESP_IP}/level", timeout=3)
        if r.status_code == 200:
            last_level = int(r.text.strip())
    except:
        pass
    return jsonify({"level": last_level})

@app.route("/update_bin/<bin_type>")
def update_bin(bin_type):
    if bin_type in bin_counts:
        bin_counts[bin_type] += 1
    return jsonify(bin_counts)

@app.route("/get_bin_counts")
def get_bin_counts():
    return jsonify(bin_counts)

@app.route("/admin/open/<bin_type>")
def admin_open(bin_type):
    try:
        r = requests.get(f"{ESP_IP}/admin/open?bin={bin_type}", timeout=3)
        return jsonify({"status": "opened", "bin": bin_type})
    except:
        return jsonify({"status": "error"})

@app.route("/admin/close/<bin_type>")
def admin_close(bin_type):
    try:
        r = requests.get(f"{ESP_IP}/admin/close?bin={bin_type}", timeout=3)
        return jsonify({"status": "closed", "bin": bin_type})
    except:
        return jsonify({"status": "error"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
