# Experiment Report: EXP-1-AUG-BASELINE

**Framework:** NEXORA Smart Tourism Assistance Platform  
**Target Component:** Samarkand Landmark Classifier (Phase 2, Round 1)  
**Model Architecture:** PyTorch `EfficientNet-B0` (Frozen Backbone)  
**Baseline Model:** `backend/models/nexora_landmark_model.pth` (Preserved, Untouched)  
**Experiment Checkpoint:** `backend/models/nexora_landmark_model_exp1.pth` (Best: Epoch 23)  
**Dataset:** `Samarkand_v2` (`original_v2`: 1,122 Train / 136 Validation across 12 classes)  
**Execution Date:** November 3, 2026  
**Status:** Completed Successfully

---

## 1. Executive Summary

In Round 1 of Phase 2 (**EXP-1-AUG-BASELINE**), our primary hypothesis was that the existing `EfficientNet-B0` linear classification head was severely under-trained and suffered from data starvation due to the lack of training augmentations, rather than an immediate limitation of the feature extractor.

To validate this hypothesis while preserving stability:
1. The **entire EfficientNet-B0 backbone** (4,007,548 parameters) remained strictly **frozen**.
2. Only the linear classification head (`model.classifier[1]`, 15,372 parameters) was trained.
3. Domain-appropriate spatial, perspective, and photometric augmentations were applied to the training set.
4. The holdout validation set (136 images) was evaluated deterministically using the exact baseline preprocessing.

### Headline Results Comparison

| Metric | Baseline (`nexora_landmark_model.pth`) | EXP-1 (`nexora_landmark_model_exp1.pth`) | Absolute Delta | Relative Gain |
|:---|:---:|:---:|:---:|:---:|
| **Top-1 Accuracy** | **70.59%** (96 / 136) | **83.09%** (113 / 136) | **+12.50%** | **+17.7%** |
| **Top-3 Accuracy** | **90.44%** (123 / 136) | **93.38%** (127 / 136) | **+2.94%** | **+3.2%** |
| **Macro Precision** | **72.24%** | **86.13%** | **+13.89%** | **+19.2%** |
| **Macro Recall** | **71.01%** | **81.36%** | **+10.35%** | **+14.6%** |
| **Macro F1-Score** | **70.02%** | **82.67%** | **+12.65%** | **+18.1%** |
| **Weighted F1-Score** | **69.84%** | **82.74%** | **+12.90%** | **+18.5%** |
| **Validation Loss** | `1.1160` | **`0.6319`** | **-0.4841** | **-43.4%** |
| **Mean Conf. (Correct)** | 54.68% ($\sigma=23.35\%$) | **79.73%** | **+25.05%** | **+45.8%** |
| **Mean Conf. (Incorrect)** | 30.80% ($\sigma=12.06\%$) | **42.27%** | **+11.47%** | **+37.2%** |
| **Confidence Gap** | +23.88% | **+37.46%** | **+13.58%** | **Sharper separation** |

> [!IMPORTANT]
> Without altering a single weight in the EfficientNet-B0 backbone, domain-appropriate data augmentation alone delivered a **+12.50% absolute increase in Top-1 accuracy** (from 70.59% to 83.09%) and lowered validation loss by **43.4%**. The critical severe underperformers from the baseline diagnostic (`Tillakori`, `Ulugbek madrasasi`, `Xizr majmuasi`, `shokhi zinda`) all exhibited massive recoveries.

---

## 2. Experiment Setup & Architectural Safeguards

### A. Architectural & Checkpoint Constraints
* **Baseline Preservation:** The production model checkpoint `backend/models/nexora_landmark_model.pth` was opened strictly read-only and remains completely byte-identical (`SHA256: f487e8f7...`, size: 16,395,571 bytes).
* **New Checkpoint:** The best-performing model checkpoint was saved separately to:
  `backend/models/nexora_landmark_model_exp1.pth` (size: 16,377,433 bytes).
* **Class Mapping Preservation:** All 12 classes and index positions `[0..11]` were preserved identically:
  `['Al-Buxoriy', 'Bibikhonim', 'Gur Emir', 'Hazrati Doniyor maqbarasi', 'Imom Motrudiy', 'Ruhobod', 'Sherdor', 'Tillakori madrasasi', 'Ulugbek Rasadxonasi', 'Ulugbek madrasasi', 'Xizr majmuasi', 'shokhi zinda']`.
* **Zero Disruption to Hierarchical Registan:** All API routes, Pydantic schemas, and fallback logic remain 100% compatible.

### B. Training Configuration & Hyperparameters
* **Parameter Split:**
  * Trainable Parameters: **15,372** (`model.classifier[1].weight` $[12 \times 1280]$ + `bias` $[12]$)
  * Frozen Parameters: **4,007,548** (`model.features.*` and `model.avgpool.*` with `requires_grad=False`)
* **Optimization:**
  * Optimizer: `AdamW` (learning rate: $1.0 \times 10^{-3}$, weight decay: $1.0 \times 10^{-4}$)
  * Learning Rate Schedule: `CosineAnnealingLR` ($T_{\max}=30$, $\eta_{\min}=1.0 \times 10^{-6}$)
  * Loss Function: `nn.CrossEntropyLoss()`
  * Epochs: 30 epochs (wall-clock time: 46.09 minutes on 6 CPU threads)
  * Reproducibility Seed: `torch.manual_seed(42)`, `np.random.seed(42)`

### C. Data Augmentation Pipeline
* **Training Pipeline (Stochastic):**
  1. `transforms.RandomResizedCrop(224, scale=(0.75, 1.0), ratio=(0.85, 1.15))`: Simulates user framing variability and different camera focal lengths while preventing excessive cropping of key architectural features.
  2. `transforms.RandomHorizontalFlip(p=0.5)`: Exploits bilateral symmetry of Timurid portals, iwans, and madrasah facades.
  3. `transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05)`: Simulates varied lighting conditions across harsh desert sunlight, golden hour, and overcast skies.
  4. `transforms.ToTensor()` + `transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])`.
* **Validation Pipeline (Deterministic Holdout):**
  1. `transforms.Resize((224, 224))`
  2. `transforms.ToTensor()` + `transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])`
  * Exactly identical to the original evaluation protocol on all 136 validation images.

---

## 3. Epoch-by-Epoch Metric Trajectory

The complete training run progressed across 30 epochs without divergence or instability:

| Epoch | Train Loss | Train Acc (%) | Val Loss | Val Acc (%) | Val Macro-F1 (%) | Learning Rate | Status / Notes |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **Baseline** | — | — | `1.1160` | **70.59%** | **70.02%** | — | *Original Baseline Checkpoint* |
| **1** | 1.0113 | 75.76% | 0.9978 | 68.38% | 68.29% | 0.001000 | Initial alignment |
| **2** | 0.8439 | 79.23% | 0.9140 | 74.26% | 74.34% | 0.000997 | ★ Surpassed baseline (+3.67%) |
| **3** | 0.7308 | 83.07% | 0.8723 | 77.21% | 76.95% | 0.000989 | ★ Steady gain |
| **4** | 0.6810 | 83.87% | 0.8282 | 78.68% | 78.29% | 0.000976 | ★ Steady gain |
| **5** | 0.6176 | 86.72% | 0.7959 | 79.41% | 79.02% | 0.000957 | ★ Approaching 80% |
| **6** | 0.5619 | 87.34% | 0.7795 | 77.94% | 77.54% | 0.000933 | Minor fluctuation |
| **7** | 0.5216 | 88.68% | 0.7393 | 80.15% | 79.70% | 0.000905 | ★ Broke 80% mark |
| **8** | 0.5068 | 88.77% | 0.7247 | 79.41% | 78.73% | 0.000872 | Consolidating |
| **9** | 0.4785 | 89.39% | 0.7103 | 80.15% | 79.70% | 0.000835 | Loss drop continues |
| **10** | 0.4438 | 90.73% | 0.7032 | 80.15% | 79.55% | 0.000794 | High train accuracy |
| **11** | 0.4345 | 90.55% | 0.6929 | 80.88% | 80.53% | 0.000750 | ★ Macro-F1 broke 80% |
| **12** | 0.4196 | 90.91% | 0.6848 | 80.15% | 79.70% | 0.000704 | Loss under 0.70 |
| **13** | 0.3926 | 92.51% | 0.6754 | 80.88% | 80.27% | 0.000655 | Solid generalization |
| **14** | 0.3848 | 92.51% | 0.6686 | 81.62% | 81.13% | 0.000604 | ★ Broke 81% mark |
| **15** | 0.3511 | 93.49% | 0.6603 | 80.88% | 80.42% | 0.000553 | Loss continues down |
| **16** | 0.3533 | 93.49% | 0.6570 | 81.62% | 81.13% | 0.000501 | Stable |
| **17** | 0.3474 | 92.51% | 0.6537 | 81.62% | 81.07% | 0.000448 | Stable |
| **18** | 0.3466 | 93.58% | 0.6472 | 82.35% | 82.03% | 0.000397 | ★ Broke 82% mark |
| **19** | 0.3279 | 93.85% | 0.6453 | 82.35% | 82.03% | 0.000346 | High confidence |
| **20** | 0.3348 | 93.23% | 0.6434 | 82.35% | 82.03% | 0.000297 | Stable plateau |
| **21** | 0.3259 | 93.67% | 0.6378 | 82.35% | 82.09% | 0.000251 | ★ Macro-F1 uptick |
| **22** | 0.3230 | 93.67% | 0.6350 | 82.35% | 82.03% | 0.000207 | Loss under 0.64 |
| **23** | **0.3100** | **94.12%** | **0.6319** | **83.09%** | **82.67%** | **0.000166** | ★ **PEAK BEST CHECKPOINT** |
| **24** | 0.3041 | 94.47% | 0.6291 | 83.09% | 82.33% | 0.000129 | Minimal loss |
| **25** | 0.3118 | 94.56% | 0.6285 | 83.09% | 82.33% | 0.000096 | Min Val Loss (0.6285) |
| **26** | 0.3012 | 94.83% | 0.6287 | 83.09% | 82.33% | 0.000068 | Convergence |
| **27** | 0.3045 | 94.39% | 0.6296 | 83.09% | 82.19% | 0.000044 | Convergence |
| **28** | 0.3208 | 93.67% | 0.6299 | 83.09% | 82.19% | 0.000025 | LR near zero |
| **29** | 0.3105 | 94.65% | 0.6296 | 83.09% | 82.19% | 0.000012 | LR near zero |
| **30** | 0.3174 | 93.40% | 0.6296 | 83.09% | 82.19% | 0.000004 | Final step |

```
Validation Accuracy Trajectory (%)
85 |                                             * * * * * * * *
80 |                             * - * * * * - *
75 |                 * * * - *
70 | Baseline: 70.6%
65 | *
   +-------------------------------------------------------------
     E1  E3  E5  E7  E9  E11 E13 E15 E17 E19 E21 E23 E25 E27 E29
```

---

## 4. Per-Class Performance Breakdown & Delta Analysis

The table below directly contrasts the baseline diagnostic metrics against EXP-1 for all 12 landmark classes on the 136 validation images:

| Index | Landmark Class | Val $N$ | Baseline F1 (%) | EXP-1 F1 (%) | Baseline Prec. (%) | EXP-1 Prec. (%) | Baseline Rec. (%) | EXP-1 Rec. (%) | $\Delta$ F1-Score |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0 | `Al-Buxoriy` | 9 | 80.00% | **87.50%** | 72.73% | **100.00%** | 88.89% | 77.78% | **+7.50%** |
| 1 | `Bibikhonim` | 9 | 73.68% | **75.00%** | 70.00% | **85.71%** | 77.78% | 66.67% | **+1.32%** |
| 2 | `Gur Emir` | 17 | 77.42% | **84.21%** | 85.71% | 76.19% | 70.59% | **94.12%** | **+6.79%** |
| 3 | `Hazrati Doniyor maqbarasi` | 7 | 87.50% | **100.00%** | 77.78% | **100.00%** | 100.00% | **100.00%** | **+12.50%** |
| 4 | `Imom Motrudiy` | 9 | 77.78% | **82.35%** | 77.78% | **87.50%** | 77.78% | 77.78% | **+4.57%** |
| 5 | `Ruhobod` | 10 | 75.00% | **84.21%** | 100.00% | 88.89% | 60.00% | **80.00%** | **+9.21%** |
| 6 | `Sherdor` | 12 | 71.43% | **83.33%** | 62.50% | **83.33%** | 83.33% | 83.33% | **+11.90%** |
| 7 | `Tillakori madrasasi` | 11 | **45.45%** | **70.00%** | **45.45%** | **77.78%** | **45.45%** | **63.64%** | **+24.55%** |
| 8 | `Ulugbek Rasadxonasi` | 16 | 80.00% | **91.43%** | 66.67% | **84.21%** | 100.00% | 100.00% | **+11.43%** |
| 9 | `Ulugbek madrasasi` | 14 | **63.64%** | **86.67%** | 87.50% | 81.25% | **50.00%** | **92.86%** | **+23.03%** |
| 10 | `Xizr majmuasi` | 9 | **50.00%** | **71.43%** | 57.14% | **100.00%** | **44.44%** | **55.56%** | **+21.43%** |
| 11 | `shokhi zinda` | 13 | **58.33%** | **75.86%** | 63.64% | **68.75%** | **53.85%** | **84.62%** | **+17.53%** |
| **ALL** | **Macro Average** | **136** | **70.02%** | **82.67%** | **72.24%** | **86.13%** | **71.01%** | **81.36%** | **+12.65%** |

---

## 5. Confusion Matrix Analysis & Error Diagnosis

### Complete 12×12 Confusion Matrix (EXP-1 Checkpoint at Epoch 23)

*Rows represent ground-truth classes; columns represent predicted classes.*

```
       [0]  [1]  [2]  [3]  [4]  [5]  [6]  [7]  [8]  [9] [10] [11]  | Ground Truth Class
[ 0]     7    1    0    0    1    0    0    0    0    0    0    0   | Al-Buxoriy (N=9)
[ 1]     0    6    1    0    0    1    0    0    0    0    0    1   | Bibikhonim (N=9)
[ 2]     0    0   16    0    0    0    0    0    0    0    0    1   | Gur Emir (N=17)
[ 3]     0    0    0    7    0    0    0    0    0    0    0    0   | Hazrati Doniyor maqbarasi (N=7)
[ 4]     0    0    1    0    7    0    0    0    1    0    0    0   | Imom Motrudiy (N=9)
[ 5]     0    0    0    0    0    8    0    0    1    1    0    0   | Ruhobod (N=10)
[ 6]     0    0    0    0    0    0   10    0    0    2    0    0   | Sherdor (N=12)
[ 7]     0    0    1    0    0    0    1    7    1    0    0    1   | Tillakori madrasasi (N=11)
[ 8]     0    0    0    0    0    0    0    0   16    0    0    0   | Ulugbek Rasadxonasi (N=16)
[ 9]     0    0    0    0    0    0    1    0    0   13    0    0   | Ulugbek madrasasi (N=14)
[10]     0    0    2    0    0    0    0    0    0    0    5    2   | Xizr majmuasi (N=9)
[11]     0    0    0    0    0    0    0    2    0    0    0   11   | shokhi zinda (N=13)
```

### Major Resolved Confusions

1. **`Ulugbek madrasasi` vs. `Sherdor` Madrasah:**
   * *Baseline:* 4 out of 14 images of `Ulugbek madrasasi` were misclassified as `Sherdor` (recall was an abysmal 50.00%).
   * *EXP-1:* Only **1 image** was misclassified as `Sherdor`. Recall surged from **50.00% to 92.86% (13/14 correct)**, elevating F1 from 63.64% to **86.67%**.
   * *Cause of Resolution:* Scale and crop augmentation prevented the classifier from solely relying on global arch framing, forcing the weights to attend to unique tile patterns (e.g. geometric star constellations vs. tiger/sun).

2. **`Tillakori madrasasi` Bidirectional Confusion:**
   * *Baseline:* Suffered from severe cross-confusion with `Bibikhonim` (2), `Sherdor` (2), `Ulugbek Rasadxonasi` (1), and `shokhi zinda` (1), yielding F1 of 45.45%.
   * *EXP-1:* Confusion with `Bibikhonim` was **completely eliminated (0 errors)**. Precision climbed from 45.45% to **77.78%** and F1 reached **70.00% (+24.55% gain)**.

3. **`Gur Emir` Precision & Recall:**
   * *Baseline:* 5 false negatives (scattered across Al-Buxoriy, Tillakori, Ulugbek madrasasi, shokhi zinda).
   * *EXP-1:* Recall jumped from 70.59% to **94.12% (16/17 correct)**. The 64-flute turquoise ribbed dome is now reliably identified under varying lighting conditions.

4. **`Hazrati Doniyor maqbarasi`:**
   * Achieved **100.00% Precision, 100.00% Recall, and 100.00% F1-score (7/7 correct, 0 false positives)**.

5. **`Ulugbek Rasadxonasi`:**
   * Retained **100.00% Recall (16/16 correct)** while false positives dropped from 8 down to 3, boosting precision from 66.67% to **84.21%** and F1 to **91.43%**.

### Remaining Failure Modes & Confusion Clusters

| Ground Truth Class | Misclassified As | Error Count | Root Architectural Explanation |
|:---|:---|:---:|:---|
| `Sherdor` | `Ulugbek madrasasi` | 2 images | Both madrasahs stand directly opposite on Registan Square; when images show partial side portals or courtyards, tile heraldry is cropped out. |
| `Ulugbek madrasasi` | `Sherdor` | 1 image | Residual Registan intra-ensemble symmetry. |
| `Xizr majmuasi` | `Gur Emir` (2), `shokhi zinda` (2) | 4 images | Hazrat Khizr features elevated masonry foundations and wooden columns on the hillside, which share textural similarities with Shahi Zinda alleyways and stone plinths. |
| `Tillakori madrasasi` | `Gur Emir` (1), `Sherdor` (1), `Ulugbek Rasadxonasi` (1), `shokhi zinda` (1) | 4 images | Tilya-Kori acts as a hybrid mosque-madrasah; its central gilded dome and open courtyard still produce minor residual ambiguity. |
| `shokhi zinda` | `Tillakori madrasasi` | 2 images | Highly ornamented cobalt-and-gold entrance portal resembles Tilya-Kori's golden interior tiling. |

---

## 6. Confidence Separation Analysis

```
Baseline Separation:
[========== Incorrect: 30.8% ==========]
                   [========== Correct: 54.7% ==========]
                   |<- Gap: 23.9% ->|

EXP-1 Separation:
[============= Incorrect: 42.3% =============]
                                   [================ Correct: 79.7% ================]
                                   |<--------------- Gap: 37.5% --------------->|
```

* **Mean Confidence for Correct Predictions:** Surged from **54.68% to 79.73% (+25.05% gain)**. Correct classifications are no longer lingering near the 40% certainty rejection threshold.
* **Mean Confidence for Incorrect Predictions:** Shifted moderately from 30.80% to 42.27%.
* **Separation Margin:** The margin between true positives and misclassifications widened from **23.88% to 37.46%**, providing a substantially safer operating margin for NEXORA's 40% certainty threshold.

---

## 7. Conclusions & Strategic Recommendations

### Key Findings
1. **Augmentation was the Missing Lever:** The original model was severely under-fitted due to static training on only 1,122 images. Applying `RandomResizedCrop`, `RandomHorizontalFlip`, and `ColorJitter` expanded effective visual coverage by orders of magnitude, unlocking +12.50% Top-1 accuracy with **zero changes to the convolutional backbone**.
2. **Backbone Saturation Point:** As observed in Epochs 23–30, validation loss stabilized at $\approx 0.628$ and Top-1 accuracy plateaued at 83.09%. A linear probe on a frozen ImageNet backbone cannot extract features that ImageNet weights never learned to differentiate (such as subtle Islamic calligraphic script or specific tile tessellation geometry).
3. **Safety of Hierarchical Routing:** The dramatic reduction in mutual Registan misclassifications directly benefits the Phase 1 hierarchical pipeline, providing cleaner probability vectors for Gemini disambiguation.

### Concrete Recommendations for Round 2

To cross the **88%–90% Top-1 accuracy threshold**, the next round should implement **Differential Backbone Fine-Tuning**:

1. **Unfreeze Top Convolutional Blocks (Blocks 6–8 of EfficientNet-B0):**
   * Keep low-level edge/texture layers (`features.0` through `features.5`) frozen to retain foundational visual representations.
   * Unfreeze high-level semantic layers (`features.6`, `features.7`, `features.8`) to allow the model to learn domain-specific Timurid architectural patterns.
2. **Differential Learning Rates:**
   * Backbone layers (`features.6–8`): $lr = 1.0 \times 10^{-4}$ (conservative, preventing catastrophic forgetting).
   * Classifier head: $lr = 5.0 \times 10^{-4}$.
3. **Preserve Checkpoints:**
   * Keep `backend/models/nexora_landmark_model.pth` and `nexora_landmark_model_exp1.pth` archived.
   * Save Round 2 results to `backend/models/nexora_landmark_model_exp2.pth`.

