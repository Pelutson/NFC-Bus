from flask import Flask, render_template
import requests
from datetime import datetime
import xml.etree.ElementTree as ET

app = Flask(__name__)

ACCESS_ID = 'APIKEY'
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
        'numF': 6,  # bis zu 6 Verbindungen
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

            # LegList kann entweder ein einzelnes Leg sein oder eine Liste
            legs = leg_list.findall('hafas:Leg', ns)
            if not legs:
                leg = leg_list.find('hafas:Leg', ns)
                if leg is not None:
                    legs = [leg]

            for leg in legs:
                origin = leg.find('hafas:Origin', ns)
                destination = leg.find('hafas:Destination', ns)
                line = leg.find('hafas:Product', ns)

                if origin is not None and destination is not None and line is not None:
                    # Formatierte Abfahrtszeit (HH:MM)
                    departure_iso = origin.attrib.get('dateTime')
                    try:
                        departure_time = datetime.fromisoformat(departure_iso).strftime('%H:%M')
                    except:
                        departure_time = origin.attrib.get('time', '')[:5]  # Fallback

                    connections.append({
                        'line': line.attrib.get('line', 'Unbekannt'),
                        'departure': departure_time,
                        'destination': destination.attrib.get('name', ''),
                    })
                break  # Nur die erste Fahrt betrachten

        return connections
    except Exception as e:
        print("Fehler beim Parsen:", e)
        return []

@app.route('/')
def index():
    connections = fetch_connections()
    return render_template('index.html', connections=connections)

if __name__ == '__main__':
    app.run(debug=True)
