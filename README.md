# Eco AI Agent Backend

AI-powered sustainability commuting assistant backend built with FastAPI and NVIDIA Nemotron.

## Features

- **Commuting Analysis**: Compare driving, public transit, and bike+transit options
- **Emissions Estimation**: Calculate CO2e emissions for different travel modes
- **AI Agent**: Uses NVIDIA Nemotron for intelligent tool calling and response generation
- **Mock Mode**: Works without external APIs for demo purposes
- **FastAPI**: Modern, fast web framework
- **Pydantic**: Data validation and serialization

## Setup

1. **Clone and navigate**:
   ```bash
   git clone <repo-url>
   cd eco-ai-agent-backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your NVIDIA API key if not using mock mode
   ```

## Environment Variables

- `NVIDIA_API_KEY`: Your NVIDIA API key for Nemotron (optional in mock mode)
- `MOCK_MODE`: Set to `true` for demo without real APIs

## Running Locally

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST /api/chat

Chat endpoint for commuting queries using AI agent.

**Request Body**:
```json
{
  "message": "I commute from San Jose to Mountain View.",
  "sessionId": "demo-session-1"
}
```

**Response** (200 OK):
```json
{
  "reply": "Comparing commuting options from San Jose to Mountain View. The most sustainable option is Bike + transit, saving 3.7 tons of CO2e annually compared to driving.",
  "data": {
    "intent": "commute_comparison",
    "origin": "San Jose",
    "destination": "Mountain View",
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
}
```

### GET /api/demo/commute

Demo endpoint returning fixed sample payload (no AI agent call).

Perfect for:
- Testing frontend without backend latency
- Validating response structure and JSON parsing
- Offline development (no network/API keys required)

**Response** (200 OK):
Returns same structure as `/api/chat` but with fixed San Jose → Mountain View data.

```bash
curl http://localhost:8000/api/demo/commute
```

### GET /api/health

Health check endpoint.

**Response** (200 OK):
```json
{
  "ok": true
}
```

## Testing

### Sample curl request:
```bash
curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "I commute from San Jose to Mountain View.",
       "sessionId": "demo-session-1"
     }'
```

## Architecture

- **API Layer**: FastAPI routes with Pydantic validation
- **Agent Layer**: Orchestrator with tool-calling loop using Nemotron
- **Tools**: Modular functions for route options, emissions estimation, and annualization
- **Model Layer**: OpenAI-compatible client for NVIDIA Nemotron
- **Config**: Environment-based configuration

## Switching from Mock to Real APIs

1. Set `MOCK_MODE=false` in `.env`
2. Add your NVIDIA API key
3. Implement real route API in `get_route_options.py` (e.g., Google Routes API)
4. Update emissions factors with more accurate data if needed

## Frontend Integration Guide

The backend is optimized for React frontend integration with structured JSON responses.

### CORS Configuration for Local Development

During development, CORS is configured to allow any origin:
```python
# app/main.py
allow_origins=["*"]  # Development: allow all
```

For production, update to specific frontend URLs:
```python
allow_origins=[
    "https://yourdomain.com",
    "https://app.yourdomain.com",
]
```

### React Integration Example

Complete example showing how to fetch and render responses:

```javascript
import { useState } from 'react';

function CommutePlanner() {
  const [message, setMessage] = useState('');
  const [reply, setReply] = useState('');
  const [scenarios, setScenarios] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const sendMessage = async () => {
    if (!message.trim()) return;

    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          sessionId: `session-${Date.now()}`,
        }),
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`);
      }

      const data = await response.json();
      
      // Display reply in chat bubble
      setReply(data.reply);
      
      // Display scenarios in comparison cards
      setScenarios(data.data.scenarios);
      
      // Use best_option for highlight
      const best = data.data.best_option;
      console.log(`Best option: ${best.mode}, saves ${best.annual_savings_vs_driving_tons} tons/year`);
      
    } catch (err) {
      setError(err.message);
      console.error('Chat error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="I commute from... to..."
        disabled={loading}
      />
      <button onClick={sendMessage} disabled={loading}>
        {loading ? 'Analyzing...' : 'Compare'}
      </button>

      {reply && <div className="chat-bubble">{reply}</div>}

      {scenarios.length > 0 && (
        <div className="scenarios">
          {scenarios.map((scenario) => (
            <div key={scenario.mode} className="card">
              <h3>{scenario.name}</h3>
              <p>Duration: {scenario.estimated_duration_min} min</p>
              <p>Annual CO2e: {scenario.co2e_tons_per_year} tons</p>
            </div>
          ))}
        </div>
      )}

      {error && <div className="error">{error}</div>}
    </div>
  );
}

export default CommutePlanner;
```

### Testing with Demo Endpoint

For frontend development without backend latency or API keys:

```javascript
// Test with demo endpoint
const demoResponse = await fetch('http://localhost:8000/api/demo/commute');
const demoData = await demoResponse.json();
console.log(demoData);  // Fixed San Jose → Mountain View data
```

### Response Data Structure

**Key fields to use in frontend:**

| Field | Purpose | Type |
|-------|---------|------|
| `reply` | Human-readable chat message | string |
| `data.intent` | Validate if request was understood | string |
| `data.origin` | Display start location | string |
| `data.destination` | Display end location | string |
| `data.scenarios` | Array to render comparison cards | array |
| `data.best_option.mode` | Highlight recommended option | string |
| `data.best_option.annual_savings_vs_driving_tons` | Show emissions savings | number |
| `data.improvement_plan` | Display actionable tips | array |

### Error Handling

```javascript
{
  "detail": "Internal server error: ..."  // 500 error response
}
```

Frontend should:
1. Check response status (200 = success, 5xx = error)
2. Parse `.detail` for error messages
3. Show user-friendly error UI
4. Optionally retry with demo endpoint

## Mock Mode vs Real APIs

### Architecture: Two Implementation Paths

The codebase cleanly separates mock and real implementations for easy switching:

```
app/tools/
├── get_route_options.py       ← _get_mock_routes() vs _get_real_routes()
├── estimate_travel_emissions.py ← Uses hardcoded factors (both modes)
└── annualize_emissions.py      ← Pure calculation (both modes)
```

### Mock Mode (Default - MOCK_MODE=true)

**Ideal for:**
- Local development (no network calls)
- Hackathon demos (no API keys needed)
- Frontend testing (instant responses)
- CI/CD pipelines (reproducible data)

**What it provides:**
- Hardcoded route data for San Jose → Mountain View
- Generic fallback for any other route
- Deterministic results (same input = same output)
- Zero external dependencies

**To use:**
```bash
MOCK_MODE=true  # In .env (default)
uvicorn app.main:app --reload
```

### Real Mode (MOCK_MODE=false)

**Ideal for:**
- Production deployment
- Real-world accuracy
- Multi-location support
- Live route/traffic data

**Setup steps:**

1. **Choose a routing service** (implementations in `get_route_options.py`):
   - Google Maps Directions API (comprehensive)
   - OpenStreetMap/OSRM (free, self-hosted)
   - HERE Maps (enterprise support)

2. **Add API key to .env**:
   ```bash
   GOOGLE_MAPS_API_KEY=your_key_here
   MOCK_MODE=false
   ```

3. **Implement real integration** in `app/tools/get_route_options.py`:
   ```python
   def _get_real_routes(origin, destination):
       # Add your API integration here
       # See docstring for examples
       pass
   ```

4. **Test**:
   ```bash
   uvicorn app.main:app --reload
   ```

### Emissions & Annualization

Both mock and real modes use the same emissions calculation:
- Factor-based estimation (kg CO2e per distance)
- Annualization (220 commute days/year default)
- Improvements: integrate CarbonInterfaceAPI if needed

## Architecture

### Component Overview

- **API Layer** (`app/api/routes/`): FastAPI routes with Pydantic validation
- **Agent Layer** (`app/agent/`): Orchestrator with tool-calling loop
  - `orchestrator.py`: Main agent logic, tool coordination
  - `system_prompt.py`: System message for Nemotron
- **Tools Layer** (`app/tools/`):
  - `get_route_options.py`: Mock (default) or real routing API
  - `estimate_travel_emissions.py`: Factor-based CO2e calculation
  - `annualize_emissions.py`: Per-trip to annual conversion
- **Model Layer** (`app/model/`): OpenAI-compatible Nemotron client
- **Schemas** (`app/schemas.py`): Pydantic models for type validation
- **Config** (`app/config.py`): Environment-based settings

### Data Flow

```
User Message
    ↓
POST /api/chat
    ↓
Orchestrator.process_message()
    ↓
Intent Detection ("commute_comparison" → continue, else → unsupported)
    ↓
Location Extraction (parse "from X to Y")
    ↓
get_route_options(origin, destination)
    ├→ MOCK_MODE=true:  hardcoded routes
    └→ MOCK_MODE=false: API call to Google Maps, etc.
    ↓
For each route:
    ├→ estimate_travel_emissions(mode, distance)
    └→ annualize_emissions(kg_per_trip)
    ↓
Best option selection (min emissions)
    ↓
Response formatting
    ↓
ChatResponse (reply + structured data)
    ↓
React frontend renders chat + comparison cards
```

## Development Notes

- Mock mode works without any API keys
- Agent uses tool-calling for structured processing
- Fallback logic ensures responses even if AI fails
- Simple location extraction (enhance with better NLP if needed)
- Emissions factors are hackathon approximations
- Easy to extend: add new tools by updating tool registry in orchestrator