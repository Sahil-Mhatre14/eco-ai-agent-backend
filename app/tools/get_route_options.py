from typing import List
from app.schemas import RouteOption
from app.config import Config

# ============================================================================
# MOCK MODE - Returns hardcoded data for prototyping and demos
# Default for hackathon (fast, no external dependencies, works offline)
# ============================================================================

def _get_mock_routes(origin: str, destination: str) -> List[RouteOption]:
    """
    Mock implementation returning hardcoded commute routes.
    
    Useful for:
    - Local development without APIs
    - Frontend testing without backend latency
    - Hackathon demos with fixed data
    """
    # Specific hardcoded data for common route
    if "san jose" in origin.lower() and "mountain view" in destination.lower():
        return [
            RouteOption(
                mode="driving",
                label="Driving daily",
                distance_miles=18.0,
                duration_min=27
            ),
            RouteOption(
                mode="transit",
                label="Public transit",
                distance_miles=18.0,
                duration_min=48
            ),
            RouteOption(
                mode="bike_transit",
                label="Bike + transit",
                distance_miles=18.0,
                duration_min=44
            )
        ]
    else:
        # Generic fallback for any route
        return [
            RouteOption(
                mode="driving",
                label="Driving daily",
                distance_miles=10.0,
                duration_min=20
            ),
            RouteOption(
                mode="transit",
                label="Public transit",
                distance_miles=10.0,
                duration_min=35
            ),
            RouteOption(
                mode="bike_transit",
                label="Bike + transit",
                distance_miles=10.0,
                duration_min=30
            )
        ]

# ============================================================================
# REAL API MODE - Future: integrate with routing services
# ============================================================================

def _get_real_routes(origin: str, destination: str) -> List[RouteOption]:
    """
    Real implementation: fetch routes from external API.
    
    To implement, choose one:
    
    1. Google Maps Directions API
       - https://developers.google.com/maps/documentation/directions
       - Requires: GOOGLE_MAPS_API_KEY env var
       - Returns: distance, duration, route details for multiple modes
    
    2. OpenStreetMap (free alternative)
       - https://github.com/Project-OSRM/osrm-backend
       - Self-hosted or public instance
       - Good for cycling and transit
    
    3. HERE Maps API
       - https://developer.here.com/
       - Commercial, enterprise support
    
    Steps to implement:
    1. Add API key to .env file
    2. Update config.py to read it
    3. Implement geocoding (address → lat/lon)
    4. Call routing API for each mode
    5. Parse response and return RouteOption objects
    """
    raise NotImplementedError(
        "Real routing API not yet implemented. "
        f"See app/tools/get_route_options.py docstring for integration options. "
        f"Currently in MOCK_MODE={Config.MOCK_MODE}. "
        f"To switch to real mode, set MOCK_MODE=false in .env"
    )

# ============================================================================
# PUBLIC API
# ============================================================================

def get_route_options(origin: str, destination: str) -> List[RouteOption]:
    """
    Get commute route options between two locations.
    
    Behavior controlled by MOCK_MODE config setting:
    
    - MOCK_MODE=true (default)
      Fast hardcoded data. Perfect for hackathon, offline development, demos.
      No external API calls, no network latency, instant response.
      
    - MOCK_MODE=false
      Fetches real-time data from routing API.
      Requires API key and network connection.
      Provide accurate distance and duration.
    
    Args:
        origin: Starting location (city, address, or landmark)
        destination: Ending location
    
    Returns:
        List of RouteOption objects with mode, distance, duration
    """
    if Config.MOCK_MODE:
        return _get_mock_routes(origin, destination)
    else:
        return _get_real_routes(origin, destination)