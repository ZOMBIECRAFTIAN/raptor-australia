"""
Australian Raptor CNN — Web Application
Backend Flask con inferencia del modelo entrenado
y módulo de vocabulario AUSLAN.
"""

import os
import json
import uuid
from flask import (Flask, render_template, request,
                   jsonify, send_from_directory, Response,
                   redirect, url_for, make_response)
import io

# Detailed species profiles (Merlin-style content)
from species_data import SPECIES_DETAILS
from species_data_i18n import get_species_data, SPECIES_I18N

# Internationalisation: 10-language UI + species data
from i18n import (load_translations, t, get_locale,
                  get_languages, COOKIE_NAME, LANGUAGES)
from yolo_detector import YoloBirdDetector, YoloUnavailable

from PIL import Image
from pathlib import Path
import numpy as np
from datetime import datetime
import csv

LIGHTWEIGHT_MODE = os.environ.get("RAPTOR_LIGHTWEIGHT", "").lower() in {
    "1", "true", "yes"
}

try:
    import torch
    import torch.nn as nn
    import torchvision.transforms as transforms
    from torchvision import models
except Exception as exc:  # pragma: no cover - exercised in lightweight CI
    if not LIGHTWEIGHT_MODE:
        raise
    torch = None
    nn = None
    transforms = None
    models = None
    TORCH_IMPORT_ERROR = exc
else:
    TORCH_IMPORT_ERROR = None

# ─── Configuración ────────────────────────────────────
BASE_DIR     = Path(__file__).parent
PROJECT_ROOT = BASE_DIR.parent
MODEL_PATH   = PROJECT_ROOT / "models" / "best_model.pth"
UPLOAD_DIR   = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max

# Load all 10 translation files at startup, expose helpers to Jinja.
load_translations()
app.jinja_env.globals.update(
    t=t,
    get_locale=get_locale,
    get_languages=get_languages,
    LANGUAGES=LANGUAGES,
)

# ─── Dispositivo ──────────────────────────────────────
device = (torch.device("cuda" if torch.cuda.is_available() else "cpu")
          if torch is not None else None)

# ─── Información de especies ──────────────────────────
SPECIES_INFO = {
    "aquila_audax": {
        "common_name":     "Wedge-tailed Eagle",
        "scientific_name": "Aquila audax",
        "class_idx":       0,

        "family":          "Accipitridae",


        "code":            "WTE",
        "epbc_status":     "Not listed (A. a. fleayi: Endangered)",
        "habitat":         "Open woodland, scrubland, grassland",
        "wingspan_cm":     "182-232 cm",
        "length_cm":       "85-105 cm",
        "diagnostic":      "Diamond/wedge-shaped tail, "
                           "arched wings in soaring flight",
        "auslan_sign":     "Both hands in inverted V, "
                           "extend downward with wide amplitude",
        "auslan_video":    "aquila_audax.svg",
        "color":           "#2C3E50",
    },
    "falco_peregrinus": {
        "common_name":     "Peregrine Falcon",
        "scientific_name": "Falco peregrinus macropus",
        "class_idx":       5,

        "family":          "Falconidae",


        "code":            "PRF",
        "epbc_status":     "Not listed",
        "habitat":         "Cliffs, urban areas, coastlines",
        "wingspan_cm":     "74-120 cm",
        "length_cm":       "34-58 cm",
        "diagnostic":      "Long pointed wings, black malar "
                           "stripe, fast vertical stoop",
        "auslan_sign":     "Dominant hand index finger, "
                           "rapid vertical dive downward",
        "auslan_video":    "falco_peregrinus.svg",
        "color":           "#8E44AD",
    },
    "circus_assimilis": {
        "common_name":     "Spotted Harrier",
        "scientific_name": "Circus assimilis",
        "class_idx":       1,

        "family":          "Accipitridae",


        "code":            "SPH",
        "epbc_status":     "Vulnerable (NSW)",
        "habitat":         "Grassland, scrubland, open farmland",
        "wingspan_cm":     "110-148 cm",
        "length_cm":       "50-61 cm",
        "diagnostic":      "Facial disc, shallow V dihedral, "
                           "low sweeping flight",
        "auslan_sign":     "Both flat hands, lateral oscillating "
                           "glide at low height",
        "auslan_video":    "circus_assimilis.svg",
        "color":           "#27AE60",
    },
    "tachyspiza_fasciata": {
        "common_name":     "Brown Goshawk",
        "scientific_name": "Tachyspiza fasciata",
        "class_idx":       12,

        "family":          "Accipitridae",


        "code":            "BRG",
        "epbc_status":     "Not listed",
        "habitat":         "Dense forest, woodland",
        "wingspan_cm":     "75-95 cm",
        "length_cm":       "40-55 cm",
        "diagnostic":      "Short rounded wings, long banded "
                           "tail, yellow iris",
        "auslan_sign":     "Curved hand, rapid zigzag movement "
                           "between trees",
        "auslan_video":    "tachyspiza_fasciata.svg",
        "color":           "#D35400",
    },
    "falco_cenchroides": {
        "common_name":     "Nankeen Kestrel",
        "scientific_name": "Falco cenchroides",
        "class_idx":       4,

        "family":          "Falconidae",


        "code":            "NKK",
        "epbc_status":     "Not listed",
        "habitat":         "Open habitats, grassland, farmland",
        "wingspan_cm":     "66-78 cm",
        "length_cm":       "28-35 cm",
        "diagnostic":      "Stationary hovering over open ground, "
                           "rufous coloration, fan tail",
        "auslan_sign":     "Open hand, stationary vibration "
                           "(hovering motion)",
        "auslan_video":    "falco_cenchroides.svg",
        "color":           "#E67E22",
    },
    "elanus_axillaris": {
        "common_name":     "Black-shouldered Kite",
        "scientific_name": "Elanus axillaris",
        "class_idx":       2,

        "family":          "Accipitridae",


        "code":            "BSK",
        "epbc_status":     "Not listed",
        "habitat":         "Grassland, agricultural areas, "
                           "wetland edges",
        "wingspan_cm":     "80-94 cm",
        "length_cm":       "35-38 cm",
        "diagnostic":      "Black shoulder patches, white-grey "
                           "plumage, red iris, hovering",
        "auslan_sign":     "Both hands in H, hover then "
                           "short descent",
        "auslan_video":    "elanus_axillaris.svg",
        "color":           "#2980B9",
    },
    "lophoictinia_isura": {
        "common_name":     "Square-tailed Kite",
        "scientific_name": "Lophoictinia isura",
        "class_idx":       10,

        "family":          "Accipitridae",


        "code":            "SQK",
        "epbc_status":     "Vulnerable (EPBC Act)",
        "habitat":         "Mature eucalyptus forest, woodland",
        "wingspan_cm":     "120-145 cm",
        "length_cm":       "50-56 cm",
        "diagnostic":      "Long square tail, slow soaring "
                           "over forest canopy",
        "auslan_sign":     "Flat hand, slow glide with "
                           "square tail demarcated",
        "auslan_video":    "lophoictinia_isura.svg",
        "color":           "#16A085",
    },
    "hieraaetus_morphnoides": {
        "common_name":     "Little Eagle",
        "scientific_name": "Hieraaetus morphnoides",
        "class_idx":       9,

        "family":          "Accipitridae",


        "code":            "LIE",
        "epbc_status":     "Not listed",
        "habitat":         "Open woodland, forest edges",
        "wingspan_cm":     "85-110 cm",
        "length_cm":       "45-55 cm",
        "diagnostic":      "Small size for eagle, broad "
                           "rounded wings, short tail, "
                           "small crest",
        "auslan_sign":     "Compact hand, small active "
                           "movement (small size + broad wings)",
        "auslan_video":    "hieraaetus_morphnoides.svg",
        "color":           "#C0392B",
    },
    "falco_berigora": {
        "common_name":     "Brown Falcon",
        "scientific_name":     "Falco berigora",
        "class_idx":       3,

        "family":          "Falconidae",


        "code":            "BRF",
        "epbc_status":     "Not listed",
        "habitat":     "Open habitats, agricultural land, semi-arid woodland",
        "wingspan_cm":     "88-110 cm",
        "length_cm":     "41-51 cm",
        "diagnostic":     "Variable plumage (light to dark morphs), broad rounded wings, slow flapping flight",
        "auslan_sign":     "Open hand, slow broad flap with occasional glide",
        "auslan_video":     "falco_berigora.svg",
        "color":     "#7E5109",
    },
    "haliaeetus_leucogaster": {
        "common_name":     "White-bellied Sea-Eagle",
        "scientific_name":     "Haliaeetus leucogaster",
        "class_idx":       6,

        "family":          "Accipitridae",


        "code":            "WBE",
        "epbc_status":     "Vulnerable (NSW, VIC, SA, TAS)",
        "habitat":     "Coastal cliffs, estuaries, large inland lakes, rivers",
        "wingspan_cm":     "178-220 cm",
        "length_cm":     "75-85 cm",
        "diagnostic":     "Adult with white head/underparts and grey back, dark flight feathers, short wedge-shaped tail",
        "auslan_sign":     "Both hands flat horizontal, slow gliding extension outward",
        "auslan_video":     "haliaeetus_leucogaster.svg",
        "color":     "#154360",
    },
    "haliastur_indus": {
        "common_name":     "Brahminy Kite",
        "scientific_name":     "Haliastur indus",
        "class_idx":       7,

        "family":          "Accipitridae",


        "code":            "BHK",
        "epbc_status":     "Not listed",
        "habitat":     "Coastal mangroves, estuaries, tropical wetlands",
        "wingspan_cm":     "110-125 cm",
        "length_cm":     "44-52 cm",
        "diagnostic":     "Striking white head and chest contrasting with chestnut body, soars on flat or slightly arched wings",
        "auslan_sign":     "Dominant hand, smooth horizontal glide with subtle banking",
        "auslan_video":     "haliastur_indus.svg",
        "color":     "#B7660D",
    },
    "haliastur_sphenurus": {
        "common_name":     "Whistling Kite",
        "scientific_name":     "Haliastur sphenurus",
        "class_idx":       8,

        "family":          "Accipitridae",


        "code":            "WHK",
        "epbc_status":     "Not listed",
        "habitat":     "Open country, wetlands, woodland near water; widespread",
        "wingspan_cm":     "120-146 cm",
        "length_cm":     "50-60 cm",
        "diagnostic":     "Pale buff head, long rounded tail with diagnostic 'M' wing pattern from below, frequent whistling call",
        "auslan_sign":     "Flat hand horizontal, smooth gliding sweep with audible-like accent",
        "auslan_video":     "haliastur_sphenurus.svg",
        "color":     "#B7950B",
    },
    "milvus_migrans": {
        "common_name":     "Black Kite",
        "scientific_name":     "Milvus migrans",
        "class_idx":       11,

        "family":          "Accipitridae",


        "code":            "BLK",
        "epbc_status":     "Not listed",
        "habitat":     "Open country, edges of bushfires, rubbish tips, agricultural land",
        "wingspan_cm":     "140-160 cm",
        "length_cm":     "50-60 cm",
        "diagnostic":     "Distinctively forked tail, dark plumage, often seen in flocks over fires",
        "auslan_sign":     "Dominant hand with V-fingers for forked tail, soaring motion",
        "auslan_video":     "milvus_migrans.svg",
        "color":     "#6C3483",
    },
    "tachyspiza_novaehollandiae": {
        "common_name":     "Grey Goshawk",
        "scientific_name":     "Tachyspiza novaehollandiae",
        "class_idx":       13,

        "family":          "Accipitridae",


        "code":            "GRG",
        "epbc_status":     "Vulnerable (TAS, VIC)",
        "habitat":     "Rainforest, eucalyptus forest, riparian woodland",
        "wingspan_cm":     "75-105 cm",
        "length_cm":     "40-55 cm",
        "diagnostic":     "Two morphs: pure white form (unique to Australia) and grey form, red iris, yellow legs",
        "auslan_sign":     "Curved hand, swift turning movement through dense canopy",
        "auslan_video":     "tachyspiza_novaehollandiae.svg",
        "color":     "#7B7D7D",
    },
}

# Orden de clases v1.5 según ImageFolder (alfabético).
# Las especies Tier-2 permanecen en SPECIES_INFO como roadmap, pero
# no se exponen en inferencia hasta que exista un checkpoint v2.0.
CLASS_ORDER = [
    "aquila_audax",
    "circus_assimilis",
    "elanus_axillaris",
    "falco_cenchroides",
    "falco_peregrinus",
    "hieraaetus_morphnoides",
    "lophoictinia_isura",
    "tachyspiza_fasciata",
]
NUM_CLASSES = len(CLASS_ORDER)
MODEL_VERSION = "v1.5"
MODEL_F1_MACRO = "0.8482"
CALIBRATION_TEMPERATURE = 0.6934510469436646
LOW_CONFIDENCE_THRESHOLD = 50.0
AMBIGUOUS_TOP2_MARGIN = 10.0
YOLO_CROP_POLICY = os.environ.get("RAPTOR_YOLO_CROP_POLICY",
                                  "adaptive").lower()
YOLO_CROP_CONFIDENCE_GAIN = 10.0
ROADMAP_CLASS_ORDER = [
    "falco_berigora",
    "haliaeetus_leucogaster",
    "haliastur_indus",
    "haliastur_sphenurus",
    "milvus_migrans",
    "tachyspiza_novaehollandiae",
]

for _idx, _key in enumerate(CLASS_ORDER):
    SPECIES_INFO[_key]["class_idx"] = _idx


def _active_species_info() -> dict:
    """Species exposed by the currently validated checkpoint."""
    return {key: SPECIES_INFO[key] for key in CLASS_ORDER}

# ─── Modelo ───────────────────────────────────────────
if nn is not None:
    class AustralianRaptorCNN(nn.Module):
        def __init__(self, num_classes=NUM_CLASSES, dropout_rate=0.4):
            super(AustralianRaptorCNN, self).__init__()
            self.backbone = models.efficientnet_b4(weights=None)
            num_features  = self.backbone.classifier[1].in_features
            self.backbone.classifier = nn.Sequential(
                nn.Dropout(p=dropout_rate, inplace=True),
                nn.Linear(num_features, 512),
                nn.ReLU(),
                nn.Dropout(p=dropout_rate / 2),
                nn.Linear(512, num_classes)
            )

        def forward(self, x):
            return self.backbone(x)
else:
    class AustralianRaptorCNN:  # pragma: no cover - lightweight CI only
        def __init__(self, *_, **__):
            raise RuntimeError(
                "PyTorch is not available. Set RAPTOR_LIGHTWEIGHT=0 "
                "and install requirements.txt for model inference."
            )


def load_model():
    """Carga el modelo entrenado una sola vez al iniciar."""
    if torch is None:
        raise RuntimeError(f"PyTorch import failed: {TORCH_IMPORT_ERROR}")
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model checkpoint not found: {MODEL_PATH}")

    model = AustralianRaptorCNN(num_classes=NUM_CLASSES).to(device)
    checkpoint = torch.load(MODEL_PATH, map_location=device,
                            weights_only=True)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    ckpt_order = checkpoint.get("class_order")
    if ckpt_order and list(ckpt_order) != CLASS_ORDER:
        raise ValueError(
            "Checkpoint class_order does not match gui.CLASS_ORDER: "
            f"{ckpt_order} != {CLASS_ORDER}"
        )
    print(f"Modelo cargado — Val F1: {checkpoint['val_f1']:.4f}")
    return model


# Cargar modelo al iniciar la app
if LIGHTWEIGHT_MODE:
    raptor_model = None
else:
    raptor_model = load_model()

# ─── Transformación de inferencia ─────────────────────
inference_transform = (transforms.Compose([
    transforms.Resize((420, 420)),
    transforms.CenterCrop(380),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
]) if transforms is not None else None)


def _dummy_prediction() -> dict:
    """Deterministic lightweight prediction used by CI route tests."""
    key = CLASS_ORDER[0]
    info = _localized_species_info()[key]
    top3 = []
    for i, sp_key in enumerate(CLASS_ORDER[:3]):
        sp = _localized_species_info()[sp_key]
        top3.append({
            "species_key": sp_key,
            "common_name": sp["common_name"],
            "scientific_name": sp["scientific_name"],
            "confidence": round(91.0 - i * 12.5, 1),
            "color": sp["color"],
        })
    return {
        "species_key":     key,
        "common_name":     info["common_name"],
        "scientific_name": info["scientific_name"],
        "confidence":      91.0,
        "epbc_status":     info["epbc_status"],
        "habitat":         info["habitat"],
        "wingspan_cm":     info["wingspan_cm"],
        "length_cm":       info["length_cm"],
        "diagnostic":      info["diagnostic"],
        "auslan_sign":     info["auslan_sign"],
        "auslan_video":    info["auslan_video"],
        "color":           info["color"],
        "top3":            top3,
        "detector":        "lightweight_dummy",
        "bbox":            None,
        "bbox_score":      None,
        "calibration_temperature": CALIBRATION_TEMPERATURE,
        "decision_status": "identified",
        "warnings":        [],
        "top2_margin":     12.5,
        "inference_mode":  "lightweight_dummy",
        "yolo_crop_policy": YOLO_CROP_POLICY,
        "yolo_crop_available": False,
    }


def _expand_bbox(bbox: list[int], width: int, height: int,
                 margin_frac: float = 0.05) -> list[int]:
    """Expand a bbox by a small context margin and clamp to image bounds."""
    x0, y0, x1, y1 = bbox
    margin = int(round(margin_frac * min(width, height)))
    return [
        max(0, x0 - margin),
        max(0, y0 - margin),
        min(width, x1 + margin),
        min(height, y1 + margin),
    ]


def _select_yolo_crop(img: Image.Image) -> tuple[Image.Image, dict | None]:
    """
    Use YOLO to select the strongest bird crop for single-image inference.

    If YOLO is unavailable or no bird is detected, return the original image
    and None. This keeps inference usable while making the detector/cropper
    claim true whenever YOLO weights are available.
    """
    try:
        yolo = _lazy_yolo_detector()
    except Exception:
        yolo = None
    if yolo is None:
        return img, None

    boxes = yolo.detect(img)
    if not boxes:
        return img, None

    best = max(boxes, key=lambda box: box.confidence)
    width, height = img.size
    crop_box = _expand_bbox(best.bbox, width, height)
    crop = img.crop(tuple(crop_box))
    if min(crop.size) < 32:
        return img, None

    return crop, {
        "detector": best.source,
        "bbox": crop_box,
        "bbox_score": best.confidence,
    }


def _calibrated_probs(logits):
    """Apply post-hoc temperature scaling before softmax."""
    return torch.softmax(logits / CALIBRATION_TEMPERATURE, dim=1)


def _decision_metadata(probs_np: np.ndarray,
                       top3_idx: np.ndarray) -> dict:
    confidence = float(probs_np[top3_idx[0]]) * 100.0
    top2 = float(probs_np[top3_idx[1]]) * 100.0 if len(top3_idx) > 1 else 0.0
    margin = confidence - top2
    warnings = []
    if confidence < LOW_CONFIDENCE_THRESHOLD:
        warnings.append("low_confidence")
    if margin < AMBIGUOUS_TOP2_MARGIN:
        warnings.append("ambiguous_top2")
    return {
        "calibration_temperature": CALIBRATION_TEMPERATURE,
        "decision_status": "uncertain" if warnings else "identified",
        "warnings": warnings,
        "top2_margin": round(margin, 1),
    }


def _predict_probs_from_pil(img: Image.Image) -> np.ndarray:
    tensor = inference_transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        probs = _calibrated_probs(raptor_model(tensor))[0]
    return probs.cpu().numpy()


def _choose_inference_image(img: Image.Image) -> tuple[np.ndarray, dict]:
    """
    Classify whole image and, when available, YOLO crop.

    The default adaptive policy keeps the whole-image prediction unless
    the crop is at least YOLO_CROP_CONFIDENCE_GAIN points more confident.
    This reflects the v1.5 ablation: YOLO is useful infrastructure, but
    crop-only inference is not automatically better for this checkpoint.
    """
    whole_probs = _predict_probs_from_pil(img)
    crop, detection_meta = _select_yolo_crop(img)
    if detection_meta is None:
        return whole_probs, {
            "detector": "whole_image",
            "bbox": None,
            "bbox_score": None,
            "inference_mode": "whole_image",
            "yolo_crop_available": False,
        }

    crop_probs = _predict_probs_from_pil(crop)
    whole_conf = float(whole_probs.max()) * 100.0
    crop_conf = float(crop_probs.max()) * 100.0
    use_crop = (
        YOLO_CROP_POLICY == "always" or
        (YOLO_CROP_POLICY == "adaptive" and
         crop_conf >= whole_conf + YOLO_CROP_CONFIDENCE_GAIN)
    )
    if YOLO_CROP_POLICY == "never":
        use_crop = False

    meta = dict(detection_meta)
    meta.update({
        "inference_mode": "yolo_crop" if use_crop else "whole_image_yolo_detected",
        "yolo_crop_available": True,
        "whole_image_confidence": round(whole_conf, 1),
        "yolo_crop_confidence": round(crop_conf, 1),
        "yolo_crop_policy": YOLO_CROP_POLICY,
    })
    return (crop_probs if use_crop else whole_probs), meta


def predict_image(img_path):
    """
    Realiza la predicción sobre una imagen.

    Returns:
        dict con especie predicha, confianza y top-3
    """
    if raptor_model is None:
        if LIGHTWEIGHT_MODE:
            return _dummy_prediction()
        raise RuntimeError("Model is not loaded.")

    img = Image.open(img_path).convert("RGB")
    probs_np, inference_meta = _choose_inference_image(img)

    # Top-3 predicciones
    top3_idx = np.argsort(probs_np)[::-1][:3]

    # Use locale-specific common names, status, habitat, etc.
    localized = _localized_species_info()

    top3 = []
    for idx in top3_idx:
        species_key = CLASS_ORDER[idx]
        info = localized[species_key]
        top3.append({
            "species_key":     species_key,
            "common_name":     info["common_name"],
            "scientific_name": info["scientific_name"],
            "confidence":      round(float(probs_np[idx]) * 100, 1),
            "color":           info["color"]
        })

    # Predicción principal
    best_key  = CLASS_ORDER[top3_idx[0]]
    best_info = localized[best_key]

    result = {
        "species_key":     best_key,
        "common_name":     best_info["common_name"],
        "scientific_name": best_info["scientific_name"],
        "confidence":      round(float(probs_np[top3_idx[0]])*100,1),
        "epbc_status":     best_info["epbc_status"],
        "habitat":         best_info["habitat"],
        "wingspan_cm":     best_info["wingspan_cm"],
        "length_cm":       best_info["length_cm"],
        "diagnostic":      best_info["diagnostic"],
        "auslan_sign":     best_info["auslan_sign"],
        "auslan_video":    best_info["auslan_video"],
        "color":           best_info["color"],
        "top3":            top3
    }
    result.update(_decision_metadata(probs_np, top3_idx))
    result.update(inference_meta)
    result.setdefault("yolo_crop_policy", YOLO_CROP_POLICY)
    return result


# ─── Rutas Flask ──────────────────────────────────────
def _localized_species_info(lang: str | None = None,
                            include_roadmap: bool = False) -> dict:
    """
    Merge non-translatable fields from SPECIES_INFO (class_idx,
    wingspan_cm, length_cm, auslan_video, color, scientific_name)
    with the locale-specific overrides (common_name, epbc_status,
    habitat, diagnostic, auslan_sign + the Merlin profile fields).
    """
    lang = lang or get_locale()
    loc  = get_species_data(lang)
    out: dict = {}
    source = SPECIES_INFO if include_roadmap else _active_species_info()
    for key, base in source.items():
        merged = dict(base)
        merged.update(loc.get(key, {}))
        # 'behaviour' is the canonical field in SPECIES_I18N;
        # templates use 'behavior' as alias for backward compat.
        if "behaviour" in merged and "behavior" not in merged:
            merged["behavior"] = merged["behaviour"]
        out[key] = merged
    return out


@app.route("/set_lang/<code>")
def set_lang(code: str):
    """
    Change the user's UI language by setting a long-lived cookie.
    Falls through silently if the code is unknown.
    """
    target = request.args.get("next") or request.referrer or "/"
    resp   = make_response(redirect(target))
    if code in LANGUAGES:
        # 1 year cookie
        resp.set_cookie(COOKIE_NAME, code, max_age=60 * 60 * 24 * 365,
                        samesite="Lax")
    return resp



@app.route("/health")
def health():
    """Machine-readable app health endpoint for demos and deployment."""
    cuda_available = bool(
        torch is not None and hasattr(torch, "cuda") and torch.cuda.is_available()
    )
    return jsonify({
        "status": "ok",
        "project": "Australian Raptor CNN + AUSLAN",
        "model_version": MODEL_VERSION,
        "classifier": "EfficientNetB4",
        "detector": "YOLO",
        "active_species_count": NUM_CLASSES,
        "model_loaded": raptor_model is not None,
        "lightweight_mode": LIGHTWEIGHT_MODE,
        "device": str(device) if device is not None else "unavailable",
        "cuda_available": cuda_available,
        "yolo_crop_policy": YOLO_CROP_POLICY,
    })
@app.route("/")
def index():
    """Página principal — UI localizada."""
    return render_template("index.html",
                           species_info=_localized_species_info())


@app.route("/identify", methods=["POST"])
def identify():
    """
    Endpoint de identificación.
    Recibe imagen, ejecuta modelo, devuelve JSON.
    """
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Extensiones permitidas
    allowed = {"jpg", "jpeg", "png", "tiff", "bmp", "webp"}
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in allowed:
        return jsonify(
            {"error": f"Format not supported: {ext}"}
        ), 400

    # Guardar imagen temporalmente
    filename  = f"{uuid.uuid4()}.{ext}"
    img_path  = UPLOAD_DIR / filename

    try:
        file.save(str(img_path))
        result = predict_image(img_path)
        result["filename"] = filename
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Limpiar archivo temporal
        if img_path.exists():
            os.remove(img_path)


@app.route("/save_observation", methods=["POST"])
def save_observation():
    """
    Guarda una observación confirmada por el usuario
    en un archivo CSV local.
    """
    data = request.get_json()

    obs_file = PROJECT_ROOT / "results" / "observations.csv"
    obs_file.parent.mkdir(parents=True, exist_ok=True)
    file_exists = obs_file.exists()

    with open(obs_file, "a", newline="", encoding="utf-8") as f:
        fieldnames = [
            "timestamp", "species_key", "common_name",
            "scientific_name", "confidence", "latitude",
            "longitude", "notes", "observer_confirmed"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "timestamp":          datetime.now().isoformat(),
            "species_key":        data.get("species_key", ""),
            "common_name":        data.get("common_name", ""),
            "scientific_name":    data.get("scientific_name", ""),
            "confidence":         data.get("confidence", ""),
            "latitude":           data.get("latitude", ""),
            "longitude":          data.get("longitude", ""),
            "notes":              data.get("notes", ""),
            "observer_confirmed": data.get("confirmed", True)
        })

    return jsonify({"status": "saved"})


@app.route("/feedback", methods=["POST"])
def save_feedback():
    """
    Guarda la corrección del usuario cuando el modelo
    se equivocó. Lista para futuro reentrenamiento.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400

        correct_key = data.get("correct_key", "")
        is_out_of_domain = (correct_key == "other_not_listed")

        # Folder for retraining material — only for known classes.
        if not is_out_of_domain and correct_key:
            feedback_dir = (PROJECT_ROOT / "dataset" / "feedback"
                            / correct_key)
            feedback_dir.mkdir(parents=True, exist_ok=True)

        # Out-of-domain corrections go to a separate audit log so they
        # are not confused with in-domain retraining material.
        if is_out_of_domain:
            log_file = PROJECT_ROOT / "results" / "out_of_domain_log.csv"
        else:
            log_file = PROJECT_ROOT / "results" / "feedback_log.csv"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_exists = log_file.exists()

        feedback_id = str(uuid.uuid4())[:8]
        timestamp   = datetime.now().isoformat()
        with open(log_file, "a", newline="", encoding="utf-8") as f:
            fieldnames = [
                "feedback_id", "timestamp",
                "predicted_key", "predicted_name",
                "correct_key", "correct_name",
                "confidence",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                "feedback_id":    feedback_id,
                "timestamp":      timestamp,
                "predicted_key":  data.get("predicted_key", ""),
                "predicted_name": data.get("predicted_name", ""),
                "correct_key":    correct_key,
                "correct_name":   data.get("correct_name", ""),
                "confidence":     data.get("confidence", ""),
            })
        return jsonify({
            "status":           "saved",
            "feedback_id":      feedback_id,
            "out_of_domain":    is_out_of_domain,
            "message":          ("Out-of-domain report saved." if
                                  is_out_of_domain else
                                  "Correction saved successfully."),
        })
    except Exception as e:
        # Siempre devolver JSON aunque haya error
        return jsonify({"error": str(e)}), 500


@app.route("/feedback_stats", methods=["GET"])
def feedback_stats():
    """
    Devuelve estadísticas del log de correcciones para
    mostrarlas en el GUI tras enviar un feedback.
    Usadas por el frontend para indicar cuándo hay
    suficientes correcciones para reentrenar el modelo.
    """
    try:
        feedback_file = PROJECT_ROOT / "results" / "feedback_log.csv"
        # Umbral mínimo de correcciones antes de reentrenar
        retrain_threshold = 50

        if not feedback_file.exists():
            return jsonify({
                "total_corrections": 0,
                "ready_to_retrain":  False,
                "threshold":         retrain_threshold
            })

        with open(feedback_file, "r", newline="",
                  encoding="utf-8") as f:
            reader = csv.DictReader(f)
            total = sum(1 for _ in reader)

        # Distribución por especie correcta (top 5)
        per_species = {}
        with open(feedback_file, "r", newline="",
                  encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = row.get("correct_key", "unknown")
                per_species[key] = per_species.get(key, 0) + 1

        return jsonify({
            "total_corrections": total,
            "ready_to_retrain":  total >= retrain_threshold,
            "threshold":         retrain_threshold,
            "per_species":       per_species
        })

    except Exception as e:
        return jsonify({
            "error":             str(e),
            "total_corrections": 0,
            "ready_to_retrain":  False
        }), 500


def _load_species_metrics():
    """
    Carga métricas por especie desde results/reporte_final.json
    y cuenta imágenes de entrenamiento desde dataset/raw/.
    Devuelve un dict species_key -> {f1, precision, recall, support, train_count}
    """
    metrics = {}
    # Métricas por clase (precision / recall / F1)
    report_path = PROJECT_ROOT / "results" / "reporte_final.json"
    if report_path.exists():
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # El JSON usa nombres comunes; mapeo a species_key
            common_to_key = {
                info["common_name"]: key
                for key, info in SPECIES_INFO.items()
            }
            for common_name, m in (data.get("por_especie") or {}).items():
                key = common_to_key.get(common_name)
                if key:
                    metrics[key] = {
                        "f1":        m.get("f1"),
                        "precision": m.get("precision"),
                        "recall":    m.get("recall"),
                        "support":   m.get("support"),
                    }
        except Exception as e:
            print(f"[species] could not load metrics: {e}")

    # Conteo de imágenes de entrenamiento por especie
    raw_dir = PROJECT_ROOT / "dataset" / "raw"
    for key in CLASS_ORDER:
        sp_dir = raw_dir / key
        count  = 0
        if sp_dir.exists():
            count = sum(
                1 for _ in sp_dir.glob("*.[jpJP]*[gG]*")
            )
        metrics.setdefault(key, {})["train_count"] = count

    return metrics


def _load_ebird_enrichment() -> dict:
    """
    Loads ``results/ebird_enrichment.json`` if present. Returns
    an empty dict on any error so the GUI degrades gracefully
    when the eBird fetcher has not been run yet.
    """
    p = PROJECT_ROOT / "results" / "ebird_enrichment.json"
    if not p.exists():
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("species", {})
    except Exception as e:
        print(f"[ebird] could not load enrichment: {e}")
        return {}


@app.route("/species")
def species_list():
    """Catálogo de especies — métricas + eBird + i18n."""
    lang     = get_locale()
    metrics  = _load_species_metrics()
    info_loc = _localized_species_info(lang)
    return render_template("species.html",
                           species_info=info_loc,
                           species_metrics=metrics,
                           species_details=info_loc,
                           behavior_videos=_behavior_video_status(),
                           ebird=_load_ebird_enrichment())


# ─── Paso 8 — Exportación CSV / ALA ─────────────────────
def _load_observations() -> list[dict]:
    """Read the local observations CSV; returns [] if not present."""
    obs_file = PROJECT_ROOT / "results" / "observations.csv"
    if not obs_file.exists():
        return []
    rows: list[dict] = []
    with open(obs_file, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def _to_dwc_rows(obs_rows: list[dict]) -> list[dict]:
    """
    Convert internal observation rows → Darwin Core compliant rows.
    Reference: https://dwc.tdwg.org/terms/

    Output is suitable for upload to ALA's `Sightings`/`User
    Submitted Records` portal and to GBIF data publishers.
    """
    out: list[dict] = []
    for i, r in enumerate(obs_rows):
        # eventDate: parse ISO 8601 timestamp from our internal column
        ts = r.get("timestamp", "") or ""
        event_date = ts.split("T")[0] if "T" in ts else ts
        confidence = r.get("confidence", "") or ""
        confirmed  = (r.get("observer_confirmed", "") or "").lower()
        verification = ("verifiedByExpert"
                        if confirmed in {"true", "1", "yes"}
                        else "unverified")

        identified_by = (
            f"Australian Raptor CNN {MODEL_VERSION} "
            "(YOLO-assisted pipeline, EfficientNetB4 classifier, "
            f"iNaturalist + ALA, F1-macro {MODEL_F1_MACRO})"
        )

        out.append({
            "occurrenceID":       f"raptor-au-{i+1:06d}",
            "basisOfRecord":      "HumanObservation",
            "eventDate":          event_date,
            "scientificName":     r.get("scientific_name", ""),
            "vernacularName":     r.get("common_name", ""),
            "decimalLatitude":    r.get("latitude", ""),
            "decimalLongitude":   r.get("longitude", ""),
            "geodeticDatum":      "WGS84",
            "recordedBy":         "Australian Raptor CNN — citizen science",
            "identifiedBy":       identified_by,
            "identificationVerificationStatus": verification,
            "occurrenceRemarks":  r.get("notes", ""),
            "dataGeneralizations":
                f"AI-assisted identification, confidence={confidence}%",
            "dynamicProperties":
                f"{{\"model_confidence\":{confidence},"
                f"\"observer_confirmed\":{confirmed}}}",
        })
    return out


def _csv_response(rows: list[dict],
                  fieldnames: list[str],
                  filename: str) -> Response:
    """Build a Flask Response that streams a downloadable CSV."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames,
                            extrasaction="ignore")
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )


@app.route("/data")
def data_dashboard():
    """
    Página /data: estadísticas básicas del CSV de observaciones
    + botones para descargar en formato local y Darwin Core (ALA).
    """
    rows = _load_observations()

    # Distribución por especie
    by_species: dict[str, int] = {}
    for r in rows:
        key = r.get("species_key") or "unknown"
        by_species[key] = by_species.get(key, 0) + 1

    # Conteo de feedback
    feedback_file = PROJECT_ROOT / "results" / "feedback_log.csv"
    feedback_count = 0
    if feedback_file.exists():
        with open(feedback_file, "r", newline="",
                  encoding="utf-8") as f:
            feedback_count = sum(1 for _ in csv.DictReader(f))

    # Para mostrar las últimas 10 observaciones
    recent = list(reversed(rows))[:10]

    return render_template(
        "data.html",
        species_info=_localized_species_info(),
        total_observations=len(rows),
        observations_by_species=by_species,
        feedback_count=feedback_count,
        recent_observations=recent,
    )


@app.route("/export/observations.csv")
def export_observations():
    """Raw observations CSV — internal schema."""
    rows = _load_observations()
    fieldnames = [
        "timestamp", "species_key", "common_name",
        "scientific_name", "confidence", "latitude",
        "longitude", "notes", "observer_confirmed",
    ]
    return _csv_response(rows, fieldnames,
                         "raptor_au_observations.csv")


@app.route("/export/observations_dwc.csv")
def export_observations_dwc():
    """Darwin Core formatted CSV — ready for ALA / GBIF upload."""
    rows = _to_dwc_rows(_load_observations())
    fieldnames = [
        "occurrenceID", "basisOfRecord", "eventDate",
        "scientificName", "vernacularName",
        "decimalLatitude", "decimalLongitude", "geodeticDatum",
        "recordedBy", "identifiedBy",
        "identificationVerificationStatus",
        "occurrenceRemarks", "dataGeneralizations",
        "dynamicProperties",
    ]
    return _csv_response(rows, fieldnames,
                         "raptor_au_observations_dwc.csv")


@app.route("/export/feedback.csv")
def export_feedback():
    """Feedback log CSV — useful for re-training audits."""
    feedback_file = PROJECT_ROOT / "results" / "feedback_log.csv"
    if not feedback_file.exists():
        return Response("feedback log is empty", status=404)
    with open(feedback_file, "r", encoding="utf-8") as f:
        content = f.read()
    return Response(
        content,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
                'attachment; filename="raptor_au_feedback_log.csv"'
        },
    )


@app.route("/auslan_videos/<filename>")
def auslan_video(filename):
    """Sirve los videos AUSLAN."""
    return send_from_directory(
        str(BASE_DIR / "static" / "auslan_videos"),
        filename
    )


# ─── Video analysis (multi-species, multi-bird) ──────────
_yolo_detector = None


def _yolo_weights_path() -> str:
    configured = os.environ.get("RAPTOR_YOLO_WEIGHTS")
    if configured:
        return configured
    local = PROJECT_ROOT / "models" / "yolov8n.pt"
    return str(local) if local.exists() else "yolov8n.pt"


def _lazy_yolo_detector():
    """
    YOLO detector reused across video frames.

    If ultralytics/weights are unavailable, detection is disabled and
    callers can still classify the whole image through /identify.
    """
    global _yolo_detector
    if _yolo_detector is False:
        return None
    if _yolo_detector is None:
        try:
            _yolo_detector = YoloBirdDetector(_yolo_weights_path(),
                                              confidence=0.5)
            print(f"YOLO bird detector loaded: {_yolo_weights_path()}")
        except (YoloUnavailable, Exception) as exc:
            print(f"[video] YOLO unavailable; detection disabled: {exc}")
            _yolo_detector = False
            return None
    return _yolo_detector


def _detect_birds(pil: Image.Image, min_conf: float = 0.5) -> list[dict]:
    """
    Detect bird boxes in one frame with YOLO.

    Returns dicts with bbox, bbox_score and detector. If YOLO is not
    available, returns an empty list rather than switching architecture.
    """
    yolo = _lazy_yolo_detector()
    if yolo is None:
        return []

    out = []
    for box in yolo.detect(pil):
        if box.confidence < min_conf:
            continue
        out.append({
            "bbox": box.bbox,
            "bbox_score": box.confidence,
            "detector": box.source,
        })
    return out


def _classify_crop(crop_pil) -> dict:
    """Run the trained classifier on a single bird crop (PIL.Image)."""
    tensor = inference_transform(crop_pil).unsqueeze(0).to(device)
    with torch.no_grad():
        probs = _calibrated_probs(raptor_model(tensor))[0].cpu().numpy()
    idx = int(np.argmax(probs))
    sp_key = CLASS_ORDER[idx]
    return {
        "species_key":  sp_key,
        "common_name":  SPECIES_INFO[sp_key]["common_name"],
        "scientific":   SPECIES_INFO[sp_key]["scientific_name"],
        "color":        SPECIES_INFO[sp_key]["color"],
        "confidence":   round(float(probs[idx]) * 100, 1),
    }


@app.route("/identify_video", methods=["POST"])
def identify_video():
    """
    Multi-species video analysis.

    Pipeline (per uploaded video):
      1. Sample frames at ~1 fps using OpenCV.
      2. Run YOLO on each frame to find bird bboxes.
      3. Crop each detected bird and classify with the CNN.
      4. Return a per-frame timeline + a per-species summary.

    Heavy operation — typical 30-second clip @ 1 fps yields
    ~30 frames; runtime is dominated by the detector
    (~0.5-2 s per frame on CPU; ~0.1 s on GPU).
    """
    try:
        import cv2
    except Exception:
        return jsonify({"error": "OpenCV (cv2) is not installed. "
                                  "Run: pip install opencv-python"}), 500

    if "video" not in request.files:
        return jsonify({"error": "No video uploaded"}), 400
    file = request.files["video"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    allowed_ext = {"mp4", "mov", "webm", "mkv", "avi"}
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in allowed_ext:
        return jsonify({"error": f"Format not supported: {ext}"}), 400

    tmp_path = UPLOAD_DIR / f"{uuid.uuid4()}.{ext}"
    file.save(str(tmp_path))

    try:
        cap = cv2.VideoCapture(str(tmp_path))
        if not cap.isOpened():
            return jsonify({"error": "Could not open video"}), 500

        fps      = cap.get(cv2.CAP_PROP_FPS) or 30.0
        n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        duration = n_frames / fps if fps > 0 else 0
        # Sample roughly one frame per second; cap at 60 frames total.
        step     = max(1, int(round(fps)))
        max_frames = 60
        sampled  = 0

        timeline: list[dict] = []
        per_species: dict[str, int] = {}
        frame_idx = 0

        while sampled < max_frames:
            ret, bgr = cap.read()
            if not ret:
                break
            if frame_idx % step != 0:
                frame_idx += 1
                continue

            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            pil = Image.fromarray(rgb)
            W, H = pil.size

            birds: list[dict] = []
            for detection in _detect_birds(pil, min_conf=0.5):
                x0, y0, x1, y1 = detection["bbox"]
                # Add a 5% margin for the classifier to use context
                m = 0.05 * min(W, H)
                cx0 = max(0, int(x0 - m))
                cy0 = max(0, int(y0 - m))
                cx1 = min(W, int(x1 + m))
                cy1 = min(H, int(y1 + m))
                crop = pil.crop((cx0, cy0, cx1, cy1))
                # Skip near-zero crops
                if min(crop.size) < 32:
                    continue
                pred = _classify_crop(crop)
                pred["bbox"] = [cx0, cy0, cx1, cy1]
                pred["bbox_score"] = detection["bbox_score"]
                pred["detector"] = detection["detector"]
                birds.append(pred)
                per_species[pred["species_key"]] = (
                    per_species.get(pred["species_key"], 0) + 1)

            timeline.append({
                "t_seconds":  round(frame_idx / fps, 2),
                "frame_idx":  frame_idx,
                "n_birds":    len(birds),
                "detections": birds,
            })
            sampled += 1
            frame_idx += 1
            # cv2 is a streaming decoder — fast skip instead of grab loop
            for _ in range(step - 1):
                cap.grab()
                frame_idx += 1

        cap.release()

        # Aggregate into a friendly summary
        summary = sorted(
            [{
                "species_key": k,
                "common_name": SPECIES_INFO[k]["common_name"],
                "scientific":  SPECIES_INFO[k]["scientific_name"],
                "color":       SPECIES_INFO[k]["color"],
                "frames_with_species": per_species[k],
            } for k in per_species],
            key=lambda x: -x["frames_with_species"],
        )

        return jsonify({
            "duration_seconds": round(duration, 2),
            "video_fps":        round(fps, 2),
            "frames_sampled":   sampled,
            "timeline":         timeline,
            "summary":          summary,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            tmp_path.unlink()
        except Exception:
            pass


@app.route("/behavior_videos/<filename>")
def behavior_video(filename):
    """
    Sirve los videos de comportamiento por especie.
    Los archivos viven en gui/static/behavior_videos/<species_key>.mp4
    Si el archivo no existe, devuelve 404; el frontend cae a un
    placeholder con instrucciones para subir el video.
    """
    return send_from_directory(
        str(BASE_DIR / "static" / "behavior_videos"),
        filename
    )


def _behavior_video_status() -> dict[str, dict]:
    """
    Returns, per species_key, whether a behavior video file is present
    on disk. Used by templates to conditionally render the video tile.
    """
    folder = BASE_DIR / "static" / "behavior_videos"
    out = {}
    for key in CLASS_ORDER:
        # Accept .mp4, .webm, .mov in this order of preference.
        for ext in ("mp4", "webm", "mov"):
            p = folder / f"{key}.{ext}"
            if p.exists():
                out[key] = {"exists": True, "filename": p.name,
                            "size_mb": round(p.stat().st_size / 1e6, 1)}
                break
        else:
            out[key] = {"exists": False, "filename": f"{key}.mp4",
                        "size_mb": 0}
    return out


if __name__ == "__main__":
    print("\n🦅 Australian Raptor CNN — Web App")
    print(f"   Modelo: {MODEL_PATH.name}")
    print(f"   Dispositivo: {device}")
    print(f"   URL: http://localhost:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
