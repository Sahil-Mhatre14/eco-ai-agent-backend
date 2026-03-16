import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime

from tools.routing import get_distance
from tools.carbon_api import car_emissions, estimate_cost, estimate_time
from tools.flight_search import search_flights

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "nvidia/nemotron-3-nano-30b-a3b"


airport_map = {
    "Las Vegas": "LAS",
    "San Jose": "SJC",
    "San Francisco": "SFO",
    "Los Angeles": "LAX"
}


def call_llm(messages):

    response = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 300,
        },
    )

    result = response.json()

    if "choices" not in result:
        raise Exception(f"NVIDIA API error: {result}")

    message = result["choices"][0]["message"]

    content = message.get("content")

    if content is None:
        return ""

    if isinstance(content, list):
        text = ""
        for part in content:
            text += part.get("text", "")
        return text

    return content


def extract_cities(user_query):

    prompt = f"""
Extract the origin, destination locations, and any constraints from this query.

Return JSON only.

Example:
{{"origin": "Las Vegas", "destination": "San Jose", "constraints": {{"budget": 200, "max_time": "4 hours"}}}}

Constraints can include: budget (in dollars), max_time (travel time), preferred_mode, etc.

Query:
{user_query}
"""

    response = call_llm([
        {"role": "system", "content": "Extract travel locations and constraints."},
        {"role": "user", "content": prompt}
    ])

    if not response:
        raise Exception("Model returned empty response")

    try:
        start = response.find("{")
        end = response.rfind("}") + 1

        data = json.loads(response[start:end])

        origin = data.get("origin")
        destination = data.get("destination")
        constraints = data.get("constraints", {})

        return origin, destination, constraints

    except Exception:
        print("Model response:", response)
        raise Exception("Could not parse extraction")


def run_agent(user_query):

    today = datetime.now().strftime("%Y-%m-%d")

    # Extract cities and constraints
    origin, destination, constraints = extract_cities(user_query)

    if origin is None:
        origin = input("Where are you starting from? ")

    if destination is None:
        destination = input("Where are you traveling to? ")

    # Airport codes
    origin_airport = airport_map.get(origin)
    destination_airport = airport_map.get(destination)

    flights = []

    if origin_airport and destination_airport:
        flights = search_flights(origin_airport, destination_airport)

    # Distance calculation
    distance = get_distance(origin, destination)

    # Carbon emissions
    car = car_emissions(distance, "car")
    bus = car_emissions(distance, "bus")
    train = car_emissions(distance, "train")
    flight = car_emissions(distance, "flight")

    # Cost estimates
    car_cost = estimate_cost(distance, "car")
    bus_cost = estimate_cost(distance, "bus")
    train_cost = estimate_cost(distance, "train")
    flight_cost = estimate_cost(distance, "flight")

    # Time estimates
    car_time = estimate_time(distance, "car")
    bus_time = estimate_time(distance, "bus")
    train_time = estimate_time(distance, "train")
    flight_time = estimate_time(distance, "flight")

    carbon_saved = car - train
    percent_saved = round((carbon_saved / car) * 100)

    comparison = f"""
Travel distance: {round(distance,2)} miles

Estimated carbon emissions, cost, and time:

Car: {car} kg CO2, ${car_cost}, {car_time} hours
Flight: {flight} kg CO2, ${flight_cost}, {flight_time} hours
Bus: {bus} kg CO2, ${bus_cost}, {bus_time} hours
Train: {train} kg CO2, ${train_cost}, {train_time} hours

Train reduces emissions by {percent_saved}% compared to driving.
"""

    flight_summary = ""

    if flights:

        for f in flights:

            flight_summary += f"""
Airline: {f['airline']}
Flight: {f['flight_number']}
Departure: {f['departure']}
Arrival: {f['arrival']}
"""

    else:

        flight_summary = "No flight data found."

    comparison += "\nFlights Found:\n" + flight_summary

    # Format constraints for prompt
    constraints_text = ""
    if constraints:
        constraints_text = "User constraints: " + ", ".join([f"{k}: {v}" for k, v in constraints.items()]) + "\n\n"

    final_prompt = f"""
A user wants to travel from {origin} to {destination}.

Travel distance: {distance} miles.

Transport options (emissions, cost, time):

Car: {car} kg CO2, ${car_cost}, {car_time} hours
Bus: {bus} kg CO2, ${bus_cost}, {bus_time} hours
Train: {train} kg CO2, ${train_cost}, {train_time} hours
Flight: {flight} kg CO2, ${flight_cost}, {flight_time} hours

Flights available:

{flight_summary}

{constraints_text}Choose the best option that minimizes carbon emissions
while considering travel time, cost, and user constraints.

Explain your reasoning clearly.
"""

    answer = call_llm([
        {
            "role": "system",
            "content": "You are a sustainability AI agent helping reduce carbon footprint."
        },
        {"role": "user", "content": final_prompt}
    ])

    if not answer:
        answer = "The train is the lowest carbon option. Flights are faster but produce significantly higher emissions."

    return f"""
Route: {origin} → {destination}

{comparison}

AI Sustainability Plan:

{answer}
"""