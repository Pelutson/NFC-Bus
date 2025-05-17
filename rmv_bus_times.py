from flask import Flask, render_template
import requests
from datetime import datetime
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv

# .env laden
load_dotenv()

app = Flask(__name__)

ACCESS_ID = os.getenv('ACCESS_ID')
ORIGIN_ID = '3016016'  # Darmstadt Schloss
DEST_ID = '3004735'    # Darmstadt Berliner Allee

def fetch_connections():
    url = 'https://www.rmv.de/hapi/trip'
    params = {
        'accessId': ACCESS_ID,
        'originId': ORIGIN_ID,
        'destId': DEST_ID,
        'format': 'xml',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'time': datetime.now().strftime('%H:%M'),
        'numF': 6,
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("Fehler bei API-Abfrage:", response.status_code)
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

            legs = leg_list.findall('hafas:Leg', ns)
            if not legs:
                leg = leg_list.find('hafas:Leg', ns)
                if leg is not None:
                    legs = [leg]

            for leg in legs:
                origin = leg.find('hafas:Origin', ns)
                destination = leg.find('hafas:Destination', ns)
                line = leg.find('hafas:Product', ns)

                departure_time = "Unbekannt"
                if origin is not None and 'time' in origin.attrib:
                    try:
                        dt = datetime.fromisoformat(origin.attrib['time'])
                        departure_time = dt.strftime('%H:%M')
                    except Exception as e:
                        print("Zeitformat-Fehler:", e)
                departure_time = origin.attrib.get('time', '')[:5] if origin is not None else "Unbekannt"


                if origin is not None and destination is not None and line is not None:
                    connections.append({
                        'line': line.attrib.get('line', 'Unbekannt'),
                        'departure': departure_time,
                        'destination': destination.attrib.get('name', 'Unbekannt'),
                    })
                break  # nur erste Fahrt

        return connections
    except Exception as e:
        print("Fehler beim Parsen:", e)
        return []

@app.route('/')
def index():
    connections = fetch_connections()
    return render_template('index.html', connections=connections)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)