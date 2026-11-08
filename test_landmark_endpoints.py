"""
Landmark endpoint test script.
Run from project root: python test_landmark_endpoints.py
"""
import sys
import base64
import json
import requests
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
SAMPLE_DIR = Path("backend/app/data/sample_landmarks")

def separator(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

# -------------------------------------------------------
# TEST 1: GET /api/landmark/classes
# -------------------------------------------------------
separator("TEST 1: GET /api/landmark/classes")
try:
    r = requests.get(f"{BASE_URL}/api/landmark/classes", timeout=30)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        d = r.json()
        print(f"Architecture : {d['architecture']}")
        print(f"Image size   : {d['image_size']}")
        print(f"Total classes: {d['total_classes']}")
        for cls in d["classes"]:
            meta = cls.get("metadata", {})
            print(f"  [{cls['index']:2d}] {cls['raw_class']:35s} → {meta.get('display_name', 'N/A')}")
    else:
        print("ERROR:", r.text[:500])
except Exception as e:
    print(f"EXCEPTION: {e}")
    sys.exit(1)

# -------------------------------------------------------
# TEST 2: POST /api/landmark/classify-file  (multipart)
# -------------------------------------------------------
separator("TEST 2: POST /api/landmark/classify-file (4 sample images)")

sample_images = list(SAMPLE_DIR.glob("*.jpg")) + list(SAMPLE_DIR.glob("*.png"))
if not sample_images:
    print("No sample images found in", SAMPLE_DIR)
else:
    for img_path in sorted(sample_images):
        try:
            with open(img_path, "rb") as f:
                img_bytes = f.read()
            files = {"file": (img_path.name, img_bytes, "image/jpeg")}
            r = requests.post(f"{BASE_URL}/api/landmark/classify-file", files=files, timeout=30)
            print(f"\nImage: {img_path.name}")
            print(f"  Status: {r.status_code}")
            if r.status_code == 200:
                d = r.json()
                print(f"  Predicted    : {d['predicted_landmark']}")
                print(f"  Display name : {d['display_name']}")
                print(f"  Confidence   : {d['confidence_score'] * 100:.1f}%  [{d['confidence_level']}]")
                print(f"  Is recognized: {d['is_recognized']}")
                print(f"  Top candidates:")
                for c in d.get("top_candidates", []):
                    print(f"    - {c['display_name']}: {c['confidence'] * 100:.1f}%")
            else:
                print(f"  ERROR: {r.text[:300]}")
        except Exception as e:
            print(f"  EXCEPTION for {img_path.name}: {e}")

# -------------------------------------------------------
# TEST 3: POST /api/landmark/classify  (base64)
# -------------------------------------------------------
separator("TEST 3: POST /api/landmark/classify (base64) — gure_amir.jpg")
gure_path = SAMPLE_DIR / "gure_amir.jpg"
if gure_path.exists():
    with open(gure_path, "rb") as f:
        b64 = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()
    try:
        r = requests.post(f"{BASE_URL}/api/landmark/classify", json={"image_base64": b64}, timeout=30)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            d = r.json()
            print(f"Predicted    : {d['predicted_landmark']}")
            print(f"Display name : {d['display_name']}")
            print(f"Confidence   : {d['confidence_score'] * 100:.1f}%  [{d['confidence_level']}]")
            print(f"Is recognized: {d['is_recognized']}")
            print(f"Message      : {d['message']}")
        else:
            print("ERROR:", r.text[:500])
    except Exception as e:
        print(f"EXCEPTION: {e}")
else:
    print(f"File not found: {gure_path}")

# -------------------------------------------------------
# TEST 4: POST /api/landmark/recognize  (full pipeline)
# -------------------------------------------------------
separator("TEST 4: POST /api/landmark/recognize (full pipeline) — gure_amir.jpg")
if gure_path.exists():
    with open(gure_path, "rb") as f:
        b64 = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()
    try:
        payload = {"image_base64": b64, "context_notes": "Testing Gur-e-Amir mausoleum"}
        r = requests.post(f"{BASE_URL}/api/landmark/recognize", json=payload, timeout=60)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            d = r.json()
            print(f"Predicted    : {d['predicted_landmark']}")
            print(f"Confidence   : {d['confidence_score'] * 100:.1f}%  [{d['confidence_level']}]")
            print(f"Is recognized: {d['is_recognized']}")
            print(f"Location     : {d['location']}")
            hist = d.get("historical_background", "")
            print(f"Historical   : {hist[:200]}{'...' if len(hist) > 200 else ''}")
            arch = d.get("architectural_characteristics", "")
            print(f"Architectural: {arch[:200]}{'...' if len(arch) > 200 else ''}")
            tips = d.get("visiting_tips", "")
            print(f"Visiting tips: {tips[:150]}{'...' if len(tips) > 150 else ''}")
        else:
            print("ERROR:", r.text[:500])
    except Exception as e:
        print(f"EXCEPTION: {e}")

print("\n" + "=" * 60)
print("  All tests complete.")
print("=" * 60)
