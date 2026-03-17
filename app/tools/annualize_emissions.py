from app.schemas import AnnualizedEmissions
from app.config import Config

def annualize_emissions(co2e_kg_per_trip: float, commute_days_per_year: int = None) -> AnnualizedEmissions:
    """
    Convert per-trip emissions to annual totals.
    
    Default assumes 220 work commute days per year:
      365 days - 52 Saturdays - 52 Sundays - 41 holidays/vacation ≈ 220 days
    
    Customizable for different work schedules:
    - Part-time: 110 days
    - Remote + hybrid: 100-150 days
    - Full-time on-site: 220-240 days
    
    Args:
        co2e_kg_per_trip: Single trip CO2e in kg
        commute_days_per_year: Override default (default: 220)
    
    Returns:
        AnnualizedEmissions with yearly totals in kg and metric tons
    """
    if commute_days_per_year is None:
        commute_days_per_year = Config.COMMUTE_DAYS_PER_YEAR
    
    co2e_kg_per_year = co2e_kg_per_trip * commute_days_per_year
    co2e_tons_per_year = co2e_kg_per_year / 1000
    
    return AnnualizedEmissions(
        co2e_kg_per_year=round(co2e_kg_per_year, 1),
        co2e_tons_per_year=round(co2e_tons_per_year, 1)
    )