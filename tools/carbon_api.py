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


def estimate_cost(distance, mode):
    """
    Estimate cost in USD for different travel modes.
    distance should be in miles.
    """

    cost_factors = {
        "car": 0.58,      # $ per mile (gas + maintenance)
        "bus": 0.15,      # $ per mile
        "train": 0.12,    # $ per mile
        "flight": 0.25    # $ per mile (rough estimate)
    }

    factor = cost_factors.get(mode)

    if factor is None:
        return None

    cost = distance * factor

    return round(cost, 2)


def estimate_time(distance, mode):
    """
    Estimate travel time in hours for different travel modes.
    distance should be in miles.
    """

    speed_factors = {
        "car": 60,        # mph
        "bus": 50,        # mph
        "train": 70,      # mph
        "flight": 500     # mph (cruising speed)
    }

    speed = speed_factors.get(mode)

    if speed is None:
        return None

    time_hours = distance / speed

    # Add buffer time for flights (takeoff/landing)
    if mode == "flight":
        time_hours += 1  # 1 hour for airport procedures

    return round(time_hours, 2)


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