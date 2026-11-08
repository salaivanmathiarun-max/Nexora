import os
import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base, SessionLocal
from .models.destination import Destination
from .models.user import UserProfile
from .api.profile import router as profile_router
from .api.query import router as query_router
from .api.itinerary import router as itinerary_router
from .api.context import router as context_router
from .api.landmark import router as landmark_router
from .api.services import router as services_router
from .api.translation import router as translation_router
from .api.memory import router as memory_router
from .services.landmark_classifier_service import landmark_classifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexora.app")

def seed_initial_data():
    """Seeds destinations and default user profile on first boot."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Check destinations
        dest_count = db.query(Destination).count()
        if dest_count == 0:
            seed_file = os.path.join(os.path.dirname(__file__), "data", "seed_destinations.json")
            if os.path.exists(seed_file):
                with open(seed_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        d = Destination(
                            name=item["name"],
                            category=item["category"],
                            city=item["city"],
                            country=item["country"],
                            latitude=item["latitude"],
                            longitude=item["longitude"],
                            opening_time=item.get("opening_time", "09:00"),
                            closing_time=item.get("closing_time", "18:00"),
                            avg_duration_minutes=item.get("avg_duration_minutes", 90),
                            cost_tier=item.get("cost_tier", "moderate"),
                            is_wheelchair_accessible=item.get("is_wheelchair_accessible", True),
                            indoor_outdoor=item.get("indoor_outdoor", "outdoor"),
                            typical_crowd_level=item.get("typical_crowd_level", "moderate"),
                            description=item.get("description", ""),
                            image_url=item.get("image_url", ""),
                            tags=json.dumps(item.get("tags", []))
                        )
                        db.add(d)
                db.commit()
                logger.info("Successfully seeded destinations catalog.")

        # Ensure default user profile exists
        if db.query(UserProfile).count() == 0:
            default_user = UserProfile(
                name="Traveler",
                language="en",
                accessibility_needs=json.dumps([]),
                preferred_activities=json.dumps(["historical", "cultural", "scenic"]),
                budget_tier="moderate",
                travel_style="balanced",
                dietary_preferences=json.dumps([])
            )
            db.add(default_user)
            db.commit()
            logger.info("Default user profile initialized.")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_initial_data()
    landmark_classifier.load_model()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multimodal & Explainable AI Framework for Intelligent Smart Tourism Assistance",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(profile_router)
app.include_router(query_router)
app.include_router(itinerary_router)
app.include_router(context_router)
app.include_router(landmark_router)
app.include_router(services_router)
app.include_router(translation_router)
app.include_router(memory_router)

@app.get("/")
def root():
    return {
        "framework": "NEXORA",
        "version": settings.APP_VERSION,
        "status": "online",
        "description": "Multimodal and Explainable AI Framework for Intelligent Tourism Assistance"
    }
