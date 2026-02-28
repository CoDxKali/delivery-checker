from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import math

app = Flask(__name__)
CORS(app)

WAREHOUSE_LAT = 28.4429
WAREHOUSE_LON = 77.0525
RADIUS_KM = 50


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))


@app.route("/check-delivery", methods=["POST"])
def check_delivery():
    pincode = request.json.get("pincode")

    try:
        res = requests.get(f"https://api.postalpincode.in/pincode/{pincode}")
        data = res.json()
    except:
        return jsonify({"error": "Postal API failed"})

    if data[0]["Status"] != "Success":
        return jsonify({"error": "Invalid Pincode"})

    post = data[0]["PostOffice"][0]
    city = post["District"]
    state = post["State"]

    # OPTIONAL: Only calculate distance if needed
    # You can skip distance and use only city logic

    return jsonify({
        "available": city.lower() in ["gurugram", "gurgaon"],
        "city": city,
        "state": state
    })