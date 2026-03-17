import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
    MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"
    COMMUTE_DAYS_PER_YEAR = 220
    CAR_TYPE = "average gasoline passenger vehicle"
    ESTIMATE_QUALITY = "prototype"