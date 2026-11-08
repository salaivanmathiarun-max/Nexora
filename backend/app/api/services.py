from typing import Optional, List
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/services", tags=["Travel Services"])

@router.get("/nearby")
def get_travel_services(city: str = "Samarkand"):
    """
    Travel Service Integration (Section 3.9 in paper):
    Aggregates accommodation, dining, local transit directions, and emergency assistance.
    """
    return {
        "city": city,
        "accommodations": [
            {
                "name": "Hotel Dilshoda Samarkand",
                "type": "Boutique Heritage Hotel",
                "distance": "0.3 km from Gur-e-Amir",
                "rating": 4.8,
                "price_tier": "$$",
                "wheelchair_accessible": True,
                "perks": ["Traditional Courtyard", "Free Breakfast", "Walking distance to Registan"]
            },
            {
                "name": "Silk Road By Minyoun",
                "type": "Luxury Resort & Spa",
                "distance": "4.2 km from Registan",
                "rating": 4.9,
                "price_tier": "$$$",
                "wheelchair_accessible": True,
                "perks": ["Indoor Pool", "Silk Road Canal View", "Concierge Guided Tours"]
            }
        ],
        "dining": [
            {
                "name": "Platan Restaurant & Wine Garden",
                "cuisine": "Uzbek & European",
                "dietary": ["Halal", "Vegetarian Options", "Gluten-Free upon request"],
                "signature_dish": "Samarkand Osh (Lamb & Yellow Carrot Plov)",
                "rating": 4.7
            },
            {
                "name": "Bibikhanum Teahouse (Choyxona)",
                "cuisine": "Traditional Uzbek Choyxona",
                "dietary": ["Halal", "Vegetarian Manti"],
                "signature_dish": "Herbal Saffron Tea & Hot Tandoor Non",
                "rating": 4.6
            }
        ],
        "transit_options": [
            {
                "mode": "Samarkand Tram (Line 1 & Line 2)",
                "coverage": "Railway Station to Siyob Bazaar",
                "cost": "1,400 UZS (~$0.12)",
                "accessibility": "Step-free ramp entry"
            },
            {
                "mode": "Yandex Go (E-Hailing)",
                "coverage": "Citywide 24/7 on-demand pickup",
                "cost": "15,000 - 30,000 UZS per ride",
                "accessibility": "Select Comfort / Large vehicle options"
            }
        ],
        "emergency_assistance": [
            {"service": "Tourist Police (English Speaking)", "phone": "+998 71 200 00 88"},
            {"service": "Ambulance / Medical Emergency", "phone": "103"},
            {"service": "General Emergency SOS", "phone": "112"},
            {"service": "Samarkand Regional Medical Center", "address": "Spitamen Ave 42, Samarkand", "phone": "+998 66 233 45 67"}
        ]
    }
