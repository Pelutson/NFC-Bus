# 🚌 RMV Bus Connection Viewer – Darmstadt Live Departures

This web application displays real-time bus connections **from Darmstadt Schloss to Berliner Allee**.

It is built with [Flask](https://flask.palletsprojects.com/), uses the [RMV HAFAS API](https://www.rmv.de/), and can optionally be deployed on [Heroku](https://www.heroku.com/) with a custom domain and HTTPS support.

---

## 🚀 Features

- Live RMV bus departures with time, line, and destination
- One table:
  - From **Schloss → Berliner Allee**
- Responsive and modern design
- Optional custom domain (e.g., `bus.yourdomain.com`)
- HTTPS with automatic SSL certificate support via Heroku

---

## 🔐 API Key

To use the RMV HAFAS API, you need a free `ACCESS_ID` which can be obtained here:
👉 https://www.rmv.de/c/developer

Once you have the key, you can provide it via:

- A `.env` file (recommended locally):  
