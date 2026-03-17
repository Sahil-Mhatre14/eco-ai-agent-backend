import json
from typing import Dict, Any, List
from app.model.nemotron import NemotronClient
from app.agent.system_prompt import SYSTEM_PROMPT
from app.tools.get_route_options import get_route_options
from app.tools.estimate_travel_emissions import estimate_travel_emissions
from app.tools.annualize_emissions import annualize_emissions
from app.schemas import ChatData, Scenario, BestOption, Assumptions
from app.config import Config

class Orchestrator:
    def __init__(self):
        self.client = NemotronClient()
        self.tools = {
            "get_route_options": get_route_options,
            "estimate_travel_emissions": estimate_travel_emissions,
            "annualize_emissions": annualize_emissions
        }
    
    def _get_tool_schemas(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_route_options",
                    "description": "Get available commuting route options between two locations",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "origin": {"type": "string", "description": "Origin location"},
                            "destination": {"type": "string", "description": "Destination location"}
                        },
                        "required": ["origin", "destination"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "estimate_travel_emissions",
                    "description": "Estimate CO2e emissions for a travel mode and distance",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "mode": {"type": "string", "description": "Travel mode (driving, transit, bike_transit)"},
                            "distance_miles": {"type": "number", "description": "Distance in miles"}
                        },
                        "required": ["mode", "distance_miles"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "annualize_emissions",
                    "description": "Convert per-trip emissions to annual emissions",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "co2e_kg_per_trip": {"type": "number", "description": "CO2e kg per trip"},
                            "commute_days_per_year": {"type": "integer", "description": "Number of commute days per year", "default": 220}
                        },
                        "required": ["co2e_kg_per_trip"]
                    }
                }
            }
        ]
    
    def _extract_locations(self, message: str) -> tuple[str, str]:
        """Simple extraction for origin and destination."""
        message_lower = message.lower()
        if "from" in message_lower and "to" in message_lower:
            parts = message_lower.split("from")[1].split("to")
            if len(parts) == 2:
                origin = parts[0].strip()
                destination = parts[1].strip().split()[0]  # Take first word after "to"
                return origin.title(), destination.title()
        return None, None
    
    def _call_tool(self, tool_call):
        """Execute a tool call."""
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        if function_name in self.tools:
            return self.tools[function_name](**arguments)
        else:
            raise ValueError(f"Unknown tool: {function_name}")
    
    def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """Main orchestrator logic."""
        # Quick check for commute intent
        if not any(keyword in message.lower() for keyword in ["commute", "from", "to", "travel", "carbon", "emissions"]):
            return self._unsupported_response()
        
        # Extract locations
        origin, destination = self._extract_locations(message)
        if not origin or not destination:
            return self._unsupported_response()
        
        # Agent loop
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ]
        
        tool_schemas = self._get_tool_schemas()
        
        max_iterations = 5
        for _ in range(max_iterations):
            response = self.client.chat_completion(
                messages=messages,
                tools=tool_schemas,
                tool_choice="auto"
            )
            
            assistant_message = response.choices[0].message
            messages.append({"role": "assistant", "content": assistant_message.content})
            
            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    tool_result = self._call_tool(tool_call)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result, default=str)
                    })
            else:
                # No more tool calls, get final response
                break
        
        # Parse final response
        final_content = assistant_message.content
        try:
            data = json.loads(final_content)
            return self._format_response(data, origin, destination)
        except:
            # Fallback if parsing fails
            return self._fallback_response(origin, destination)
    
    def _unsupported_response(self) -> Dict[str, Any]:
        return {
            "reply": "I'm sorry, I can only help with commuting sustainability comparisons right now. Try asking about commuting from one place to another!",
            "data": {
                "intent": "unsupported",
                "origin": None,
                "destination": None,
                "scenarios": [],
                "best_option": {"mode": "", "annual_savings_vs_driving_tons": 0, "annual_reduction_percent": 0},
                "improvement_plan": [],
                "assumptions": Assumptions(
                    commute_days_per_year=Config.COMMUTE_DAYS_PER_YEAR,
                    car_type=Config.CAR_TYPE,
                    estimate_quality=Config.ESTIMATE_QUALITY
                )
            }
        }
    
    def _fallback_response(self, origin: str, destination: str) -> Dict[str, Any]:
        # Generate scenarios manually if agent fails
        routes = get_route_options(origin, destination)
        scenarios = []
        driving_emissions = None
        
        for route in routes:
            emissions = estimate_travel_emissions(route.mode, route.distance_miles)
            annualized = annualize_emissions(emissions.co2e_kg_per_trip)
            
            scenario = Scenario(
                name=route.label,
                mode=route.mode,
                co2e_kg_per_trip=emissions.co2e_kg_per_trip,
                co2e_tons_per_year=annualized.co2e_tons_per_year,
                estimated_duration_min=route.duration_min,
                assumptions=emissions.assumptions + [f"{Config.COMMUTE_DAYS_PER_YEAR} commute days/year"]
            )
            scenarios.append(scenario)
            
            if route.mode == "driving":
                driving_emissions = annualized.co2e_tons_per_year
        
        # Find best option
        best = min(scenarios, key=lambda s: s.co2e_tons_per_year)
        savings = driving_emissions - best.co2e_tons_per_year if driving_emissions else 0
        reduction = int((savings / driving_emissions) * 100) if driving_emissions else 0
        
        best_option = BestOption(
            mode=best.mode,
            annual_savings_vs_driving_tons=round(savings, 1),
            annual_reduction_percent=reduction
        )
        
        improvement_plan = [
            "Use public transit for 3 commute days each week",
            "Bike to and from the station for first/last mile",
            "Batch errands on one driving day to reduce extra trips"
        ]
        
        reply = f"Comparing commuting options from {origin} to {destination}. The most sustainable option is {best.name}, saving {savings:.1f} tons of CO2e annually compared to driving."
        
        return {
            "reply": reply,
            "data": {
                "intent": "commute_comparison",
                "origin": origin,
                "destination": destination,
                "scenarios": [s.dict() for s in scenarios],
                "best_option": best_option.dict(),
                "improvement_plan": improvement_plan,
                "assumptions": Assumptions(
                    commute_days_per_year=Config.COMMUTE_DAYS_PER_YEAR,
                    car_type=Config.CAR_TYPE,
                    estimate_quality=Config.ESTIMATE_QUALITY
                ).dict()
            }
        }
    
    def _format_response(self, data: Dict[str, Any], origin: str, destination: str) -> Dict[str, Any]:
        # Ensure proper formatting
        scenarios = [Scenario(**s) for s in data.get("scenarios", [])]
        best_option = BestOption(**data.get("best_option", {}))
        assumptions = Assumptions(**data.get("assumptions", {}))
        
        reply = data.get("reply", f"Comparison complete for {origin} to {destination}")
        
        return {
            "reply": reply,
            "data": {
                "intent": "commute_comparison",
                "origin": origin,
                "destination": destination,
                "scenarios": [s.dict() for s in scenarios],
                "best_option": best_option.dict(),
                "improvement_plan": data.get("improvement_plan", []),
                "assumptions": assumptions.dict()
            }
        }