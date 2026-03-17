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

    try:
        response = call_llm([
            {"role": "system", "content": "Extract travel locations and constraints."},
            {"role": "user", "content": prompt}
        ])

        if not response:
            raise Exception("Empty response")

        start = response.find("{")
        end = response.rfind("}") + 1

        data = json.loads(response[start:end])

        origin = data.get("origin")
        destination = data.get("destination")
        constraints = data.get("constraints", {})

        return origin, destination, constraints

    except Exception as e:
        print(f"LLM extraction failed: {e}")
        # Fallback: simple parsing
        query_lower = user_query.lower()

        # Simple city extraction (very basic)
        cities = []
        for city in ["las vegas", "san jose", "san francisco", "los angeles", "new york", "chicago"]:
            if city in query_lower:
                cities.append(city.title())

        origin = cities[0] if len(cities) > 0 else None
        destination = cities[1] if len(cities) > 1 else None

        # Extract constraints
        constraints = {}
        if "budget of $" in query_lower or "budget $" in query_lower:
            # Extract number after budget
            import re
            budget_match = re.search(r'budget(?: of)? \$?(\d+)', query_lower)
            if budget_match:
                constraints['budget'] = budget_match.group(1)

        if "within" in query_lower and "hour" in query_lower:
            # Extract number before hours
            hour_match = re.search(r'within (\d+) hours?', query_lower)
            if hour_match:
                constraints['max_time'] = f"{hour_match.group(1)} hours"

        return origin, destination, constraints


def evaluate_options_with_constraints(distance, constraints, flights=None):
    """
    Evaluate travel options considering emissions, cost, time, and user constraints.
    Returns a detailed recommendation.
    """

    # Calculate all metrics
    modes = ['car', 'bus', 'train', 'flight']
    options = {}

    for mode in modes:
        emissions = car_emissions(distance, mode)
        cost = estimate_cost(distance, mode)
        time = estimate_time(distance, mode)
        options[mode] = {
            'emissions': emissions,
            'cost': cost,
            'time': time
        }

    # Sort by emissions (lowest first)
    sorted_by_emissions = sorted(options.items(), key=lambda x: x[1]['emissions'])

    # Check constraints
    valid_options = []
    reasoning = []

    for mode, data in options.items():
        valid = True
        reasons = []

        if 'budget' in constraints:
            budget = float(constraints['budget'])
            if data['cost'] > budget:
                valid = False
                reasons.append(f"exceeds budget (${data['cost']:.2f} > ${budget})")

        if 'max_time' in constraints:
            # Parse time constraint (e.g., "4 hours" -> 4)
            max_time_str = constraints['max_time'].lower()
            if 'hour' in max_time_str:
                max_hours = float(max_time_str.split()[0])
                if data['time'] > max_hours:
                    valid = False
                    reasons.append(f"exceeds time limit ({data['time']:.1f}h > {max_hours}h)")

        if valid:
            valid_options.append((mode, data))
            if reasons:
                reasoning.append(f"{mode.title()}: meets constraints")
            else:
                reasoning.append(f"{mode.title()}: meets all constraints")

    # Build detailed response
    response = f"Travel Analysis for {distance:.1f} miles:\n\n"

    response += "All Options:\n"
    for mode, data in options.items():
        response += f"• {mode.title()}: {data['emissions']:.1f} kg CO2, ${data['cost']:.2f}, {data['time']:.1f} hours\n"

    # Add flight details if available
    if flights and len(flights) > 0:
        response += f"\nAvailable Flights ({len(flights)} found):\n"
        for i, f in enumerate(flights[:3]):  # Show up to 3 flights
            response += f"• {f['airline']} {f['flight_number']}: {f['departure'][:10]} at {f['departure'][11:16]}\n"
        if len(flights) > 3:
            response += f"• ... and {len(flights)-3} more flights\n"

    response += "\n"

    if valid_options:
        # Find best option considering constraints
        if constraints:
            response += f"Considering your constraints ({', '.join([f'{k}: {v}' for k, v in constraints.items()])}):\n"
            response += "\n".join(reasoning) + "\n\n"

            # Prioritize by emissions among valid options
            best_option = min(valid_options, key=lambda x: x[1]['emissions'])
            mode, data = best_option

            response += f"🌱 Recommended: {mode.title()}\n"
            response += f"• Carbon emissions: {data['emissions']:.1f} kg CO2 ({data['emissions']/sorted_by_emissions[0][1]['emissions']:.1f}x the lowest)\n"
            response += f"• Estimated cost: ${data['cost']:.2f}\n"
            response += f"• Travel time: {data['time']:.1f} hours\n"

            # Add specific reasoning
            if mode == 'train':
                response += f"• Why train? It's the most sustainable option, producing {data['emissions']:.1f} kg CO2 - "
                car_emissions_val = options['car']['emissions']
                response += f"{car_emissions_val/data['emissions']:.0f}x less than driving alone.\n"
            elif mode == 'flight' and flights:
                response += f"• Why flight? It meets your time constraint and flights are available.\n"
            elif mode == 'bus':
                response += f"• Why bus? Good balance of emissions and cost for longer distances.\n"

            # Compare to alternatives
            alternatives = [opt for opt in valid_options if opt[0] != mode]
            if alternatives:
                response += f"\nAlternatives that also meet constraints:\n"
                for alt_mode, alt_data in sorted(alternatives, key=lambda x: x[1]['emissions']):
                    emissions_diff = alt_data['emissions'] - data['emissions']
                    response += f"• {alt_mode.title()}: {alt_data['emissions']:.1f} kg CO2 ({'+' if emissions_diff > 0 else ''}{emissions_diff:.1f} kg), ${alt_data['cost']:.2f}, {alt_data['time']:.1f}h\n"
        else:
            # No constraints, recommend lowest emissions
            best_option = sorted_by_emissions[0]
            mode, data = best_option
            response += f"🌱 Recommended (lowest emissions): {mode.title()}\n"
            response += f"• Carbon emissions: {data['emissions']:.1f} kg CO2\n"
            response += f"• Estimated cost: ${data['cost']:.2f}\n"
            response += f"• Travel time: {data['time']:.1f} hours\n"
    else:
        response += "⚠️ No options meet all your constraints. Consider:\n"
        response += "• Increasing your budget\n"
        response += "• Allowing more travel time\n"
        response += "• Choosing a different route\n\n"

        # Show closest options
        response += "Closest sustainable options:\n"
        for mode, data in sorted(options.items(), key=lambda x: x[1]['emissions'])[:2]:
            constraint_notes = []
            if 'budget' in constraints and data['cost'] > float(constraints['budget']):
                constraint_notes.append(f"over budget by ${data['cost'] - float(constraints['budget']):.2f}")
            if 'max_time' in constraints:
                max_time_str = constraints['max_time'].lower()
                if 'hour' in max_time_str:
                    max_hours = float(max_time_str.split()[0])
                    if data['time'] > max_hours:
                        constraint_notes.append(f"{data['time'] - max_hours:.1f}h too slow")
            notes = f" ({', '.join(constraint_notes)})" if constraint_notes else ""
            response += f"• {mode.title()}: {data['emissions']:.1f} kg CO2, ${data['cost']:.2f}, {data['time']:.1f}h{notes}\n"

    return response


def run_agent(user_query):

    today = datetime.now().strftime("%Y-%m-%d")

    # Extract cities and constraints
    origin, destination, constraints = extract_cities(user_query)

    if origin is None or destination is None:
        return "Sorry, I couldn't extract the origin and destination from your query. Please specify both locations clearly."

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

    # Try to get LLM enhancement, but use constraint-aware evaluation as primary
    try:
        answer = call_llm([
            {
                "role": "system",
                "content": "You are a sustainability AI agent helping reduce carbon footprint. Provide a brief, specific recommendation considering all factors."
            },
            {"role": "user", "content": final_prompt}
        ])
        if not answer or len(answer.strip()) < 20:
            raise Exception("LLM response too short")
    except Exception as e:
        print(f"LLM call failed: {e}")
        answer = None

    # Use constraint-aware evaluation as primary method
    detailed_analysis = evaluate_options_with_constraints(distance, constraints, flights)

    if answer and answer != "The train is the lowest carbon option. Flights are faster but produce significantly higher emissions.":
        # LLM provided a good response, append it
        detailed_analysis += f"\n\nAI Insights:\n{answer}"
    else:
        # Use the detailed analysis as is
        pass

    return f"""
Route: {origin} → {destination}

{detailed_analysis}
"""