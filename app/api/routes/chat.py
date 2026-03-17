from fastapi import APIRouter, HTTPException
from app.schemas import ChatRequest, ChatResponse, HealthResponse
from app.agent.orchestrator import Orchestrator

router = APIRouter()
orchestrator = Orchestrator()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a user chat message and return structured commuting analysis.
    
    Supports natural language queries like:
    - "I commute from San Jose to Mountain View"
    - "Compare driving vs transit from X to Y"
    - "How much carbon would I save commuting from X to Y?"
    
    Returns both a human-readable reply and structured data for rendering.
    """
    try:
        result = orchestrator.process_message(request.message, request.sessionId)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/demo/commute", response_model=ChatResponse)
async def demo_commute():
    """
    Demo endpoint returning a fixed sample commute comparison payload.
    
    Useful for:
    - Testing frontend integration without hitting the AI agent
    - Validating response structure and data types
    - Working offline (no API keys or network required)
    
    Shows comparison for San Jose to Mountain View commute with three scenarios:
    driving, public transit, and bike + transit.
    """
    return ChatResponse(
        reply="Comparing commuting options from San Jose to Mountain View. The most sustainable option is Bike + transit, saving 3.7 tons of CO2e annually compared to driving.",
        data={
            "intent": "commute_comparison",
            "origin": "San Jose, CA",
            "destination": "Mountain View, CA",
            "scenarios": [
                {
                    "name": "Driving daily",
                    "mode": "driving",
                    "co2e_kg_per_trip": 10.2,
                    "co2e_tons_per_year": 4.5,
                    "estimated_duration_min": 27,
                    "assumptions": ["gasoline car", "220 commute days/year"]
                },
                {
                    "name": "Public transit",
                    "mode": "transit",
                    "co2e_kg_per_trip": 2.7,
                    "co2e_tons_per_year": 1.2,
                    "estimated_duration_min": 48,
                    "assumptions": ["single rider", "220 commute days/year"]
                },
                {
                    "name": "Bike + transit",
                    "mode": "bike_transit",
                    "co2e_kg_per_trip": 1.9,
                    "co2e_tons_per_year": 0.8,
                    "estimated_duration_min": 44,
                    "assumptions": ["first/last mile by bike", "220 commute days/year"]
                }
            ],
            "best_option": {
                "mode": "bike_transit",
                "annual_savings_vs_driving_tons": 3.7,
                "annual_reduction_percent": 82
            },
            "improvement_plan": [
                "Use Caltrain or VTA for 3 commute days each week",
                "Bike to and from the station for first/last mile",
                "Batch errands on one driving day to reduce extra trips"
            ],
            "assumptions": {
                "commute_days_per_year": 220,
                "car_type": "average gasoline passenger vehicle",
                "estimate_quality": "prototype"
            }
        }
    )

@router.get("/health", response_model=HealthResponse)
async def health():
    """Check if the backend service is running."""
    return HealthResponse(ok=True)