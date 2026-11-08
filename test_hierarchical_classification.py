"""
Comprehensive test script for Phase 1 Hierarchical Landmark Classification.
Tests:
1. Panoramic Registan image (entire complex)
2. Individual madrasah image (Sherdor Madrasah)
3. Individual madrasah image (Ulugh Beg Madrasah)
4. Unrelated recognized monument (Gur-e-Amir)
5. Ambiguous / Non-landmark image
"""
import sys
import io
import base64
import json
import zipfile
from pathlib import Path
from PIL import Image

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend.app.services.landmark_classifier_service import landmark_classifier
from backend.app.services.gemini_service import gemini_service

def img_to_base64(img_path_or_bytes):
    if isinstance(img_path_or_bytes, (str, Path)):
        with open(img_path_or_bytes, "rb") as f:
            b = f.read()
    else:
        b = img_path_or_bytes
    return "data:image/jpeg;base64," + base64.b64encode(b).decode("utf-8")

def test_full_pipeline(name, b64_img, context="Testing hierarchical classification"):
    print("\n" + "=" * 70)
    print(f"TEST: {name}")
    print("=" * 70)

    # 1. PyTorch Classification
    clf = landmark_classifier.predict(b64_img)
    print(f"[Classifier Output]")
    print(f"  Top-1 Class:         {clf['raw_class']} ({clf['display_name']})")
    print(f"  Confidence:          {clf['confidence_score']:.1%} [{clf['confidence_level']}]")
    print(f"  Is Registan Domain:  {clf['is_registan_domain']} (Cumulative: {clf['registan_domain_probability']:.1%})")
    print(f"  Scope Ambiguous:     {clf['registan_scope_ambiguous']}")
    print(f"  Hierarchy Level:     {clf['hierarchy_level']}")
    print(f"  Parent Landmark:     {clf['parent_landmark']}")
    top_cands = [(c['display_name'], round(c['confidence'] * 100, 1)) for c in clf['top_candidates']]
    print(f"  Top 3 Candidates:    {top_cands}")

    # 2. Multimodal Scope Disambiguation & Enrichment
    is_reg = clf.get("is_registan_domain", False)
    gemini_res = gemini_service.recognize_landmark(
        image_data=b64_img,
        context_notes=context,
        landmark_hint=clf["display_name"],
        classifier_confidence=clf["confidence_score"],
        hierarchy_context=clf if is_reg else None
    )

    # Resolve final hierarchical output (mirroring /api/landmark/recognize logic)
    final_landmark = clf["display_name"]
    hierarchy_level = clf.get("hierarchy_level", "monument")
    parent_landmark = clf.get("parent_landmark")
    sub_landmarks = clf.get("sub_landmarks", [])

    if is_reg:
        scope = gemini_res.get("scope_determination", "")
        if scope == "full_complex":
            final_landmark = "Registan Complex"
            hierarchy_level = "complex"
            parent_landmark = None
            sub_landmarks = ["Sher-Dor Madrasah", "Tilya-Kori Madrasah & Mosque", "Ulugh Beg Madrasah"]
        elif scope == "individual_monument":
            identified = gemini_res.get("predicted_landmark")
            if identified and identified != "Registan Complex":
                final_landmark = identified
            hierarchy_level = "sub_monument"
            parent_landmark = "Registan Complex"
            sub_landmarks = []
    
    print(f"\n[Final Hierarchical Decision]")
    print(f"  Gemini Scope:        {gemini_res.get('scope_determination', 'N/A')}")
    print(f"  Final Landmark:      {final_landmark}")
    print(f"  Hierarchy Level:     {hierarchy_level}")
    print(f"  Parent Landmark:     {parent_landmark}")
    print(f"  Sub-Landmarks:       {sub_landmarks}")
    print(f"  Historical Summary:  {gemini_res.get('historical_background', '')[:140]}...")
    print(f"  Architectural:       {gemini_res.get('architectural_characteristics', '')[:140]}...")

if __name__ == "__main__":
    print("Initializing Landmark Classifier...")
    landmark_classifier.load_model()

    # 1. Panoramic Registan Square (Wide Angle)
    registan_sample = root_dir / "backend" / "app" / "data" / "sample_landmarks" / "registan.jpg"
    if registan_sample.exists():
        test_full_pipeline("Panoramic Registan Square (Full Complex)", img_to_base64(registan_sample))

    # 2. Individual Madrasah from archive.zip: Sherdor
    zip_path = Path("C:/Users/Admin/Downloads/archive.zip")
    if zip_path.exists():
        with zipfile.ZipFile(zip_path, "r") as z:
            # Pick a Sherdor image
            sherdor_names = [n for n in z.namelist() if "val/Sherdor/" in n and n.endswith(".jpg")]
            if sherdor_names:
                b = z.read(sherdor_names[0])
                test_full_pipeline("Individual Madrasah: Sher-Dor (Close-Up / Façade)", img_to_base64(b))
            
            # Pick an Ulugh Beg Madrasah image
            ulugbek_names = [n for n in z.namelist() if "val/Ulugbek madrasasi/" in n and n.endswith(".jpg")]
            if ulugbek_names:
                b = z.read(ulugbek_names[0])
                test_full_pipeline("Individual Madrasah: Ulugh Beg (Close-Up / Façade)", img_to_base64(b))

    # 3. Unrelated Historical Monument: Gur-e-Amir
    gure_sample = root_dir / "backend" / "app" / "data" / "sample_landmarks" / "gure_amir.jpg"
    if gure_sample.exists():
        test_full_pipeline("Unrelated Historical Monument (Gur-e-Amir)", img_to_base64(gure_sample))

    # 4. Ambiguous / Non-landmark (Synthetic noise or black)
    import numpy as np
    noise_img = Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8))
    buf = io.BytesIO()
    noise_img.save(buf, format="JPEG")
    test_full_pipeline("Ambiguous / Non-Landmark Image (Noise)", img_to_base64(buf.getvalue()))
