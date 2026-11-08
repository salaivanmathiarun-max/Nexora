"""
Full Diagnostic Script for NEXORA Landmark Model (EfficientNet-B0)
Computes:
1. Exact baseline validation evaluation (Resize(224, 224) + ImageNet Norm)
2. 12x12 Confusion Matrix
3. Per-class metrics: Support, TP, FP, FN, Precision, Recall, F1
4. Most confused class pairs (frequency and percentages)
5. Correlation between training set size and recall/F1
6. Train vs Val duplicate and near-duplicate analysis (MD5 + dHash)
7. Backbone weight variance analysis (frozen vs fine-tuned)
"""
import sys
import io
import zipfile
import hashlib
from collections import defaultdict, Counter
from pathlib import Path
import torch
import torchvision.models as models
from torchvision import transforms
from PIL import Image
import numpy as np

# 1. Load checkpoint and model
pth_path = Path("backend/models/nexora_landmark_model.pth")
ckpt = torch.load(pth_path, map_location="cpu")
class_names = ckpt["class_names"]
class_to_idx = {name: i for i, name in enumerate(class_names)}
num_classes = len(class_names)

model = models.efficientnet_b0(weights=None)
model.classifier[1] = torch.nn.Linear(1280, num_classes)
model.load_state_dict(ckpt["model_state_dict"])
model.eval()

# Original preprocessing: Resize(224, 224) with ImageNet normalization
val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

zip_path = Path("C:/Users/Admin/Downloads/archive.zip")
assert zip_path.exists(), "Dataset archive.zip not found"

val_samples = []
train_counts = Counter()
val_counts = Counter()
train_hashes = {}
val_hashes = {}

# Compute dHash (difference hash) for near-duplicate detection
def dhash(image, hash_size=8):
    # Resize to (hash_size + 1, hash_size), grayscale
    img_gray = image.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    pixels = np.array(img_gray)
    # Compare adjacent pixels
    diff = pixels[:, 1:] > pixels[:, :-1]
    # Convert bool array to integer bitstring
    return sum([2 ** i for i, v in enumerate(diff.flatten()) if v])

train_dhashes = {}
val_dhashes = {}

with zipfile.ZipFile(zip_path, "r") as z:
    for name in z.namelist():
        parts = name.split("/")
        if len(parts) >= 3 and parts[-1].lower().endswith((".jpg", ".jpeg", ".png")):
            split = parts[1]
            cls = parts[2]
            img_bytes = z.read(name)
            md5_h = hashlib.md5(img_bytes).hexdigest()
            
            if split == "train":
                train_counts[cls] += 1
                train_hashes[md5_h] = (cls, parts[-1])
                try:
                    pil_img = Image.open(io.BytesIO(img_bytes))
                    train_dhashes[parts[-1]] = (cls, dhash(pil_img))
                except Exception:
                    pass
            elif split == "val":
                val_counts[cls] += 1
                val_hashes[md5_h] = (cls, parts[-1])
                try:
                    pil_img = Image.open(io.BytesIO(img_bytes))
                    dh = dhash(pil_img)
                    val_dhashes[parts[-1]] = (cls, dh)
                    val_samples.append((cls, class_to_idx[cls], img_bytes, parts[-1]))
                except Exception:
                    pass

print(f"Total train images: {sum(train_counts.values())}")
print(f"Total val images: {sum(val_counts.values())}")

# 2. Check exact and near-duplicates between train and val
exact_leakage = set(train_hashes.keys()) & set(val_hashes.keys())
print(f"Exact MD5 duplicate leakage (train <-> val): {len(exact_leakage)}")

# Hamming distance for near-duplicates (threshold <= 4 bits difference on 64-bit dhash)
near_duplicates = []
for val_fname, (val_cls, v_dh) in val_dhashes.items():
    for train_fname, (train_cls, t_dh) in train_dhashes.items():
        # XOR to find bit differences
        diff_bits = bin(v_dh ^ t_dh).count("1")
        if diff_bits <= 4:
            near_duplicates.append((val_cls, val_fname, train_cls, train_fname, diff_bits))

print(f"Near-duplicates found (dHash <= 4 bits diff): {len(near_duplicates)}")
for item in near_duplicates[:10]:
    print(f"  Val [{item[0]}: {item[1]}] <-> Train [{item[2]}: {item[3]}] (Hamming dist: {item[4]})")

# 3. Model Inference on Validation Split
cm = np.zeros((num_classes, num_classes), dtype=int)
conf_correct = []
conf_incorrect = []
all_losses = []
criterion = torch.nn.CrossEntropyLoss()

top1_correct = 0
top3_correct = 0

sample_diagnostics = []

with torch.no_grad():
    for true_cls, true_idx, b, fname in val_samples:
        img = Image.open(io.BytesIO(b)).convert("RGB")
        tensor = val_transform(img).unsqueeze(0)
        logits = model(tensor)
        loss = criterion(logits, torch.tensor([true_idx]))
        all_losses.append(loss.item())

        probs = torch.softmax(logits, dim=1)[0]
        top_probs, top_indices = torch.topk(probs, 3)
        pred_top1 = top_indices[0].item()
        pred_conf = top_probs[0].item()
        top3_list = top_indices.tolist()

        cm[true_idx, pred_top1] += 1
        if pred_top1 == true_idx:
            top1_correct += 1
            conf_correct.append(pred_conf)
        else:
            conf_incorrect.append(pred_conf)
            sample_diagnostics.append({
                "file": fname,
                "true_class": true_cls,
                "pred_class": class_names[pred_top1],
                "confidence": round(pred_conf, 4),
                "true_rank": top3_list.index(true_idx) + 1 if true_idx in top3_list else ">3",
                "true_prob": round(probs[true_idx].item(), 4)
            })

        if true_idx in top3_list:
            top3_correct += 1

total_val = len(val_samples)
val_loss = np.mean(all_losses)
top1_acc = top1_correct / total_val * 100
top3_acc = top3_correct / total_val * 100

print(f"\n--- OVERALL VALIDATION METRICS ---")
print(f"Validation Loss:     {val_loss:.4f}")
print(f"Top-1 Accuracy:      {top1_acc:.2f}% ({top1_correct}/{total_val})")
print(f"Top-3 Accuracy:      {top3_acc:.2f}% ({top3_correct}/{total_val})")
print(f"Mean Confidence (Correct):   {np.mean(conf_correct)*100:.2f}% (std: {np.std(conf_correct)*100:.2f}%)")
print(f"Mean Confidence (Incorrect): {np.mean(conf_incorrect)*100:.2f}% (std: {np.std(conf_incorrect)*100:.2f}%)")

# 4. Per-Class Metrics
print(f"\n--- PER-CLASS PERFORMANCE TABLE ---")
header = f"{'Class':28s} {'Train':>5s} {'Val':>4s} {'TP':>3s} {'FP':>3s} {'FN':>3s} {'Prec(%)':>8s} {'Rec(%)':>8s} {'F1(%)':>8s}"
print(header)
print("-" * len(header))

class_metrics = []
for i in range(num_classes):
    name = class_names[i]
    tp = cm[i, i]
    fp = cm[:, i].sum() - tp
    fn = cm[i, :].sum() - tp
    val_n = cm[i, :].sum()
    train_n = train_counts[name]
    
    prec = (tp / (tp + fp) * 100) if (tp + fp) > 0 else 0.0
    rec = (tp / (tp + fn) * 100) if (tp + fn) > 0 else 0.0
    f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
    
    class_metrics.append({
        "name": name,
        "train_n": train_n,
        "val_n": val_n,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "prec": prec,
        "rec": rec,
        "f1": f1
    })
    print(f"{name:28s} {train_n:5d} {val_n:4d} {tp:3d} {fp:3d} {fn:3d} {prec:8.2f} {rec:8.2f} {f1:8.2f}")

macro_prec = np.mean([m["prec"] for m in class_metrics])
macro_rec = np.mean([m["rec"] for m in class_metrics])
macro_f1 = np.mean([m["f1"] for m in class_metrics])
weighted_f1 = sum([m["f1"] * m["val_n"] for m in class_metrics]) / total_val

print("-" * len(header))
print(f"{'MACRO AVERAGE':28s} {sum(train_counts.values()):5d} {total_val:4d} {top1_correct:3d} {sum(m['fp'] for m in class_metrics):3d} {sum(m['fn'] for m in class_metrics):3d} {macro_prec:8.2f} {macro_rec:8.2f} {macro_f1:8.2f}")
print(f"Weighted F1-Score: {weighted_f1:.2f}%")

# 5. Confusion Matrix in Tabular Text
print(f"\n--- 12x12 CONFUSION MATRIX (Rows=Ground Truth, Columns=Predicted) ---")
idx_hdr = "    " + " ".join([f"{i:>4d}" for i in range(num_classes)])
print(idx_hdr)
for i in range(num_classes):
    row_str = " ".join([f"{cm[i, j]:4d}" for j in range(num_classes)])
    print(f"[{i:2d}] {row_str}  | {class_names[i]}")

# 6. Most Frequently Confused Pairs
print(f"\n--- MOST FREQUENTLY CONFUSED PAIRS (Off-Diagonal > 0) ---")
confusions = []
for i in range(num_classes):
    for j in range(num_classes):
        if i != j and cm[i, j] > 0:
            confusions.append((class_names[i], class_names[j], cm[i, j], cm[i, j] / cm[i, :].sum() * 100))

confusions.sort(key=lambda x: x[2], reverse=True)
for true_c, pred_c, count, pct in confusions:
    print(f"  {true_c:26s} -> Misclassified as {pred_c:26s}: {count} image(s) ({pct:.1f}% of class)")

# 7. Correlation between Train Size and Performance
train_sizes = [m["train_n"] for m in class_metrics]
recalls = [m["rec"] for m in class_metrics]
f1s = [m["f1"] for m in class_metrics]
corr_rec = np.corrcoef(train_sizes, recalls)[0, 1]
corr_f1 = np.corrcoef(train_sizes, f1s)[0, 1]
print(f"\nPearson Correlation (Train Sample Count vs Recall):   r = {corr_rec:.3f}")
print(f"Pearson Correlation (Train Sample Count vs F1-Score): r = {corr_f1:.3f}")

# 8. Backbone Training / Freezing Analysis
sd = ckpt["model_state_dict"]
backbone_weights = [v for k, v in sd.items() if "features" in k and "weight" in k and v.dim() > 1]
classifier_weight = sd["classifier.1.weight"]
print(f"\n--- BACKBONE VS CLASSIFIER WEIGHT STATS ---")
print(f"Classifier Head weight norm: {classifier_weight.norm().item():.4f}, std: {classifier_weight.std().item():.5f}")
for i, name in enumerate(["features.0.0.weight", "features.1.0.block.0.0.weight", "features.4.0.block.0.0.weight", "features.7.0.block.0.0.weight", "features.8.0.weight"]):
    if name in sd:
        w = sd[name]
        print(f"  {name:32s}: norm={w.norm().item():.4f}, mean={w.mean().item():.5f}, std={w.std().item():.5f}")

