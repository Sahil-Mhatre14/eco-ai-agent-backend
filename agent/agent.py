import requests
import json
import os
from dotenv import load_dotenv

from tools.routing import get_distance
from tools.carbon_api import car_emissions

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

MODEL = "nvidia/nemotron-3-nano-30b-a3b"


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

    return result["choices"][0]["message"]["content"]


def extract_cities(user_query):

    prompt = f"""
Extract the origin and destination locations from this query.

Locations may be:
- city
- street address
- landmark

Rules:
- Do NOT guess missing locations.
- If a location is missing, return null.
- Return JSON only.

Example:
{{"origin": "Las Vegas", "destination": "San Jose"}}

Query:
{user_query}
"""

    response = call_llm(
        [
            {"role": "system", "content": "You extract structured travel information."},
            {"role": "user", "content": prompt},
        ]
    )

    if not response:
        raise Exception("Model returned empty response")

    # Sometimes the model returns extra text. Extract JSON safely.
    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        json_text = response[start:end]

        cities = json.loads(json_text)

        origin = cities.get("origin")
        destination = cities.get("destination")

        return origin, destination

    except Exception:
        print("Model response was:", response)
        raise Exception("Could not parse cities from model response")


def run_agent(user_query):

    # Step 1: extract cities using AI
    origin, destination = extract_cities(user_query)

    if origin is None:
        origin = input("Where are you starting from? ")

    if destination is None:
        destination = input("Where are you traveling to? ")

    # Step 2: calculate distance
    distance = get_distance(origin, destination)

    # Step 3: estimate emissions
    car = car_emissions(distance, "car")
    bus = car_emissions(distance, "bus")
    train = car_emissions(distance, "train")
    flight = car_emissions(distance, "flight")

    comparison = f"""
Travel distance: {round(distance,2)} miles

Estimated carbon emissions:

Car: {car} kg CO2
Flight: {flight} kg CO2
Bus: {bus} kg CO2
Train: {train} kg CO2
"""

    # Step 4: ask AI to generate sustainability plan
    final_prompt = f"""
A user is travelling from {origin} to {destination}.

Here are estimated emissions for different travel modes:

{comparison}

Explain which option produces the lowest carbon footprint
and suggest the best sustainable travel plan.
"""

    answer = call_llm(
        [
            {
                "role": "system",
                "content": "You are a sustainability AI agent helping reduce carbon footprint.",
            },
            {"role": "user", "content": final_prompt},
        ]
    )

    return f"""
Route: {origin} → {destination}

{comparison}

AI Sustainability Plan:

{answer}
"""
