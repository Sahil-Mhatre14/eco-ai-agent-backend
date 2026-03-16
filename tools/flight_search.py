import requests
import os
from dotenv import load_dotenv

load_dotenv()

AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")


def search_flights(origin_airport, destination_airport):

    url = "http://api.aviationstack.com/v1/flights"

    params = {
        "access_key": AVIATIONSTACK_API_KEY,
        "dep_iata": origin_airport,
        "arr_iata": destination_airport
    }

    response = requests.get(url, params=params)

    data = response.json()

    flights = []

    for f in data.get("data", [])[:5]:

        airline = f.get("airline", {}).get("name")
        flight_number = f.get("flight", {}).get("iata")
        departure = f.get("departure", {}).get("scheduled")
        arrival = f.get("arrival", {}).get("scheduled")

        flights.append({
            "airline": airline,
            "flight_number": flight_number,
            "departure": departure,
            "arrival": arrival
        })

    return flights