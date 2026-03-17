from app.schemas import EmissionsEstimate

# ============================================================================
# EMISSION FACTORS - Prototype hackathon approximations
# ============================================================================
# 
# These are simplified factors for fast estimation. Real emissions depend on:
# - Vehicle fuel efficiency (varies by model, year, condition)
# - Load factor / occupancy rate (more passengers = lower per-person emissions)
# - Grid electricity mix (for electric vehicles and transit)
# - Infrastructure embodied carbon (roads, stations, etc.)
# - Driving conditions (city vs highway, traffic patterns)
#
# SOURCES:
# - EPA vehicle emissions: https://www.epa.gov/
# - American Public Transportation Association (APTA) data
# - Blended bike + transit: estimated from component modes
#
# For production, consider integrating:
# - CarbonInterfaceAPI: https://www.carboninterfaceapi.com/
# - Climatiq: https://climatiq.io/
# - ElectricityMaps: https://app.electricitymaps.com/
#

EMISSIONS_FACTORS = {
    "driving": 0.404,      # kg CO2e per mile (average US gasoline vehicle)
    "transit": 0.15,       # kg CO2e per mile (public transit average)
    "bike_transit": 0.106  # kg CO2e per mile (blended: cycling + transit)
}

def estimate_travel_emissions(mode: str, distance_miles: float) -> EmissionsEstimate:
    """
    Estimate CO2e emissions for a travel mode and distance.
    
    Uses simple factor-based estimation (hackathon prototype).
    Multiplies distance by emissions factor for the mode.
    
    Args:
        mode: Travel mode key ('driving', 'transit', 'bike_transit')
        distance_miles: One-way trip distance in miles
    
    Returns:
        EmissionsEstimate with CO2e per trip and methodology notes
    """
    if mode not in EMISSIONS_FACTORS:
        raise ValueError(f"Unsupported mode: {mode}")
    
    factor = EMISSIONS_FACTORS[mode]
    co2e_kg_per_trip = factor * distance_miles
    
    assumptions = [
        f"Emissions factor: {factor} kg CO2e per passenger-mile (US average)",
        "Based on EPA and APTA transportation data",
        "Hackathon prototype approximations - not for regulatory use",
        "Assumes realistic load factors for transit modes"
    ]
    
    return EmissionsEstimate(
        mode=mode,
        co2e_kg_per_trip=round(co2e_kg_per_trip, 1),
        method="prototype_factor_estimate",
        assumptions=assumptions
    )