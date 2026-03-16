import requests
import math


def geocode(city):
    """
    Convert a city name into latitude and longitude
    using OpenStreetMap Nominatim API
    """

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": city,
        "format": "json",
        "limit": 1
    }

    response = requests.get(
        url,
        params=params,
        headers={
            "User-Agent": "Sustainability-AI-Agent"
        },
    )

    if response.status_code != 200:
        raise Exception(f"Geocoding request failed: {response.text}")

    try:
        data = response.json()
    except Exception:
        raise Exception(f"Invalid response from geocoding API: {response.text}")

    if not data:
        raise Exception(f"Location not found: {city}")

    lat = float(data[0]["lat"])
    lon = float(data[0]["lon"])

    return lat, lon


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate great-circle distance between two points
    using the Haversine formula
    """

    R = 6371  # Earth radius in km

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)

    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance_km = R * c

    distance_miles = distance_km * 0.621371

    return distance_miles


def get_distance(origin_city, destination_city):
    """
    Get distance in miles between two cities
    """

    # Clean city names if LLM returns "City, State"
    origin_city = origin_city.split(",")[0]
    destination_city = destination_city.split(",")[0]

    lat1, lon1 = geocode(origin_city)
    lat2, lon2 = geocode(destination_city)

    distance = haversine(lat1, lon1, lat2, lon2)

    return round(distance, 2)