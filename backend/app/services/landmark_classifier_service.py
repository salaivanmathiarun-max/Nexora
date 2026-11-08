import os
import io
import base64
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union

import torch
import torchvision.models as models
from torchvision import transforms
from PIL import Image

logger = logging.getLogger("nexora.landmark_classifier")

# Human-readable labels and metadata for the 12 landmark classes
LANDMARK_METADATA = {
    "Al-Buxoriy": {
        "display_name": "Imam al-Bukhari Memorial Complex",
        "uzbek_name": "Imom al-Buxoriy majmuasi",
        "location": "Hartang Village, 25 km from Samarkand",
        "type": "Mausoleum & Memorial Complex",
        "parent": None,
        "hierarchy_level": "monument"
    },
    "Bibikhonim": {
        "display_name": "Bibi-Khanym Mosque",
        "uzbek_name": "Bibixonim masjidi",
        "location": "Bibikhonim Street, Samarkand",
        "type": "Grand Congregational Mosque",
        "parent": None,
        "hierarchy_level": "monument"
    },
    "Gur Emir": {
        "display_name": "Gur-e-Amir Mausoleum",
        "uzbek_name": "Go'ri Amir maqbarasi",
        "location": "Bustonsaroy Street, Samarkand",
        "type": "Timurid Imperial Mausoleum",
        "parent": None,
        "hierarchy_level": "monument"
    },
    "Hazrati Doniyor maqbarasi": {
        "display_name": "Tomb of Saint Daniel (Hazrati Doniyor)",
        "uzbek_name": "Hazrati Doniyor maqbarasi",
        "location": "Siab Riverbank / Afrasiyab, Samarkand",
        "type": "Pilgrimage Shrine & Tomb",
        "parent": None,
        "hierarchy_level": "monument"
    },
    "Imom Motrudiy": {
        "display_name": "Imam al-Maturidi Mausoleum",
        "uzbek_name": "Imom Motrudiy maqbarasi",
        "location": "Old Town, Samarkand",
        "type": "Theological Shrine & Mausoleum",
        "parent": None,
        "hierarchy_level": "monument"
    },
    "Ruhobod": {
        "display_name": "Rukhabad Mausoleum",
        "uzbek_name": "Ruhobod maqbarasi",
        "location": "Adjacent to Gur-e-Amir, Samarkand",
        "type": "Sufi Shrine (14th Century)",
        "parent": None,
        "hierarchy_level": "monument"
    },
    "Sherdor": {
        "display_name": "Sher-Dor Madrasah",
        "uzbek_name": "Sherdor madrasasi",
        "location": "Registan Square, Samarkand",
        "type": "Historic Madrasah (1619–1636)",
        "parent": "Registan Complex",
        "hierarchy_level": "sub_monument"
    },
    "Tillakori madrasasi": {
        "display_name": "Tilya-Kori Madrasah & Mosque",
        "uzbek_name": "Tillakori madrasasi",
        "location": "Registan Square, Samarkand",
        "type": "Gold-Gilded Madrasah (1646–1660)",
        "parent": "Registan Complex",
        "hierarchy_level": "sub_monument"
    },
    "Ulugbek Rasadxonasi": {
        "display_name": "Ulugh Beg Observatory",
        "uzbek_name": "Ulug'bek rasadxonasi",
        "location": "Chupan-Ata Hills, Samarkand",
        "type": "15th-Century Astronomical Observatory",
        "parent": None,
        "hierarchy_level": "monument"
    },
    "Ulugbek madrasasi": {
        "display_name": "Ulugh Beg Madrasah",
        "uzbek_name": "Ulug'bek madrasasi",
        "location": "Registan Square, Samarkand",
        "type": "Timurid University & Madrasah (1417–1420)",
        "parent": "Registan Complex",
        "hierarchy_level": "sub_monument"
    },
    "Xizr majmuasi": {
        "display_name": "Hazrat Khizr Mosque",
        "uzbek_name": "Hazrati Xizr masjidi",
        "location": "Shah-i-Zinda / Afrasiyab border, Samarkand",
        "type": "Historic Hilltop Mosque",
        "parent": None,
        "hierarchy_level": "monument"
    },
    "shokhi zinda": {
        "display_name": "Shah-i-Zinda Necropolis",
        "uzbek_name": "Shohi Zinda majmuasi",
        "location": "Afrasiyab Hillside, Samarkand",
        "type": "Avenue of Royal Mausoleums",
        "parent": None,
        "hierarchy_level": "monument"
    }
}

# Hierarchical parent definition for Registan Complex
REGISTAN_CHILD_CLASSES = ["Sherdor", "Tillakori madrasasi", "Ulugbek madrasasi"]
REGISTAN_PARENT_METADATA = {
    "display_name": "Registan Complex",
    "uzbek_name": "Registon maydoni majmuasi",
    "location": "Registan Square, Samarkand",
    "type": "UNESCO World Heritage Ensemble & Plaza",
    "sub_landmarks": [
        "Sher-Dor Madrasah",
        "Tilya-Kori Madrasah & Mosque",
        "Ulugh Beg Madrasah"
    ]
}

class LandmarkClassifierService:
    """
    Dedicated Landmark Classification Service using the trained EfficientNet-B0 model.
    Loads once on startup and evaluates images against the 12 Samarkand landmark classes.
    Enforces provisional confidence thresholds to avoid falsely identifying unfamiliar images.
    Implements Phase 1 Hierarchical Domain Signaling for Registan without retraining weights.
    """

    # PROVISIONAL THRESHOLDS: Operational heuristic values subject to empirical calibration.
    CONFIDENCE_HIGH = 0.70
    CONFIDENCE_UNCERTAIN = 0.40
    PROVISIONAL_REGISTAN_DOMAIN_THRESHOLD = 0.35  # Cumulative probability across 3 Registan madrasahs
    PROVISIONAL_CHILD_DOMINANCE_RATIO = 1.6       # Ratio of top-1 to top-2 Registan child for single-monument dominance

    def __init__(self):
        self.model = None
        self.class_names: List[str] = []
        self.image_size: int = 224
        self.architecture: str = "EfficientNet-B0"
        self.transform = None
        self._is_loaded = False
        self.model_path = Path(__file__).resolve().parent.parent.parent / "models" / "nexora_landmark_model.pth"

    def load_model(self) -> bool:
        """Loads the PyTorch weights and initializes the model once."""
        if self._is_loaded and self.model is not None:
            return True

        if not self.model_path.exists():
            logger.error(f"Landmark model file not found at {self.model_path}")
            return False

        try:
            logger.info(f"Loading NEXORA landmark model from {self.model_path}...")
            ckpt = torch.load(str(self.model_path), map_location="cpu")

            self.class_names = ckpt.get("class_names", [])
            self.image_size = ckpt.get("image_size", 224)
            self.architecture = ckpt.get("architecture", "EfficientNet-B0")

            # Build EfficientNet-B0 architecture matching checkpoint
            model = models.efficientnet_b0(weights=None)
            model.classifier[1] = torch.nn.Linear(1280, len(self.class_names))
            model.load_state_dict(ckpt["model_state_dict"], strict=True)
            model.eval()
            self.model = model

            # EfficientNet-B0 standard training convention:
            # Resize shorter side to 256, then CenterCrop to image_size (224).
            # This matches the torchvision ImageNet training pipeline and produces
            # significantly higher confidence scores than a plain Resize(224,224).
            self.transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(self.image_size),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])

            self._is_loaded = True
            logger.info(f"Landmark model loaded successfully. Total classes: {len(self.class_names)}")
            return True
        except Exception as e:
            logger.error(f"Failed to load landmark model: {e}")
            self._is_loaded = False
            return False

    def is_ready(self) -> bool:
        return self._is_loaded and self.model is not None

    def _load_image(self, image_input: Union[str, bytes, Image.Image]) -> Image.Image:
        """Helper to parse base64, data URL, file path, bytes, or PIL Image."""
        if isinstance(image_input, Image.Image):
            return image_input.convert("RGB")

        if isinstance(image_input, bytes):
            return Image.open(io.BytesIO(image_input)).convert("RGB")

        if isinstance(image_input, str):
            # Check local file path
            if os.path.exists(image_input):
                return Image.open(image_input).convert("RGB")
            
            # Check data URL or base64 string
            raw_str = image_input
            if "base64," in raw_str:
                raw_str = raw_str.split("base64,", 1)[1]
            try:
                img_bytes = base64.b64decode(raw_str)
                return Image.open(io.BytesIO(img_bytes)).convert("RGB")
            except Exception as e:
                raise ValueError(f"Could not decode image base64 data: {e}")

        raise ValueError("Unsupported image input type.")

    def predict(self, image_input: Union[str, bytes, Image.Image]) -> Dict[str, Any]:
        """
        Runs inference on an image and returns predictions, confidence, and uncertainty diagnostics.
        """
        if not self._is_loaded or self.model is None:
            loaded = self.load_model()
            if not loaded:
                raise RuntimeError("Landmark classification model is not available.")

        try:
            image = self._load_image(image_input)
        except Exception as e:
            raise ValueError(f"Invalid image: {str(e)}")

        tensor = self.transform(image).unsqueeze(0)

        with torch.no_grad():
            logits = self.model(tensor)
            probabilities = torch.softmax(logits, dim=1)[0]

        top_k = min(3, len(self.class_names))
        top_probs, top_indices = torch.topk(probabilities, top_k)

        top1_idx = top_indices[0].item()
        top1_prob = float(top_probs[0].item())
        top1_raw_class = self.class_names[top1_idx]

        # All class probabilities for complete transparency
        all_probs = {
            self.class_names[i]: round(float(probabilities[i].item()), 4)
            for i in range(len(self.class_names))
        }

        top_candidates = [
            {
                "class_name": self.class_names[idx.item()],
                "display_name": LANDMARK_METADATA.get(self.class_names[idx.item()], {}).get("display_name", self.class_names[idx.item()]),
                "confidence": round(float(prob.item()), 4)
            }
            for prob, idx in zip(top_probs, top_indices)
        ]

        meta = LANDMARK_METADATA.get(top1_raw_class, {})

        # Compute Registan regional domain signal (cumulative probability across 3 madrasahs)
        registan_domain_prob = sum(all_probs.get(c, 0.0) for c in REGISTAN_CHILD_CLASSES)
        is_registan_domain = registan_domain_prob >= self.PROVISIONAL_REGISTAN_DOMAIN_THRESHOLD

        # Evaluate if a specific child strongly dominates inside the Registan domain
        registan_child_probs = [
            (c, all_probs.get(c, 0.0)) for c in REGISTAN_CHILD_CLASSES
        ]
        registan_child_probs.sort(key=lambda x: x[1], reverse=True)
        top_registan_child, top_registan_prob = registan_child_probs[0]
        second_registan_child, second_registan_prob = registan_child_probs[1]

        # Scope ambiguity: if Registan domain is detected but top child doesn't strongly dominate
        child_ratio = (top_registan_prob / max(second_registan_prob, 0.01))
        registan_scope_ambiguous = is_registan_domain and (child_ratio < self.PROVISIONAL_CHILD_DOMINANCE_RATIO)

        # Confidence-based uncertainty handling (Provisional Thresholds)
        if top1_prob < self.CONFIDENCE_UNCERTAIN and not is_registan_domain:
            is_recognized = False
            confidence_level = "uncertain"
            predicted_landmark = "Uncertain / Unfamiliar Landmark"
            display_name = "Unfamiliar Landmark"
            message = (
                f"Confidence ({top1_prob:.1%}) is below provisional certainty threshold ({self.CONFIDENCE_UNCERTAIN:.0%}). "
                "The visual features do not strongly match any of the 12 recognized Samarkand monuments."
            )
        elif top1_prob < self.CONFIDENCE_HIGH:
            is_recognized = True
            confidence_level = "medium"
            predicted_landmark = top1_raw_class
            display_name = meta.get("display_name", top1_raw_class)
            message = f"Moderate confidence identification as {display_name} ({top1_prob:.1%})."
        else:
            is_recognized = True
            confidence_level = "high"
            predicted_landmark = top1_raw_class
            display_name = meta.get("display_name", top1_raw_class)
            message = f"High confidence identification as {display_name} ({top1_prob:.1%})."

        # Determine hierarchy metadata
        if top1_raw_class in REGISTAN_CHILD_CLASSES:
            parent_landmark = "Registan Complex"
            hierarchy_level = "sub_monument"
            sub_landmarks = []
        elif is_registan_domain and registan_scope_ambiguous:
            # Regional signal suggests Registan presence; flagged for Gemini visual-scope disambiguation
            parent_landmark = None
            hierarchy_level = "complex"
            sub_landmarks = REGISTAN_PARENT_METADATA["sub_landmarks"]
        else:
            parent_landmark = meta.get("parent")
            hierarchy_level = meta.get("hierarchy_level", "monument")
            sub_landmarks = []

        return {
            "is_recognized": is_recognized,
            "predicted_landmark": predicted_landmark,
            "display_name": display_name,
            "raw_class": top1_raw_class,
            "class_index": top1_idx,
            "confidence_score": round(top1_prob, 4),
            "confidence_level": confidence_level,
            "location": meta.get("location", "Samarkand, Uzbekistan"),
            "landmark_type": meta.get("type", "Historical Monument"),
            "uzbek_name": meta.get("uzbek_name", top1_raw_class),
            "top_candidates": top_candidates,
            "all_probabilities": all_probs,
            "architecture": self.architecture,
            "message": message,
            # Hierarchical & Regional Domain Signaling (Phase 1)
            "is_registan_domain": is_registan_domain,
            "registan_domain_probability": round(registan_domain_prob, 4),
            "registan_scope_ambiguous": registan_scope_ambiguous,
            "hierarchy_level": hierarchy_level,
            "parent_landmark": parent_landmark,
            "sub_landmarks": sub_landmarks
        }

# Global singleton instance
landmark_classifier = LandmarkClassifierService()

