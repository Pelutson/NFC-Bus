# === app.py ===
from flask import Flask, jsonify, request
import requests
from datetime import datetime

app = Flask(__name__)

API_KEY = "e30c7cba-c625-4e75-81f7-01c3ce985691"
BASE_URL = "https://www.rmv.de/hapi"
ORIGIN_ID = "3016016"  # Darmstadt Schloss
DEST_ID = "3000009"     # Darmstadt Berliner Allee (bitte ggf. anpassen)

@app.route("/trips")
def get_trips():
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    params = {
        "accessId": API_KEY,
        "originId": ORIGIN_ID,
        "destId": DEST_ID,
        "date": date_str,
        "time": time_str,
        "format": "json",
        "numF": 5
    }

    response = requests.get(f"{BASE_URL}/trip", params=params)
    data = response.json()

    trips = []
    for trip in data.get("Trip", []):
        leg = trip["Leg"]
        trips.append({
            "line": leg.get("name"),
            "departure": leg["Origin"].get("time"),
            "arrival": leg["Destination"].get("time"),
            "from": leg["Origin"].get("name"),
            "to": leg["Destination"].get("name")
        })

    return jsonify(trips)

if __name__ == "__main__":
    app.run(debug=True)