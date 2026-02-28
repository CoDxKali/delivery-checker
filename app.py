from flask import Flask, render_template, request, jsonify
from geopy.geocoders import Nominatim
import math

app = Flask(__name__)
geolocator = Nominatim(user_agent="delivery_checker")

WAREHOUSE_LAT = 28.4429
WAREHOUSE_LON = 77.0525
RADIUS_KM = 50

# ⭐ Pincode cache (memory)
pincode_cache = {}


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))


@app.route("/")
def home():
    return render_template("index.html",
                           warehouse_lat=WAREHOUSE_LAT,
                           warehouse_lon=WAREHOUSE_LON,
                           radius=RADIUS_KM)


# ⭐ AJAX API
@app.route("/check-delivery", methods=["POST"])
def check_delivery():
    pincode = request.json.get("pincode")

    if pincode in pincode_cache:
        lat, lon, city, state = pincode_cache[pincode]
    else:
        location = geolocator.geocode(f"{pincode}, India", addressdetails=True)

        if not location:
            return jsonify({"error": "Invalid Pincode"})

        lat, lon = location.latitude, location.longitude

        # ⭐ Extract city/state
        address = location.raw.get("address", {})
        city = address.get("city") or address.get("town") or address.get("village") or "Unknown"
        state = address.get("state", "Unknown")

        # cache
        pincode_cache[pincode] = (lat, lon, city, state)

    distance = haversine(WAREHOUSE_LAT, WAREHOUSE_LON, lat, lon)

    return jsonify({
        "distance": round(distance, 2),
        "available": distance <= RADIUS_KM,
        "city": city,
        "state": state
    })


if __name__ == "__main__":
    app.run(debug=True, port=8000)