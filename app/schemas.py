from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ChatRequest(BaseModel):
    """User chat message request for commuting queries."""
    message: str = Field(..., description="User's natural language query about commuting")
    sessionId: str = Field(..., description="Unique session identifier for conversation tracking")

class RouteOption(BaseModel):
    mode: str
    label: str
    distance_miles: float
    duration_min: int

class EmissionsEstimate(BaseModel):
    mode: str
    co2e_kg_per_trip: float
    method: str
    assumptions: List[str]

class AnnualizedEmissions(BaseModel):
    co2e_kg_per_year: float
    co2e_tons_per_year: float

class Scenario(BaseModel):
    """A single commuting scenario with emissions data."""
    name: str = Field(..., description="Human-readable scenario name (e.g., 'Driving daily')")
    mode: str = Field(..., description="Travel mode: driving, transit, or bike_transit")
    co2e_kg_per_trip: float = Field(..., description="CO2e emissions in kg per single trip")
    co2e_tons_per_year: float = Field(..., description="Annualized CO2e emissions in metric tons")
    estimated_duration_min: int = Field(..., description="Estimated commute duration in minutes")
    assumptions: List[str] = Field(..., description="List of assumptions used in calculation")

class BestOption(BaseModel):
    """Recommended commuting option with emissions savings."""
    mode: str = Field(..., description="Recommended travel mode")
    annual_savings_vs_driving_tons: float = Field(..., description="CO2e savings per year vs driving")
    annual_reduction_percent: int = Field(..., description="Percentage reduction in emissions")

class Assumptions(BaseModel):
    commute_days_per_year: int
    car_type: str
    estimate_quality: str

class ChatData(BaseModel):
    """Structured data payload for rendering in frontend."""
    intent: str = Field(..., description="Intent classification: commute_comparison or unsupported")
    origin: Optional[str] = Field(None, description="Extracted origin location")
    destination: Optional[str] = Field(None, description="Extracted destination location")
    scenarios: List[Scenario] = Field(..., description="Array of commuting scenarios compared")
    best_option: BestOption = Field(..., description="Recommended option with savings")
    improvement_plan: List[str] = Field(..., description="Actionable tips to reduce emissions")
    assumptions: Assumptions = Field(..., description="Metadata about calculation assumptions")

class ChatResponse(BaseModel):
    """Complete chat response with reply and structured data."""
    reply: str = Field(..., description="Human-readable chat response for display")
    data: ChatData = Field(..., description="Structured data for rendering cards and charts")

class HealthResponse(BaseModel):
    """Simple health check response."""
    ok: bool = Field(..., description="Service health status")