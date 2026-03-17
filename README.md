# 🌱 Sustainability AI Agent

An intelligent travel planning assistant that helps users make environmentally conscious transportation decisions by considering carbon emissions, cost, time, and personal constraints.

## 🚀 Features

### Smart Travel Recommendations
- **Multi-modal Analysis**: Compares car, bus, train, and flight options
- **Carbon Footprint Calculation**: Estimates CO2 emissions for each transport mode
- **Constraint-Aware Planning**: Considers budget, time limits, and user preferences
- **Real-time Flight Data**: Integrates with aviation APIs for current flight information

### Intelligent Decision Making
- **Sustainability Priority**: Recommends the most eco-friendly option that meets your constraints
- **Trade-off Analysis**: Shows cost/time/emissions trade-offs between options
- **Fallback Recommendations**: Suggests alternatives when constraints can't be met
- **Detailed Reasoning**: Explains why each recommendation is made

### User-Friendly Interface
- **Web Dashboard**: Modern React frontend for easy interaction
- **Command-Line Interface**: Direct Python API for developers
- **Constraint Specification**: Natural language processing for travel preferences

## 🛠️ Tech Stack

### Backend (Python)
- **FastAPI** - Web framework
- **NVIDIA AI** - LLM for natural language processing
- **Requests** - HTTP client for external APIs
- **AviationStack** - Flight data API
- **Carbon Interface** - Carbon emissions calculations

### Frontend (React/TypeScript)
- **Vite** - Build tool and dev server
- **React** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Modern UI components

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- API Keys (see setup section)

## 🔧 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd sustainability-ai-agent
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
cd eco_agent_backend
pip install -r requirements.txt
```

#### Configure Environment Variables
Create a `.env` file in `eco_agent_backend/`:
```env
# NVIDIA AI API (for LLM processing)
NVIDIA_API_KEY=your_nvidia_api_key_here

# Aviation Stack API (for flight data)
AVIATIONSTACK_API_KEY=your_aviationstack_api_key_here

# Carbon Interface API (for emissions calculations)
CARBON_API_KEY=your_carbon_interface_api_key_here
```

#### Get API Keys
- **NVIDIA AI**: Sign up at [NVIDIA AI](https://ai.nvidia.com/)
- **AviationStack**: Get key at [AviationStack](https://aviationstack.com/)
- **Carbon Interface**: Register at [Carbon Interface](https://www.carboninterface.com/)

### 3. Frontend Setup

#### Install Dependencies
```bash
cd eco_agent_frontend/carbon-compass
npm install
```

#### Start Development Server
```bash
npm run dev
```

### 4. Run the Application

#### Backend (Terminal 1)
```bash
cd eco_agent_backend
python main.py
```

#### Frontend (Terminal 2)
```bash
cd eco_agent_frontend/carbon-compass
npm run dev
```

## 💡 Usage

### Command Line Interface (Local)
```bash
cd eco_agent_backend
python cli.py
```

You can also run a single query (non-interactive):

```bash
python cli.py "Travel from Las Vegas to San Jose sustainably"
```

### API (FastAPI) Usage
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Travel from Las Vegas to San Jose sustainably"}'
```

### API (FastAPI) Usage
Once the backend is running, you can query the agent via HTTP:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Travel from Las Vegas to San Jose sustainably"}'
```

Response format:
```json
{
  "response": "...agent output..."
}
```

### Web Interface
Open your browser to `http://localhost:5173` and use the chat interface to ask travel questions.

Example queries:
- "Travel from Las Vegas to San Jose with a budget of $100 and within 4 hours"
- "I need to get from New York to Boston sustainably"
- "What's the greenest way to travel from Chicago to Miami under $200?"

## 🧠 How It Works

### 1. Query Processing
- Natural language processing extracts origin, destination, and constraints
- Supports flexible constraint specification (budget, time, preferences)

### 2. Data Collection
- Calculates distances between locations
- Fetches real-time flight data
- Estimates costs and travel times for all transport modes

### 3. Carbon Analysis
- Computes CO2 emissions using established factors:
  - Car: 0.404 kg CO2/mile
  - Bus: 0.089 kg CO2/mile
  - Train: 0.041 kg CO2/mile
  - Flight: 0.255 kg CO2/mile

### 4. Intelligent Recommendation
- Prioritizes sustainability while respecting constraints
- Provides detailed reasoning and alternatives
- Handles edge cases gracefully

## 📊 Example Output

```
Route: Las Vegas → San Jose

Travel Analysis for 381.8 miles:

All Options:
• Car: 154.2 kg CO2, $221.44, 6.4 hours
• Bus: 34.0 kg CO2, $57.27, 7.6 hours
• Train: 15.7 kg CO2, $45.81, 5.5 hours
• Flight: 97.4 kg CO2, $95.45, 1.8 hours

Considering your constraints (budget: 200):
🌱 Recommended: Train
• Carbon emissions: 15.7 kg CO2 (10x less than driving)
• Estimated cost: $45.81
• Travel time: 5.5 hours
• Why train? Most sustainable option within your budget
```

## 🏗️ Project Structure

```
sustainability-ai-agent/
├── eco_agent_backend/
│   ├── agent/
│   │   ├── agent.py          # Main agent logic
│   │   ├── prompts.py        # LLM prompts
│   │   └── tools_schema.py   # Tool definitions
│   ├── planner/
│   │   └── carbon_planner.py # Planning algorithms
│   ├── tools/
│   │   ├── carbon_api.py     # Emissions calculations
│   │   ├── flight_search.py  # Flight data
│   │   ├── geocode.py        # Location services
│   │   └── routing.py        # Distance calculations
│   ├── main.py               # CLI entry point
│   └── requirements.txt      # Python dependencies
├── eco_agent_frontend/
│   └── carbon-compass/
│       ├── src/
│       │   ├── components/   # React components
│       │   ├── pages/        # Application pages
│       │   └── lib/          # Utilities
│       ├── package.json      # Node dependencies
│       └── vite.config.ts    # Build configuration
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Add tests for new features
- Update documentation

## 📈 Future Enhancements

- **Real Pricing APIs**: Integration with actual transportation providers
- **Multi-stop Journeys**: Complex route planning
- **Carbon Offsetting**: Built-in offset purchase options
- **Weather Integration**: Weather-dependent recommendations
- **Personal Carbon Tracking**: User history and goals
- **Mobile App**: React Native companion app

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Carbon emissions data from [Carbon Interface](https://www.carboninterface.com/)
- Flight data from [AviationStack](https://aviationstack.com/)
- AI capabilities powered by [NVIDIA AI](https://ai.nvidia.com/)

---

**Making sustainable travel decisions easier, one journey at a time.** 🌍✈️🚌🚆</content>
<parameter name="filePath">/Users/spartan/Desktop/Sustainability AI Agent/README.md