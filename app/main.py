from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.chat import router as chat_router

app = FastAPI(
    title="Eco AI Agent Backend",
    description="AI-powered sustainability commuting assistant",
    version="1.0.0"
)

# ============================================================================
# CORS CONFIGURATION - Enable cross-origin requests from React frontend
# ============================================================================
# 
# In development: allow_origins=["*"] permits any domain (convenient for testing)
# In production: specify your frontend URL(s) for security
#
# Example production config:
# allow_origins=[
#     "https://myapp.com",
#     "https://www.myapp.com",
#     "https://app-staging.myapp.com"
# ]
#

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api", tags=["chat"])

@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "Eco AI Agent Backend API",
        "docs": "/docs",
        "health": "/api/health",
        "demo": "/api/demo/commute"
    }