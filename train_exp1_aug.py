"""
Round 1: EXP-1-AUG-BASELINE Training Script
Objective: Test domain-appropriate data augmentation on EfficientNet-B0 with frozen backbone.
All parameters, epochs, validation metrics, and confusion matrix are saved to exp1_metrics.json.
Checkpoint saved to: backend/models/nexora_landmark_model_exp1.pth
Original checkpoint backend/models/nexora_landmark_model.pth is strictly untouched.
"""
import sys
import io
import time
import json
import zipfile
from pathlib import Path
from collections import Counter

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torchvision.models as models
from torchvision import transforms
from PIL import Image
import numpy as np

# Set reproducibility seeds
torch.manual_seed(42)
np.random.seed(42)
torch.set_num_threads(6)

device = torch.device("cpu")
print(f"Executing on device: {device} with {torch.get_num_threads()} CPU threads")

# 1. Load Original Baseline Checkpoint (Read-Only)
base_pth = Path("backend/models/nexora_landmark_model.pth")
assert base_pth.exists(), f"Baseline model not found at {base_pth}"
base_ckpt = torch.load(base_pth, map_location="cpu")
class_names = base_ckpt["class_names"]
class_to_idx = {name: i for i, name in enumerate(class_names)}
num_classes = len(class_names)
print(f"Loaded baseline checkpoint metadata. Classes ({num_classes}): {class_names}")

# 2. Build EfficientNet-B0 with Frozen Backbone
model = models.efficientnet_b0(weights=None)
model.classifier[1] = nn.Linear(1280, num_classes)
model.load_state_dict(base_ckpt["model_state_dict"], strict=True)

# Freeze entire backbone
for param in model.features.parameters():
    param.requires_grad = False
for param in model.avgpool.parameters():
    param.requires_grad = False

# Ensure classifier head is trainable
for param in model.classifier.parameters():
    param.requires_grad = True

trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
frozen_params = sum(p.numel() for p in model.parameters() if not p.requires_grad)
print(f"Model parameters: {trainable_params:,} trainable (classifier head), {frozen_params:,} frozen (backbone)")

# 3. Data Augmentation Pipelines
# Domain-appropriate architectural augmentation
train_transform = transforms.Compose([
    transforms.RandomResizedCrop(224, scale=(0.75, 1.0), ratio=(0.85, 1.15)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Deterministic original baseline validation transform
val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# 4. In-Memory Dataset (Fast CPU iteration)
class LandmarkInMemoryDataset(Dataset):
    def __init__(self, samples, transform):
        self.samples = samples  # List of (raw_bytes, label_idx, filename)
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_bytes, label, fname = self.samples[idx]
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        tensor = self.transform(img)
        return tensor, label, fname

zip_path = Path("C:/Users/Admin/Downloads/archive.zip")
train_samples = []
val_samples = []

print("Reading dataset into memory from archive.zip...")
with zipfile.ZipFile(zip_path, "r") as z:
    for name in z.namelist():
        parts = name.split("/")
        if len(parts) >= 3 and parts[-1].lower().endswith((".jpg", ".jpeg", ".png")):
            split = parts[1]
            cls = parts[2]
            if cls in class_to_idx:
                raw_bytes = z.read(name)
                label = class_to_idx[cls]
                if split == "train":
                    train_samples.append((raw_bytes, label, parts[-1]))
                elif split == "val":
                    val_samples.append((raw_bytes, label, parts[-1]))

print(f"In-memory dataset loaded: {len(train_samples)} train images, {len(val_samples)} val images")

train_dataset = LandmarkInMemoryDataset(train_samples, train_transform)
val_dataset = LandmarkInMemoryDataset(val_samples, val_transform)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=0)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False, num_workers=0)

# 5. Training Setup: AdamW, lr=0.001, CosineAnnealingLR, 30 epochs
optimizer = torch.optim.AdamW(model.classifier.parameters(), lr=0.001, weight_decay=1e-4)
total_epochs = 30
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=total_epochs, eta_min=1e-6)
criterion = nn.CrossEntropyLoss()

# Metrics tracking
history = []
best_val_acc = 0.0
best_val_macro_f1 = 0.0
best_epoch = 0
best_state_dict = None
early_stop_patience = 12
patience_counter = 0

print("\n" + "=" * 70)
print("BEGINNING TRAINING: EXP-1-AUG-BASELINE (30 Epochs, Frozen Backbone)")
print("=" * 70)

start_time = time.time()

for epoch in range(1, total_epochs + 1):
    epoch_start = time.time()
    current_lr = scheduler.get_last_lr()[0]

    # --- Training Phase ---
    model.eval()  # Keep BatchNorm in eval mode since backbone is frozen
    model.classifier.train()  # Only classifier in train mode

    train_loss_total = 0.0
    train_correct = 0
    total_train = 0

    for images, labels, _ in train_loader:
        images, labels = images.to(device), labels.to(device)

        # Frozen backbone forward pass under no_grad for max speed
        with torch.no_grad():
            feat = model.features(images)
            feat = model.avgpool(feat)
            feat = torch.flatten(feat, 1)

        # Forward through trainable classifier head
        optimizer.zero_grad()
        logits = model.classifier(feat)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()

        train_loss_total += loss.item() * images.size(0)
        preds = torch.argmax(logits, dim=1)
        train_correct += (preds == labels).sum().item()
        total_train += images.size(0)

    scheduler.step()

    train_loss = train_loss_total / total_train
    train_acc = (train_correct / total_train) * 100

    # --- Validation Phase ---
    model.eval()
    val_loss_total = 0.0
    val_correct = 0
    total_val = 0
    val_cm = np.zeros((num_classes, num_classes), dtype=int)

    with torch.no_grad():
        for images, labels, _ in val_loader:
            images, labels = images.to(device), labels.to(device)
            feat = model.features(images)
            feat = model.avgpool(feat)
            feat = torch.flatten(feat, 1)
            logits = model.classifier(feat)
            loss = criterion(logits, labels)

            val_loss_total += loss.item() * images.size(0)
            preds = torch.argmax(logits, dim=1)
            val_correct += (preds == labels).sum().item()
            total_val += images.size(0)

            for t, p in zip(labels.cpu().numpy(), preds.cpu().numpy()):
                val_cm[t, p] += 1

    val_loss = val_loss_total / total_val
    val_acc = (val_correct / total_val) * 100

    # Calculate Macro F1
    f1_list = []
    for i in range(num_classes):
        tp = val_cm[i, i]
        fp = val_cm[:, i].sum() - tp
        fn = val_cm[i, :].sum() - tp
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
        f1_list.append(f1)
    val_macro_f1 = np.mean(f1_list) * 100

    epoch_time = time.time() - epoch_start

    # Record history
    entry = {
        "epoch": epoch,
        "lr": round(current_lr, 7),
        "train_loss": round(train_loss, 4),
        "train_acc": round(train_acc, 2),
        "val_loss": round(val_loss, 4),
        "val_acc": round(val_acc, 2),
        "val_macro_f1": round(val_macro_f1, 2),
        "epoch_time_s": round(epoch_time, 1)
    }
    history.append(entry)

    # Checkpoint selection: track higher val_acc; break ties with macro F1 and lower val_loss
    is_best = False
    if (val_acc > best_val_acc) or (val_acc == best_val_acc and val_macro_f1 > best_val_macro_f1):
        best_val_acc = val_acc
        best_val_macro_f1 = val_macro_f1
        best_epoch = epoch
        best_state_dict = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        is_best = True
        patience_counter = 0
    else:
        patience_counter += 1

    best_marker = " * BEST" if is_best else ""
    print(
        f"Epoch [{epoch:2d}/30] | "
        f"Train Loss: {train_loss:.4f}, Acc: {train_acc:5.2f}% | "
        f"Val Loss: {val_loss:.4f}, Acc: {val_acc:5.2f}%, Macro-F1: {val_macro_f1:5.2f}% | "
        f"LR: {current_lr:.6f} ({epoch_time:.1f}s){best_marker}",
        flush=True
    )

    if patience_counter >= early_stop_patience:
        print(f"\nEarly stopping triggered after {patience_counter} epochs without improvement in validation performance.")
        break

total_training_time = time.time() - start_time
print(f"\nTraining completed in {total_training_time/60:.2f} minutes.")
print(f"Best Checkpoint: Epoch {best_epoch} with Val Acc: {best_val_acc:.2f}%, Val Macro F1: {best_val_macro_f1:.2f}%")

# 6. Save the EXP-1 Checkpoint Separately
out_ckpt_path = Path("backend/models/nexora_landmark_model_exp1.pth")
torch.save({
    "model_state_dict": best_state_dict,
    "class_names": class_names,
    "architecture": "EfficientNet-B0",
    "image_size": 224,
    "experiment": "EXP-1-AUG-BASELINE",
    "best_epoch": best_epoch,
    "best_val_acc": best_val_acc,
    "best_val_macro_f1": best_val_macro_f1,
    "total_epochs": len(history)
}, out_ckpt_path)
print(f"Saved best model checkpoint separately to: {out_ckpt_path} (size: {out_ckpt_path.stat().st_size:,} bytes)")

# 7. Comprehensive Diagnostic on Best Checkpoint
print("\n" + "=" * 70)
print("EVALUATING BEST EXP-1 CHECKPOINT (Full Diagnostic)")
print("=" * 70)

eval_model = models.efficientnet_b0(weights=None)
eval_model.classifier[1] = nn.Linear(1280, num_classes)
eval_model.load_state_dict(best_state_dict)
eval_model.eval()

cm = np.zeros((num_classes, num_classes), dtype=int)
top1_correct = 0
top3_correct = 0
conf_correct = []
conf_incorrect = []
all_losses = []

with torch.no_grad():
    for images, labels, _ in val_loader:
        images, labels = images.to(device), labels.to(device)
        logits = eval_model(images)
        loss = criterion(logits, labels)
        all_losses.extend([loss.item()] * images.size(0))

        probs = torch.softmax(logits, dim=1)
        top_probs, top_indices = torch.topk(probs, 3, dim=1)

        for i in range(images.size(0)):
            true_label = labels[i].item()
            pred_top1 = top_indices[i, 0].item()
            pred_conf = top_probs[i, 0].item()
            top3_labels = top_indices[i].tolist()

            cm[true_label, pred_top1] += 1
            if pred_top1 == true_label:
                top1_correct += 1
                conf_correct.append(pred_conf)
            else:
                conf_incorrect.append(pred_conf)

            if true_label in top3_labels:
                top3_correct += 1

total_eval = len(val_samples)
final_val_loss = np.mean(all_losses)
final_top1_acc = (top1_correct / total_eval) * 100
final_top3_acc = (top3_correct / total_eval) * 100

class_metrics = []
for i in range(num_classes):
    name = class_names[i]
    tp = cm[i, i]
    fp = cm[:, i].sum() - tp
    fn = cm[i, :].sum() - tp
    prec = (tp / (tp + fp) * 100) if (tp + fp) > 0 else 0.0
    rec = (tp / (tp + fn) * 100) if (tp + fn) > 0 else 0.0
    f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
    class_metrics.append({
        "class": name,
        "support": int(cm[i, :].sum()),
        "tp": int(tp),
        "fp": int(fp),
        "fn": int(fn),
        "precision": round(prec, 2),
        "recall": round(rec, 2),
        "f1_score": round(f1, 2)
    })

final_macro_prec = np.mean([m["precision"] for m in class_metrics])
final_macro_rec = np.mean([m["recall"] for m in class_metrics])
final_macro_f1 = np.mean([m["f1_score"] for m in class_metrics])
final_weighted_f1 = sum(m["f1_score"] * m["support"] for m in class_metrics) / total_eval

print(f"Top-1 Accuracy:  {final_top1_acc:.2f}% ({top1_correct}/{total_eval})")
print(f"Top-3 Accuracy:  {final_top3_acc:.2f}% ({top3_correct}/{total_eval})")
print(f"Macro Precision: {final_macro_prec:.2f}%")
print(f"Macro Recall:    {final_macro_rec:.2f}%")
print(f"Macro F1-Score:  {final_macro_f1:.2f}%")
print(f"Weighted F1:     {final_weighted_f1:.2f}%")
print(f"Mean Confidence (Correct):   {np.mean(conf_correct)*100:.2f}%")
print(f"Mean Confidence (Incorrect): {np.mean(conf_incorrect)*100:.2f}%")

# Save complete metrics report to JSON for documentation
metrics_export = {
    "experiment": "EXP-1-AUG-BASELINE",
    "best_epoch": best_epoch,
    "total_training_time_s": round(total_training_time, 1),
    "best_metrics": {
        "val_loss": round(final_val_loss, 4),
        "top1_acc": round(final_top1_acc, 2),
        "top3_acc": round(final_top3_acc, 2),
        "macro_precision": round(final_macro_prec, 2),
        "macro_recall": round(final_macro_rec, 2),
        "macro_f1": round(final_macro_f1, 2),
        "weighted_f1": round(final_weighted_f1, 2),
        "mean_conf_correct": round(float(np.mean(conf_correct)), 4),
        "mean_conf_incorrect": round(float(np.mean(conf_incorrect)), 4)
    },
    "confusion_matrix": cm.tolist(),
    "class_names": class_names,
    "per_class": class_metrics,
    "history": history
}

with open("exp1_metrics.json", "w", encoding="utf-8") as f:
    json.dump(metrics_export, f, indent=2)

print("\nMetrics exported to exp1_metrics.json.")

