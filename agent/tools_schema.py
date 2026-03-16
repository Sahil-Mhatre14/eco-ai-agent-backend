tools = [
{
 "type": "function",
 "function": {
  "name": "get_distance",
  "description": "Calculate distance between two cities",
  "parameters": {
    "type": "object",
    "properties": {
      "origin": {"type": "string"},
      "destination": {"type": "string"}
    },
    "required": ["origin", "destination"]
  }
 }
},
{
 "type": "function",
 "function": {
  "name": "car_emissions",
  "description": "Calculate carbon emissions for a travel mode",
  "parameters": {
    "type": "object",
    "properties": {
      "distance": {"type": "number"},
      "mode": {"type": "string", "enum": ["car", "bus", "train", "flight"]}
    },
    "required": ["distance", "mode"]
  }
 }
},
{
 "type": "function",
 "function": {
  "name": "estimate_cost",
  "description": "Estimate travel cost for a mode",
  "parameters": {
    "type": "object",
    "properties": {
      "distance": {"type": "number"},
      "mode": {"type": "string", "enum": ["car", "bus", "train", "flight"]}
    },
    "required": ["distance", "mode"]
  }
 }
},
{
 "type": "function",
 "function": {
  "name": "estimate_time",
  "description": "Estimate travel time for a mode",
  "parameters": {
    "type": "object",
    "properties": {
      "distance": {"type": "number"},
      "mode": {"type": "string", "enum": ["car", "bus", "train", "flight"]}
    },
    "required": ["distance", "mode"]
  }
 }
}
]