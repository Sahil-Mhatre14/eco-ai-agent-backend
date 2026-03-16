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
}
]