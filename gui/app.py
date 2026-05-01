"""
Australian Raptor CNN — Web Application
Backend Flask con inferencia del modelo entrenado
y módulo de vocabulario AUSLAN.
"""

import os
import json
import uuid
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
from flask import (Flask, render_template, request,
                   jsonify, send_from_directory, Response)
import io

# Detailed species profiles (Merlin-style content)
from species_data import SPECIES_DETAILS
from PIL import Image
from pathlib import Path
import numpy as np
from datetime import datetime
import csv

# ─── Configuración ────────────────────────────────────
BASE_DIR     = Path(__file__).parent
PROJECT_ROOT = BASE_DIR.parent
MODEL_PATH   = PROJECT_ROOT / "models" / "best_model.pth"
UPLOAD_DIR   = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max

# ─── Dispositivo ──────────────────────────────────────
device = torch.device("cuda" if torch.cuda.is_available()
                      else "cpu")

# ─── Información de especies ──────────────────────────
SPECIES_INFO = {
    "aquila_audax": {
        "common_name":     "Wedge-tailed Eagle",
        "scientific_name": "Aquila audax",
        "class_idx":       0,
        "epbc_status":     "Not listed (A. a. fleayi: Endangered)",
        "habitat":         "Open woodland, scrubland, grassland",
        "wingspan_cm":     "182-232 cm",
        "length_cm":       "85-105 cm",
        "diagnostic":      "Diamond/wedge-shaped tail, "
                           "arched wings in soaring flight",
        "auslan_sign":     "Both hands in inverted V, "
                           "extend downward with wide amplitude",
        "auslan_video":    "aquila_audax.svg",
        "color":           "#2C3E50"
    },
    "falco_peregrinus": {
        "common_name":     "Peregrine Falcon",
        "scientific_name": "Falco peregrinus macropus",
        "class_idx":       1,
        "epbc_status":     "Not listed",
        "habitat":         "Cliffs, urban areas, coastlines",
        "wingspan_cm":     "74-120 cm",
        "length_cm":       "34-58 cm",
        "diagnostic":      "Long pointed wings, black malar "
                           "stripe, fast vertical stoop",
        "auslan_sign":     "Dominant hand index finger, "
                           "rapid vertical dive downward",
        "auslan_video":    "falco_peregrinus.svg",
        "color":           "#8E44AD"
    },
    "circus_assimilis": {
        "common_name":     "Spotted Harrier",
        "scientific_name": "Circus assimilis",
        "class_idx":       2,
        "epbc_status":     "Vulnerable (NSW)",
        "habitat":         "Grassland, scrubland, open farmland",
        "wingspan_cm":     "110-148 cm",
        "length_cm":       "50-61 cm",
        "diagnostic":      "Facial disc, shallow V dihedral, "
                           "low sweeping flight",
        "auslan_sign":     "Both flat hands, lateral oscillating "
                           "glide at low height",
        "auslan_video":    "circus_assimilis.svg",
        "color":           "#27AE60"
    },
    "tachyspiza_fasciata": {
        "common_name":     "Brown Goshawk",
        "scientific_name": "Tachyspiza fasciata",
        "class_idx":       3,
        "epbc_status":     "Not listed",
        "habitat":         "Dense forest, woodland",
        "wingspan_cm":     "75-95 cm",
        "length_cm":       "40-55 cm",
        "diagnostic":      "Short rounded wings, long banded "
                           "tail, yellow iris",
        "auslan_sign":     "Curved hand, rapid zigzag movement "
                           "between trees",
        "auslan_video":    "tachyspiza_fasciata.svg",
        "color":           "#D35400"
    },
    "falco_cenchroides": {
        "common_name":     "Nankeen Kestrel",
        "scientific_name": "Falco cenchroides",
        "class_idx":       4,
        "epbc_status":     "Not listed",
        "habitat":         "Open habitats, grassland, farmland",
        "wingspan_cm":     "66-78 cm",
        "length_cm":       "28-35 cm",
        "diagnostic":      "Stationary hovering over open ground, "
                           "rufous coloration, fan tail",
        "auslan_sign":     "Open hand, stationary vibration "
                           "(hovering motion)",
        "auslan_video":    "falco_cenchroides.svg",
        "color":           "#E67E22"
    },
    "elanus_axillaris": {
        "common_name":     "Black-shouldered Kite",
        "scientific_name": "Elanus axillaris",
        "class_idx":       5,
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
        "color":           "#2980B9"
    },
    "lophoictinia_isura": {
        "common_name":     "Square-tailed Kite",
        "scientific_name": "Lophoictinia isura",
        "class_idx":       6,
        "epbc_status":     "Vulnerable (EPBC Act)",
        "habitat":         "Mature eucalyptus forest, woodland",
        "wingspan_cm":     "120-145 cm",
        "length_cm":       "50-56 cm",
        "diagnostic":      "Long square tail, slow soaring "
                           "over forest canopy",
        "auslan_sign":     "Flat hand, slow glide with "
                           "square tail demarcated",
        "auslan_video":    "lophoictinia_isura.svg",
        "color":           "#16A085"
    },
    "hieraaetus_morphnoides": {
        "common_name":     "Little Eagle",
        "scientific_name": "Hieraaetus morphnoides",
        "class_idx":       7,
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
        "color":           "#C0392B"
    }
}

# Orden de clases según ImageFolder (alfabético)
CLASS_ORDER = [
    "aquila_audax",
    "circus_assimilis",
    "elanus_axillaris",
    "falco_cenchroides",
    "falco_peregrinus",
    "hieraaetus_morphnoides",
    "lophoictinia_isura",
    "tachyspiza_fasciata"
]

# ─── Modelo ───────────────────────────────────────────
class AustralianRaptorCNN(nn.Module):
    def __init__(self, num_classes=8, dropout_rate=0.4):
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


def load_model():
    """Carga el modelo entrenado una sola vez al iniciar."""
    model = AustralianRaptorCNN(num_classes=8).to(device)
    checkpoint = torch.load(MODEL_PATH, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    print(f"✅ Modelo cargado — Val F1: "
          f"{checkpoint['val_f1']:.4f}")
    return model


# Cargar modelo al iniciar la app
raptor_model = load_model()

# ─── Transformación de inferencia ─────────────────────
inference_transform = transforms.Compose([
    transforms.Resize((420, 420)),
    transforms.CenterCrop(380),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def predict_image(img_path):
    """
    Realiza la predicción sobre una imagen.

    Returns:
        dict con especie predicha, confianza y top-3
    """
    img = Image.open(img_path).convert("RGB")
    tensor = inference_transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        output = raptor_model(tensor)
        probs  = torch.softmax(output, dim=1)[0]

    probs_np = probs.cpu().numpy()

    # Top-3 predicciones
    top3_idx = np.argsort(probs_np)[::-1][:3]

    top3 = []
    for idx in top3_idx:
        species_key = CLASS_ORDER[idx]
        info = SPECIES_INFO[species_key]
        top3.append({
            "species_key":     species_key,
            "common_name":     info["common_name"],
            "scientific_name": info["scientific_name"],
            "confidence":      round(float(probs_np[idx]) * 100, 1),
            "color":           info["color"]
        })

    # Predicción principal
    best_key  = CLASS_ORDER[top3_idx[0]]
    best_info = SPECIES_INFO[best_key]

    return {
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


# ─── Rutas Flask ──────────────────────────────────────
@app.route("/")
def index():
    """Página principal."""
    return render_template("index.html",
                           species_info=SPECIES_INFO)


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
        # Carpeta donde guardamos el registro
        feedback_dir = (PROJECT_ROOT / "dataset" / "feedback"
                        / data.get("correct_key", "unknown"))
        feedback_dir.mkdir(parents=True, exist_ok=True)
        # Guardar registro en CSV
        feedback_file = PROJECT_ROOT / "results" / "feedback_log.csv"
        file_exists   = feedback_file.exists()
        feedback_id = str(uuid.uuid4())[:8]
        timestamp   = datetime.now().isoformat()
        with open(feedback_file, "a", newline="",
                  encoding="utf-8") as f:
            fieldnames = [
                "feedback_id", "timestamp",
                "predicted_key", "predicted_name",
                "correct_key", "correct_name",
                "confidence"
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                "feedback_id":    feedback_id,
                "timestamp":      timestamp,
                "predicted_key":  data.get("predicted_key", ""),
                "predicted_name": data.get("predicted_name", ""),
                "correct_key":    data.get("correct_key", ""),
                "correct_name":   data.get("correct_name", ""),
                "confidence":     data.get("confidence", "")
            })
        return jsonify({
            "status":      "saved",
            "feedback_id": feedback_id,
            "message":     "Correction saved successfully."
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
    for key in SPECIES_INFO:
        sp_dir = raw_dir / key
        count  = 0
        if sp_dir.exists():
            count = sum(
                1 for _ in sp_dir.glob("*.[jpJP]*[gG]*")
            )
        metrics.setdefault(key, {})["train_count"] = count

    return metrics


@app.route("/species")
def species_list():
    """Página de catálogo de especies con métricas y detalles."""
    metrics = _load_species_metrics()
    return render_template("species.html",
                           species_info=SPECIES_INFO,
                           species_metrics=metrics,
                           species_details=SPECIES_DETAILS)


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
            "Australian Raptor CNN v1.0 "
            "(EfficientNetB4 transfer learning, F1-macro 0.78)"
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
        species_info=SPECIES_INFO,
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


if __name__ == "__main__":
    print("\n🦅 Australian Raptor CNN — Web App")
    print(f"   Modelo: {MODEL_PATH.name}")
    print(f"   Dispositivo: {device}")
    print(f"   URL: http://localhost:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000)