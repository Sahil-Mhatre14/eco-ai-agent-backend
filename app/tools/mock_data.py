# Mock data for testing and demo purposes

MOCK_COMMUTE_DATA = {
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
    ]
}