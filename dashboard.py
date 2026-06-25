from flask import Flask, render_template, jsonify, Response
import requests
import time
import json

app = Flask(__name__)

ESP_IP = "http://10.87.46.34"  # your ESP8266 IP
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
    # send to all dashboards
    broadcast_update()
    return jsonify(bin_counts)

@app.route("/get_bin_counts")
def get_bin_counts():
    return jsonify(bin_counts)

@app.route("/admin/open/<bin_type>")
def admin_open(bin_type):
    try:
        requests.get(f"{ESP_IP}/admin/open?bin={bin_type}", timeout=3)
        return jsonify({"status": "opened", "bin": bin_type})
    except:
        return jsonify({"status": "error"})

@app.route("/admin/close/<bin_type>")
def admin_close(bin_type):
    try:
        requests.get(f"{ESP_IP}/admin/close?bin={bin_type}", timeout=3)
        return jsonify({"status": "closed", "bin": bin_type})
    except:
        return jsonify({"status": "error"})

# --- SSE Stream ---
clients = []

@app.route("/stream")
def stream():
    def event_stream():
        messages = []
        clients.append(messages)
        while True:
            if messages:
                data = messages.pop(0)
                yield f"data: {json.dumps(data)}\n\n"
            time.sleep(0.5)
    return Response(event_stream(), mimetype="text/event-stream")

def broadcast_update():
    for c in clients:
        c.append(bin_counts.copy())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
