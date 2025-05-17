from flask import Flask, render_template, request
import requests
from datetime import datetime
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

ACCESS_ID = os.getenv('ACCESS_ID')
if not ACCESS_ID:
    ACCESS_ID = 'DEIN_ACCESS_ID_HIER'  # hier dein Key eintragen

# RMV Stop-IDs
STOPS = {
    "schloss": "3016016",
    "allee": "3004735",
    "hbf": "3000010",
    "luisenplatz": "3016001"
}

def fetch_connections(origin_id, dest_id):
    url = 'https://www.rmv.de/hapi/trip'
    params = {
        'accessId': ACCESS_ID,
        'originId': origin_id,
        'destId': dest_id,
        'format': 'xml',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'time': datetime.now().strftime('%H:%M'),
        'numF': 5,
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Fehler bei API-Abfrage ({origin_id} ➝ {dest_id}):", response.status_code)
        return []

    try:
        root = ET.fromstring(response.content)
        ns = {'hafas': 'http://hacon.de/hafas/proxy/hafas-proxy'}
        trips = root.findall('.//hafas:Trip', ns)
        connections = []

        for trip in trips:
            leg_list = trip.find('hafas:LegList', ns)
            if leg_list is None:
                continue

            leg = leg_list.find('hafas:Leg', ns)
            if leg is None:
                continue

            origin = leg.find('hafas:Origin', ns)
            destination = leg.find('hafas:Destination', ns)
            line = leg.find('hafas:Product', ns)

            if origin is not None and destination is not None and line is not None:
                time_str = origin.attrib.get('time', '')
                if 'T' in time_str:
                    departure = time_str.split('T')[1][:5]  # Uhrzeit HH:MM
                else:
                    departure = "Unbekannt"

                connections.append({
                    'line': line.attrib.get('line', 'Unbekannt'),
                    'departure': departure,
                    'destination': destination.attrib.get('name', 'Unbekannt'),
                })

        return connections
    except Exception as e:
        print("Fehler beim Parsen:", e)
        return []

@app.route('/')
def index():
    connections_to_allee = fetch_connections(STOPS['schloss'], STOPS['allee'])
    hbf_to_schloss = fetch_connections(STOPS['hbf'], STOPS['schloss'])
    hbf_to_luisenplatz = fetch_connections(STOPS['hbf'], STOPS['luisenplatz'])
    return render_template('index.html',
                           connections_to_allee=connections_to_allee,
                           hbf_to_schloss=hbf_to_schloss,
                           hbf_to_luisenplatz=hbf_to_luisenplatz)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
