# Registan Complex: Additional Dataset Requirements for Future Retraining Phase

## 1. Context & Motivation
In Phase 1 of NEXORA's landmark classification pipeline, the existing 12-class PyTorch checkpoint (`EfficientNet-B0`) was preserved without modifying model weights. Hierarchical classification for Registan was implemented via:
1. Cumulative regional domain signaling over the three existing madrasah classes (`Sherdor`, `Tillakori madrasasi`, `Ulugbek madrasasi`).
2. Secondary multimodal visual-scope disambiguation via Gemini Vision to distinguish full complex panoramas from focused individual madrasahs.

To transition in a future phase from this hybrid hierarchy to a fully native, 13-class end-to-end classifier (or two-head neural network), a dedicated dataset split for **"Registan Complex (Wide-Angle / Ensemble)"** must be curated.

---

## 2. Quantitative Sample Requirements

| Split | Minimum Images | Recommended Target | Target Class Name |
|---|---|---|---|
| **Training (`train/`)** | 80 images | 120–150 images | `Registan_Complex` |
| **Validation (`val/`)** | 15 images | 20–25 images | `Registan_Complex` |

*Balancing with existing classes:* Existing classes in `original_v2` range from 33 images (`Al-Buxoriy`) to 152 images (`Gur Emir`). Adding 100–120 training images for `Registan_Complex` positions it appropriately alongside `Sherdor` (107), `Tillakori` (97), and `Ulugbek` (126).

---

## 3. Visual Criteria & Perspective Guidelines

### Included Viewpoints (Class: `Registan_Complex`)
1. **Full Plaza Panorama:** Images showing the broad public square with the facades of two or three madrasahs simultaneously visible (e.g., Ulugh Beg on left, Tilya-Kori in center, Sher-Dor on right).
2. **Elevated / Aerial Perspectives:** Elevated angles (e.g. from the entrance pavilion, viewing platform, or aerial drone) capturing the spatial U-shaped layout of the ensemble.
3. **Piazza Street-Level Overview:** Wide-angle tourist photographs taken from the center or southern entry of the square with tourists and ground paving in the foreground.
4. **Night / Illumination Show Overviews:** Panoramic night photographs capturing the illuminated facade of the entire square during sound-and-light cultural performances.

### Excluded Viewpoints (Must remain in Child Madrasah classes)
1. **Single-Facade Centered Shots:** If >60% of the active visual frame is occupied by a single portal or minaret, it must be labelled under the corresponding madrasah (`Sherdor`, `Tillakori madrasasi`, or `Ulugbek madrasasi`).
2. **Courtyard Interiors:** Close-up photographs of inner cells (hujras), madrasah garden courtyards, or the gold mihrab inside Tilya-Kori must be assigned to the specific madrasah.

---

## 4. Provisional Threshold Calibration Protocol

Phase 1 uses provisional heuristic thresholds in `LandmarkClassifierService`:
- `CONFIDENCE_UNCERTAIN = 0.40`: Minimum probability required for confident single-monument identification.
- `PROVISIONAL_REGISTAN_DOMAIN_THRESHOLD = 0.35`: Cumulative probability threshold triggering Registan domain context.
- `PROVISIONAL_CHILD_DOMINANCE_RATIO = 1.6`: Ratio between the top Registan child and second Registan child to establish single-monument focus versus wide-angle ambiguity.

### Empirical Calibration Steps for Future Phase:
1. Once 25 validation images for `Registan_Complex` are assembled, compute precision-recall curves across grid variations:
   - Domain threshold $\tau_d \in [0.25, 0.45]$ with step 0.05.
   - Child dominance ratio $\rho \in [1.3, 2.0]$ with step 0.1.
2. Select $\tau_d$ and $\rho$ that maximize Macro F1 on the holdout validation set while minimizing cross-class leakage (e.g., misclassifying distant Bibi-Khanym portals as Registan).

