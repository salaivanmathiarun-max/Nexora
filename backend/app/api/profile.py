import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import UserProfile
from ..schemas.user import UserProfileResponse, UserProfileUpdate, UserProfileCreate

router = APIRouter(prefix="/api/profile", tags=["Profile"])

@router.get("", response_model=UserProfileResponse)
def get_or_create_profile(db: Session = Depends(get_db)):
    """Fetch the active user profile or initialize a default profile."""
    profile = db.query(UserProfile).first()
    if not profile:
        profile = UserProfile(
            name="Traveler",
            language="en",
            accessibility_needs=json.dumps([]),
            preferred_activities=json.dumps(["historical", "cultural", "scenic"]),
            budget_tier="moderate",
            travel_style="balanced",
            dietary_preferences=json.dumps([])
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return UserProfileResponse(
        id=profile.id,
        name=profile.name,
        language=profile.language,
        accessibility_needs=json.loads(profile.accessibility_needs) if profile.accessibility_needs else [],
        preferred_activities=json.loads(profile.preferred_activities) if profile.preferred_activities else [],
        budget_tier=profile.budget_tier,
        travel_style=profile.travel_style,
        dietary_preferences=json.loads(profile.dietary_preferences) if profile.dietary_preferences else [],
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )

@router.post("", response_model=UserProfileResponse)
def update_profile(updates: UserProfileUpdate, db: Session = Depends(get_db)):
    """Update profile preferences, language, or accessibility needs."""
    profile = db.query(UserProfile).first()
    if not profile:
        profile = UserProfile()
        db.add(profile)

    if updates.name is not None:
        profile.name = updates.name
    if updates.language is not None:
        profile.language = updates.language
    if updates.accessibility_needs is not None:
        profile.accessibility_needs = json.dumps(updates.accessibility_needs)
    if updates.preferred_activities is not None:
        profile.preferred_activities = json.dumps(updates.preferred_activities)
    if updates.budget_tier is not None:
        profile.budget_tier = updates.budget_tier
    if updates.travel_style is not None:
        profile.travel_style = updates.travel_style
    if updates.dietary_preferences is not None:
        profile.dietary_preferences = json.dumps(updates.dietary_preferences)

    db.commit()
    db.refresh(profile)

    return UserProfileResponse(
        id=profile.id,
        name=profile.name,
        language=profile.language,
        accessibility_needs=json.loads(profile.accessibility_needs) if profile.accessibility_needs else [],
        preferred_activities=json.loads(profile.preferred_activities) if profile.preferred_activities else [],
        budget_tier=profile.budget_tier,
        travel_style=profile.travel_style,
        dietary_preferences=json.loads(profile.dietary_preferences) if profile.dietary_preferences else [],
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )
