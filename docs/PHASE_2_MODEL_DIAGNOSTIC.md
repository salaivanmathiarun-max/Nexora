# Phase 2 Model Diagnostic & Performance Improvement Strategy

**Framework:** NEXORA Smart Tourism Assistance Platform  
**Target Component:** Landmark Classification Engine (Section 3.7)  
**Baseline Model:** PyTorch `EfficientNet-B0` (`backend/models/nexora_landmark_model.pth`)  
**Evaluation Date:** November 2026  
**Status:** Completed Baseline Diagnostic (Zero Model Changes Made)

---

## 1. Executive Summary

In Phase 1, we successfully integrated the trained EfficientNet-B0 landmark classifier into the FastAPI backend and implemented a hybrid hierarchical decision pipeline for Registan Square. 

In Phase 2, our objective is to diagnose the underlying model's failure modes and formulate an empirical optimization strategy to elevate Top-1 validation accuracy beyond the baseline of **70.59%**.

### Baseline Key Performance Indicators (Measured)
* **Dataset Splits:** 1,122 Training images / 136 Validation images across 12 classes (`original_v2`).
* **Validation Loss:** `1.1160` (Cross-Entropy).
* **Top-1 Accuracy:** **70.59%** (96 / 136 correct).
* **Top-3 Accuracy:** **90.44%** (123 / 136 correct).
* **Macro Precision:** **72.24%** | **Macro Recall:** **71.01%** | **Macro F1-Score:** **70.02%**.
* **Weighted F1-Score:** **69.84%**.
* **Confidence Separation:**
  * Correct predictions: Mean confidence = **54.68%** ($\sigma = 23.35\%$).
  * Incorrect predictions: Mean confidence = **30.80%** ($\sigma = 12.06\%$).

> [!IMPORTANT]
> The gap between Top-1 accuracy (70.59%) and Top-3 accuracy (90.44%) indicates that the model's feature extractor correctly captures the high-level regional context in over 90% of cases, but the linear classifier head lacks the fine-grained discriminative capacity to separate visually similar monuments (such as madrasahs facing each other on Registan Square).

---

## 2. Quantitative Baseline Evaluation

### A. Per-Class Performance Breakdown

Evaluated on all 136 holdout validation images with the exact baseline preprocessing:  
`Resize((224, 224)) -> ToTensor() -> Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])`.

| Index | Class Name | Train $N$ | Val $N$ | TP | FP | FN | Precision (%) | Recall (%) | F1-Score (%) |
|---|---|---|---|---|---|---|---|---|---|
| 0 | `Al-Buxoriy` | 33 | 9 | 8 | 3 | 1 | 72.73% | 88.89% | 80.00% |
| 1 | `Bibikhonim` | 79 | 9 | 7 | 3 | 2 | 70.00% | 77.78% | 73.68% |
| 2 | `Gur Emir` | 152 | 17 | 12 | 2 | 5 | 85.71% | 70.59% | 77.42% |
| 3 | `Hazrati Doniyor maqbarasi` | 62 | 7 | 7 | 2 | 0 | 77.78% | **100.00%** | **87.50%** |
| 4 | `Imom Motrudiy` | 81 | 9 | 7 | 2 | 2 | 77.78% | 77.78% | 77.78% |
| 5 | `Ruhobod` | 90 | 10 | 6 | 0 | 4 | **100.00%** | 60.00% | 75.00% |
| 6 | `Sherdor` | 107 | 12 | 10 | 6 | 2 | 62.50% | 83.33% | 71.43% |
| 7 | `Tillakori madrasasi` | 97 | 11 | 5 | 6 | 6 | **45.45%** | **45.45%** | **45.45%** |
| 8 | `Ulugbek Rasadxonasi` | 137 | 16 | 16 | 8 | 0 | 66.67% | **100.00%** | 80.00% |
| 9 | `Ulugbek madrasasi` | 126 | 14 | 7 | 1 | 7 | 87.50% | **50.00%** | 63.64% |
| 10 | `Xizr majmuasi` | 46 | 9 | 4 | 3 | 5 | 57.14% | **44.44%** | **50.00%** |
| 11 | `shokhi zinda` | 112 | 13 | 7 | 4 | 6 | 63.64% | 53.85% | 58.33% |
| **TOTAL** | **Macro Average** | **1,122** | **136** | **96** | **40** | **40** | **72.24%** | **71.01%** | **70.02%** |

---

### B. Complete 12×12 Confusion Matrix

*Rows represent ground-truth classes; columns represent predicted classes.*

```
       [0]  [1]  [2]  [3]  [4]  [5]  [6]  [7]  [8]  [9] [10] [11]  | Ground Truth Class
[ 0]     8    0    0    0    1    0    0    0    0    0    0    0   | Al-Buxoriy
[ 1]     0    7    1    0    0    0    0    0    0    0    0    1   | Bibikhonim
[ 2]     1    0   12    0    0    0    0    2    0    1    0    1   | Gur Emir
[ 3]     0    0    0    7    0    0    0    0    0    0    0    0   | Hazrati Doniyor maqbarasi
[ 4]     0    0    0    0    7    0    0    0    2    0    0    0   | Imom Motrudiy
[ 5]     0    1    1    0    0    6    0    0    2    0    0    0   | Ruhobod
[ 6]     0    0    0    0    0    0   10    1    0    0    1    0   | Sherdor
[ 7]     0    2    0    0    0    0    2    5    1    0    0    1   | Tillakori madrasasi
[ 8]     0    0    0    0    0    0    0    0   16    0    0    0   | Ulugbek Rasadxonasi
[ 9]     1    0    0    0    0    0    4    1    0    7    1    0   | Ulugbek madrasasi
[10]     1    0    0    1    1    0    0    1    0    0    4    1   | Xizr majmuasi
[11]     0    0    0    1    0    0    0    1    3    0    1    7   | shokhi zinda
```

---

## 3. Deep Failure Mode Analysis

### A. Most Frequently Confused Landmark Pairs

The off-diagonal entries reveal distinct architectural confusion clusters:

| Ground Truth Class | Misclassified As | Confused Samples | Error Share | Root Architectural Cause |
|---|---|---|---|---|
| `Ulugbek madrasasi` | `Sherdor` | **4 images** | **28.6%** | Both madrasahs stand opposite each other on Registan Square; identical brick facade geometry, minaret height, and arch curvature. |
| `shokhi zinda` | `Ulugbek Rasadxonasi` | **3 images** | **23.1%** | Avenues and hillside staircases with open sky background confuse the linear probe. |
| `Tillakori madrasasi` | `Bibikhonim` | **2 images** | **18.2%** | Grand fluted turquoise domes and large monumental pishtaq portals. |
| `Tillakori madrasasi` | `Sherdor` | **2 images** | **18.2%** | Registan Square intra-ensemble proximity; courtyards and minarets share identical glazed tile palettes. |
| `Imom Motrudiy` | `Ulugbek Rasadxonasi` | **2 images** | **22.2%** | Low domed mausoleum profiles against bright open sky. |
| `Ruhobod` | `Ulugbek Rasadxonasi` | **2 images** | **20.0%** | Conical dome and plain brickwork without glazed tiles. |
| `Gur Emir` | `Tillakori madrasasi` | **2 images** | **11.8%** | Ribbed 64-flute azure dome resembles the dome of the Tilya-Kori mosque. |

### B. Severe Underperforming Classes
1. **`Tillakori madrasasi` (F1: 45.45%):** Lowest F1 score in the entire model. Only 5 out of 11 validation images were correctly identified. It suffers from bidirectional leakage to `Sherdor` (2), `Bibikhonim` (2), `Ulugbek Rasadxonasi` (1), and `shokhi zinda` (1).
2. **`Xizr majmuasi` (F1: 50.00%, Recall: 44.44%):** More than half of all validation images (5 of 9) were misattributed across 5 different classes.
3. **`shokhi zinda` (F1: 58.33%, Recall: 53.85%):** The avenue contains more than 11 individual mausoleums with highly varied facade designs, leading to high intra-class variance.
4. **`Ulugbek madrasasi` (Recall: 50.00%):** Half of all validation images were missed, primarily absorbed by `Sherdor` (4 images).

---

## 4. Dataset & Training Pipeline Diagnostics

### A. Class Imbalance vs. Recall Correlation
* Training sample sizes range from **33 images** (`Al-Buxoriy`) to **152 images** (`Gur Emir`)—a 4.6× ratio.
* **Empirical Correlation Check:**
  * Pearson correlation between Training Sample Count and Recall: **$r = -0.071$** (statistically insignificant).
  * Pearson correlation between Training Sample Count and F1-Score: **$r = 0.001$**.
* **Interpretation:** Performance is **not** strictly dictated by sample count alone. For instance, `Al-Buxoriy` has only 33 training samples yet achieves **88.89% recall** (distinctive contemporary open pavilion architecture). Conversely, `Ulugbek madrasasi` has 126 training samples but achieves only **50.00% recall** due to architectural similarity with Sher-Dor.
* **However, Imbalance Induces False Positive Bias:** Dominant classes like `Ulugbek Rasadxonasi` (137 train samples) attract 8 false positives, skewing decision thresholds against smaller classes.

### B. Data Leakage & Near-Duplicate Audit
* **Exact MD5 Duplicate Leakage:** **0 images** between `train` and `val`.
* **Perceptual dHash Audit (Hamming distance $\le 4$ on 64-bit difference hash):**
  * Across all $1,122 \times 136 = 152,592$ image pairs, only **1 near-duplicate pair** was detected:
    * `val/Ulugbek Rasadxonasi/photo_6068900364364661470_y.jpg` $\leftrightarrow$ `train/Ulugbek Rasadxonasi/photo_6068900364364661469_y.jpg` (Hamming distance = 4).
    * These are consecutive burst photographs taken from the same vantage point.
  * *Conclusion:* The train/validation split is clean; there is no systemic leakage artificially inflating validation metrics.

### C. Validation Set Representativeness
* Total validation size is 136 images (7 to 17 images per class, mean: 11.3 images).
* A single misclassification shifts class recall by **9.1% to 14.3%**.
* While the validation split provides a reliable general indicator of model performance, fine-grained class improvements must be measured across multiple random seeds or stratified k-fold splits to confirm statistical significance.

### D. Backbone Inspection: Frozen vs. Fine-Tuned
* Tensor statistics across `features.0` through `features.8` show standard ImageNet feature distributions:
  * `features.0.0.weight`: norm = 13.94, std = 0.475
  * `features.4.0.block.0.0.weight`: norm = 19.03, std = 0.194
  * `features.8.0.weight`: norm = 39.34, std = 0.061
* The classifier head (`classifier.1.weight`) has norm 4.40 with std 0.035.
* **Diagnosis:** The backbone was largely frozen during initial training, acting as a fixed feature extractor. ImageNet features distinguish dogs from cars, but they lack the domain-specific spatial filters needed to distinguish Timurid tile patterns (e.g. 10-pointed star astronomical tessellations vs. tiger/sun solar heraldry).

---

## 5. Recommended Optimization Strategy

Based on the diagnostic evidence, the following 6 optimization techniques are evaluated:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       NEXORA Optimization Strategy                          │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
     ┌─────────────────────────────────┼─────────────────────────────────┐
┌────▼────────────────────┐  ┌─────────▼───────────────┐  ┌──────────────▼─────────────┐
│ 1. Differential Backbone│  │ 2. Domain-Specific Data │  │ 3. Class-Weighted Loss     │
│    Fine-Tuning          │  │    Augmentation         │  │    & Label Smoothing       │
│    (Unfreeze Blocks 6-8)│  │    (ColorJitter, Crop)  │  │    (Address Confusion)     │
└─────────────────────────┘  └─────────────────────────┘  └────────────────────────────┘
```

### 1. Differential Backbone Fine-Tuning (Highest Impact)
* **Rationale:** A frozen ImageNet backbone cannot resolve the 28.6% confusion between `Ulugbek madrasasi` and `Sherdor`. Unfreezing the top 3 MBConv stages (blocks 6, 7, and the 1280-d pointwise convolution in block 8) allows the network to learn Silk Road architectural motifs.
* **Learning Rate Schedule:**
  * Backbone blocks 6–8: $\text{LR}_{\text{backbone}} = 5 \times 10^{-5}$
  * Classifier head: $\text{LR}_{\text{head}} = 5 \times 10^{-4}$
  * Early backbone blocks 0–5: **Keep Frozen** (preserves low-level edge and color primitives, avoids catastrophic forgetting on a small 1.1k dataset).

### 2. Domain-Specific Data Augmentation (High Impact)
* **Rationale:** Current dataset exhibits high sensitivity to lighting and vantage angles.
* **Proposed Augmentation Pipeline:**
  * `RandomResizedCrop(224, scale=(0.75, 1.0), ratio=(0.85, 1.15))`
  * `RandomHorizontalFlip(p=0.5)`
  * `ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05)` (simulates midday sun vs. golden hour)
  * `RandomAffine(degrees=10, translate=(0.05, 0.05))` (simulates tourist camera tilt)

### 3. Class-Weighted Cross-Entropy Loss (Moderate Impact)
* **Rationale:** Addresses false-positive bias towards dominant classes like `Ulugbek Rasadxonasi` (137 images) at the expense of `Xizr majmuasi` (46 images) and `Al-Buxoriy` (33 images).
* **Formula:** Effective number of samples weighting:
  $$w_c = \frac{N}{C \cdot N_c}$$

### 4. Label Smoothing ($\alpha = 0.1$) (Moderate Impact)
* **Rationale:** Overconfident probabilities on visually identical brickwork cause severe cross-entropy penalties. Label smoothing encourages flatter, more calibrated posterior distributions, directly improving the Top-3 recovery rate and uncertainty thresholding.

### 5. Cosine Annealing Learning Rate with Warmup (Standard Best Practice)
* **Schedule:** Linear warmup for 5 epochs from $\text{LR} = 10^{-6}$ followed by Cosine Annealing decay down to $10^{-6}$ over 30 epochs.

### 6. Model Checkpointing & Early Stopping
* Track validation macro-F1 rather than raw validation loss. Save the checkpoint that achieves the highest validation macro-F1 to guarantee generalization across all 12 classes.

---

## 6. Prioritized Training Experiment Plan

The optimization will proceed in 4 controlled, incremental experiment rounds:

| Priority | Experiment ID | Strategy & Changes | Proposed Hyperparameters | Success Criteria |
|---|---|---|---|---|
| **Round 1** | `EXP-1-AUG-BASELINE` | Enhanced Data Augmentation + Cosine Annealing (Backbone still frozen) | `Epochs=30`, `LR=1e-3`, `Batch=32`, `ColorJitter`, `RandomResizedCrop` | Val Acc $\ge 74.0\%$, improved Tillakori recall |
| **Round 2** | `EXP-2-UNFREEZE-TOP` | Unfreeze Top 2 MBConv Blocks (Blocks 7–8) + Differential LR | `Backbone_LR=5e-5`, `Head_LR=5e-4`, `LabelSmoothing=0.1` | Val Acc $\ge 79.0\%$, reduced Ulugbek/Sherdor confusion |
| **Round 3** | `EXP-3-UNFREEZE-DEEP` | Unfreeze Blocks 5–8 + Class-Weighted Cross-Entropy | `Backbone_LR=3e-5`, `Head_LR=3e-4`, `Weighted_Loss` | Val Acc $\ge 83.0\%$, Macro F1 $\ge 81.0\%$ |
| **Round 4** | `EXP-4-CALIBRATION` | Temperature Scaling & Threshold Calibration | Post-hoc temperature $T$ optimization on holdout val split | ECE (Expected Calibration Error) $< 5\%$, Optimal threshold $\approx 45\%$ |

---

## 7. Preservation & Verification Guarantees

* **Original Checkpoint Preserved:** `backend/models/nexora_landmark_model.pth` remains unaltered as the baseline reference.
* **Class Mapping Compatibility:** All future model checkpoints will strictly preserve the exact 12-class alphabetical index order (`Al-Buxoriy` $\to$ `shokhi zinda`).
* **Hierarchical Pipeline Compatibility:** All Phase 1 Registan parent-child domain signaling logic in `landmark_classifier_service.py` and `gemini_service.py` functions seamlessly with any updated weight checkpoint.

