import requests
import os

CARBON_API_KEY = os.getenv("CARBON_API_KEY")

def car_emissions(distance, mode):
    """
    Estimate carbon emissions (kg CO2) for different travel modes.
    distance should be in miles.
    """

    emission_factors = {
        "car": 0.404,     # kg CO2 per mile (average gasoline car)
        "bus": 0.089,     # kg CO2 per mile per passenger
        "train": 0.041,   # kg CO2 per mile per passenger
        "flight": 0.255   # kg CO2 per mile per passenger (short flight)
    }

    factor = emission_factors.get(mode)

    if factor is None:
        raise Exception(f"Unsupported travel mode: {mode}")

    emissions = distance * factor

    return round(emissions, 2)


def flight_emissions(origin, destination):

    url = "https://www.carboninterface.com/api/v1/estimates"

    headers = {
        "Authorization": f"Bearer {CARBON_API_KEY}"
    }

    body = {
        "type": "flight",
        "passengers": 1,
        "legs": [
            {
                "departure_airport": origin,
                "destination_airport": destination
            }
        ]
    }

    response = requests.post(url, json=body, headers=headers)

    return response.json()