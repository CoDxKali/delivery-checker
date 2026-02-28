from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from geopy.geocoders import Nominatim
import math

app = Flask(__name__)
CORS(app)   # 👈 THIS LINE IS REQUIRED

geolocator = Nominatim(user_agent="delivery_checker")
WAREHOUSE_LAT = 28.4429
WAREHOUSE_LON = 77.0525
RADIUS_KM = 50

pincode_cache = {}


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

    if pincode in pincode_cache:
        lat, lon, city, state = pincode_cache[pincode]
    else:
        location = geolocator.geocode(
            f"{pincode}, Gurgaon, Haryana, India",
            addressdetails=True,
            timeout=10
        )

        if not location:
            return jsonify({"error": "Invalid Pincode"})

        lat, lon = location.latitude, location.longitude

        address = location.raw.get("address", {})
        city = address.get("city") or address.get("town") or address.get("village") or "Unknown"
        state = address.get("state", "Unknown")

        pincode_cache[pincode] = (lat, lon, city, state)

    # ⭐ Distance calculation
    distance = haversine(WAREHOUSE_LAT, WAREHOUSE_LON, lat, lon)

    # ⭐ Gurgaon override
    is_available = distance <= RADIUS_KM 

    return jsonify({
        "distance": round(distance, 2),
        "available": is_available,
        "city": city,
        "state": state
    })

if __name__ == "__main__":
    app.run(debug=True, port=8000)