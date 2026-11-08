import json
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.landmark import LandmarkLog
from ..services.gemini_service import gemini_service
from ..services.landmark_classifier_service import landmark_classifier, LANDMARK_METADATA

router = APIRouter(prefix="/api/landmark", tags=["Landmark"])

class LandmarkRecognizeRequest(BaseModel):
    image_base64: str = Field(..., description="Base64, data URL, or sample image path of landmark photo")
    context_notes: Optional[str] = Field(default="", description="Optional context notes")

class LandmarkClassifyRequest(BaseModel):
    image_base64: str = Field(..., description="Base64 or data URL of landmark photo to classify")

class CandidatePrediction(BaseModel):
    class_name: str
    display_name: str
    confidence: float

class LandmarkClassificationResponse(BaseModel):
    is_recognized: bool
    predicted_landmark: str
    display_name: str
    raw_class: str
    class_index: int
    confidence_score: float
    confidence_level: str
    location: str
    landmark_type: str
    uzbek_name: str
    top_candidates: List[CandidatePrediction] = Field(default_factory=list)
    all_probabilities: Dict[str, float] = Field(default_factory=dict)
    architecture: str
    message: str
    # Phase 1 Hierarchical Fields
    hierarchy_level: str = "monument"
    parent_landmark: Optional[str] = None
    sub_landmarks: List[str] = Field(default_factory=list)
    is_registan_domain: bool = False
    registan_domain_probability: Optional[float] = None

class LandmarkResponse(BaseModel):
    is_recognized: bool
    confidence_score: float
    confidence_level: str
    predicted_landmark: str
    location: str
    historical_background: str
    cultural_significance: str
    architectural_characteristics: str
    interesting_facts: List[str] = Field(default_factory=list)
    visiting_tips: str
    message: Optional[str] = None
    top_candidates: Optional[List[CandidatePrediction]] = Field(default_factory=list)
    # Phase 1 Hierarchical Fields
    hierarchy_level: str = "monument"             # "complex", "sub_monument", "monument", "uncertain"
    parent_landmark: Optional[str] = None         # e.g., "Registan Complex"
    sub_landmarks: List[str] = Field(default_factory=list) # e.g., ["Sher-Dor", "Tilya-Kori", "Ulugh Beg"]
    view_scope: Optional[str] = None               # "panoramic_ensemble" | "focused_monument" | None

@router.get("/classes")
def get_supported_classes():
    """
    Returns the 12 landmark classes supported by the trained EfficientNet-B0 classifier.
    """
    if not landmark_classifier.is_ready():
        landmark_classifier.load_model()
    
    return {
        "architecture": landmark_classifier.architecture,
        "image_size": landmark_classifier.image_size,
        "total_classes": len(landmark_classifier.class_names),
        "classes": [
            {
                "index": i,
                "raw_class": name,
                "metadata": LANDMARK_METADATA.get(name, {})
            }
            for i, name in enumerate(landmark_classifier.class_names)
        ]
    }

@router.post("/classify", response_model=LandmarkClassificationResponse)
def classify_landmark_base64(req: LandmarkClassifyRequest):
    """
    Direct landmark prediction using the trained EfficientNet-B0 model.
    Accepts an uploaded image (base64/data URL) and returns the predicted landmark name,
    confidence score, uncertainty diagnostics, and all class probabilities.
    """
    if not req.image_base64:
        raise HTTPException(status_code=400, detail="Image data is required.")

    try:
        result = landmark_classifier.predict(req.image_base64)
        return LandmarkClassificationResponse(**result)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Landmark classification failed: {str(e)}")

@router.post("/classify-file", response_model=LandmarkClassificationResponse)
async def classify_landmark_file(file: UploadFile = File(...)):
    """
    Direct landmark prediction accepting a multipart image file upload (.jpg, .png, .webp).
    """
    try:
        image_bytes = await file.read()
        if not image_bytes or len(image_bytes) < 100:
            raise HTTPException(status_code=400, detail="Uploaded file is empty or invalid.")

        result = landmark_classifier.predict(image_bytes)
        return LandmarkClassificationResponse(**result)
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Landmark classification failed: {str(e)}")

@router.post("/recognize", response_model=LandmarkResponse)
def recognize_landmark(req: LandmarkRecognizeRequest, db: Session = Depends(get_db)):
    """
    Complete Multimodal Landmark Pipeline:
    1. Trained PyTorch EfficientNet-B0 classifies the monument and calculates confidence.
    2. Confidence-based uncertainty filter prevents false positive identifications.
    3. Gemini AI synthesizes rich historical provenance, cultural significance, and visiting tips.
    4. Caches search entry into database.
    """
    if not req.image_base64:
        raise HTTPException(status_code=400, detail="Image data is required for landmark recognition.")

    # Step 1: Run PyTorch classification
    try:
        clf_result = landmark_classifier.predict(req.image_base64)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Landmark analysis error: {str(e)}")

    # Step 2: Handle confidence-based uncertainty (Provisional Thresholds)
    # If the image is not recognized AND has no Registan regional domain signal
    if not clf_result["is_recognized"] and not clf_result.get("is_registan_domain"):
        return LandmarkResponse(
            is_recognized=False,
            confidence_score=clf_result["confidence_score"],
            confidence_level="uncertain",
            predicted_landmark="Uncertain / Unfamiliar Landmark",
            location="Unknown",
            historical_background=(
                f"The visual features in this photo did not match any of the 12 recognized Samarkand "
                f"heritage monuments with sufficient certainty (top match: {clf_result['display_name']} at {clf_result['confidence_score']:.1%}, "
                f"below provisional threshold of {landmark_classifier.CONFIDENCE_UNCERTAIN:.0%}). "
                "It may depict an unfamiliar monument, modern structure, or non-landmark scene."
            ),
            cultural_significance="Uncertain identification. Cannot verify historical or religious significance.",
            architectural_characteristics="No distinctive Timurid or Silk Road architectural features could be confidently verified.",
            interesting_facts=[],
            visiting_tips="For optimal landmark recognition, take a clear, well-lit photo capturing the main facade, portal, or dome.",
            message=clf_result["message"],
            top_candidates=[CandidatePrediction(**c) for c in clf_result.get("top_candidates", [])],
            hierarchy_level="uncertain"
        )

    # Step 3: Run Multimodal / Hierarchical Resolution via Gemini Vision
    predicted_name = clf_result["display_name"]
    confidence_score = clf_result["confidence_score"]
    confidence_level = clf_result["confidence_level"]
    is_registan = clf_result.get("is_registan_domain", False)

    gemini_result = gemini_service.recognize_landmark(
        image_data=req.image_base64,
        context_notes=req.context_notes or "",
        landmark_hint=predicted_name,
        classifier_confidence=confidence_score,
        hierarchy_context=clf_result if is_registan else None
    )

    # Check Gemini visual-scope resolution for Registan domain
    hierarchy_level = clf_result.get("hierarchy_level", "monument")
    parent_landmark = clf_result.get("parent_landmark")
    sub_landmarks = clf_result.get("sub_landmarks", [])
    view_scope = None

    if is_registan:
        scope = gemini_result.get("scope_determination", "")
        if scope == "full_complex":
            predicted_name = "Registan Complex"
            hierarchy_level = "complex"
            parent_landmark = None
            sub_landmarks = ["Sher-Dor Madrasah", "Tilya-Kori Madrasah & Mosque", "Ulugh Beg Madrasah"]
            view_scope = "panoramic_ensemble"
            confidence_score = max(confidence_score, clf_result.get("registan_domain_probability", 0.75))
            confidence_level = "high" if confidence_score >= 0.70 else "medium"
        elif scope == "individual_monument":
            identified = gemini_result.get("predicted_landmark")
            if identified and identified != "Registan Complex":
                predicted_name = identified
            hierarchy_level = "sub_monument"
            parent_landmark = "Registan Complex"
            sub_landmarks = []
            view_scope = "focused_monument"
        elif scope == "uncertain" and not clf_result["is_recognized"]:
            # Neither classifier nor Gemini could verify the landmark
            return LandmarkResponse(
                is_recognized=False,
                confidence_score=confidence_score,
                confidence_level="uncertain",
                predicted_landmark="Uncertain / Unfamiliar Landmark",
                location="Unknown",
                historical_background="Visual evidence was insufficient to verify a specific Registan monument or complex view.",
                cultural_significance="Uncertain identification.",
                architectural_characteristics="No conclusive architectural features identified.",
                interesting_facts=[],
                visiting_tips="Try capturing a clearer shot of the portal or entire square.",
                message="Visual scope could not be conclusively determined.",
                top_candidates=[CandidatePrediction(**c) for c in clf_result.get("top_candidates", [])],
                hierarchy_level="uncertain"
            )

    # Step 4: Persist recognition log
    try:
        log = LandmarkLog(
            is_recognized=True,
            predicted_landmark=predicted_name,
            confidence_score=float(confidence_score),
            confidence_level=confidence_level,
            location=clf_result.get("location", "Samarkand"),
            history_summary=gemini_result.get("historical_background", ""),
            cultural_significance=gemini_result.get("cultural_significance", ""),
            architectural_notes=gemini_result.get("architectural_characteristics", ""),
            interesting_facts=json.dumps(gemini_result.get("interesting_facts", [])),
            visiting_tips=gemini_result.get("visiting_tips", "")
        )
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()

    return LandmarkResponse(
        is_recognized=True,
        confidence_score=confidence_score,
        confidence_level=confidence_level,
        predicted_landmark=predicted_name,
        location=gemini_result.get("location", clf_result.get("location", "Samarkand, Uzbekistan")),
        historical_background=gemini_result.get("historical_background", ""),
        cultural_significance=gemini_result.get("cultural_significance", ""),
        architectural_characteristics=gemini_result.get("architectural_characteristics", ""),
        interesting_facts=gemini_result.get("interesting_facts", []),
        visiting_tips=gemini_result.get("visiting_tips", ""),
        message=clf_result.get("message"),
        top_candidates=[CandidatePrediction(**c) for c in clf_result.get("top_candidates", [])],
        # Phase 1 Hierarchical Fields
        hierarchy_level=hierarchy_level,
        parent_landmark=parent_landmark,
        sub_landmarks=sub_landmarks,
        view_scope=view_scope
    )

@router.get("/benchmarks")
def get_research_benchmarks():
    """
    Returns the Samarkand v2 quantitative comparison matrix and confusion matrix
    directly referenced in Section 4 of the research paper.
    """
    benchmark_file = os.path.join(os.path.dirname(__file__), "..", "data", "samarkand_benchmark.json")
    if os.path.exists(benchmark_file):
        with open(benchmark_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"error": "Benchmark data not found"}
