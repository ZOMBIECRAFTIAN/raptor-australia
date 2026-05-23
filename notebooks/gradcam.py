"""
Grad-CAM Interpretability — Australian Raptor CNN
=========================================================
Generates Grad-CAM heatmaps overlaid on input images to verify
the trained model is attending to the correct morphological
features (wing silhouette, tail shape, body coloration) instead
of background or spurious cues.

This is an interpretability tool — the model itself does not
change. The heatmap is computed by:

  1. Forward-pass the image through the CNN.
  2. Capture activations of the last convolutional block.
  3. Backward-pass the chosen class's logit.
  4. Weight the activations by the gradient channel-wise (sums in
     spatial dims) and ReLU.
  5. Upsample to the input resolution and normalise to [0, 1].

The method is Selvaraju et al., 2017 (Grad-CAM:
https://arxiv.org/abs/1610.02391).

Usage (from project root, with raptor_env active):
    python notebooks/gradcam.py --image C:\\path\\to\\photo.jpg
    python notebooks/gradcam.py --image foo.jpg --arch efficientnet_b4
    python notebooks/gradcam.py --image foo.jpg --class-idx 3

Output saved to results/gradcam_<image_stem>.png by default.

This script is methodologically inspired by the author's prior
work on the Veracruz raptor identification project
(github.com/ZOMBIECRAFTIAN/raptors-cnn). Brian Fernández Báez,
Computer Systems Engineer.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from torchvision import models
import numpy as np
from PIL import Image

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ─── Project paths ───────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent.parent
MODEL_PATH  = BASE_DIR / "models" / "best_model.pth"
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Match the architecture used in gui/app.py / notebooks/retrain.py
INPUT_SIZE   = 380
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]
NUM_CLASSES  = 8

SPECIES_LABELS = [
    "Wedge-tailed Eagle",      # aquila_audax
    "Spotted Harrier",         # circus_assimilis
    "Black-shouldered Kite",   # elanus_axillaris
    "Nankeen Kestrel",         # falco_cenchroides
    "Peregrine Falcon",        # falco_peregrinus
    "Little Eagle",            # hieraaetus_morphnoides
    "Square-tailed Kite",      # lophoictinia_isura
    "Brown Goshawk",           # tachyspiza_fasciata
]


# ─── Model construction (mirrors gui/app.py) ────────────
class AustralianRaptorCNN(nn.Module):
    def __init__(self, num_classes: int = NUM_CLASSES,
                 dropout_rate: float = 0.4):
        super().__init__()
        self.backbone = models.efficientnet_b4(weights=None)
        nf = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=dropout_rate, inplace=True),
            nn.Linear(nf, 512),
            nn.ReLU(),
            nn.Dropout(p=dropout_rate / 2),
            nn.Linear(512, num_classes),
        )

    def forward(self, x):
        return self.backbone(x)


def build_model(arch: str = "efficientnet_b4",
                num_classes: int = NUM_CLASSES) -> nn.Module:
    """Multi-architecture builder, matching the future v2.0 plan."""
    arch = arch.lower()
    if arch == "efficientnet_b4":
        return AustralianRaptorCNN(num_classes)
    if arch == "resnet50":
        m = models.resnet50(weights=None)
        m.fc = nn.Sequential(nn.Dropout(0.3),
                             nn.Linear(m.fc.in_features, num_classes))
        return m
    if arch == "mobilenet_v3_large":
        m = models.mobilenet_v3_large(weights=None)
        m.classifier[-1] = nn.Linear(
            m.classifier[-1].in_features, num_classes)
        return m
    if arch == "convnext_tiny":
        m = models.convnext_tiny(weights=None)
        m.classifier[-1] = nn.Linear(
            m.classifier[-1].in_features, num_classes)
        return m
    raise ValueError(f"Unsupported architecture: {arch}")


def get_target_layer(model: nn.Module, arch: str) -> nn.Module:
    """Returns the last convolutional block for each backbone."""
    arch = arch.lower()
    if arch == "efficientnet_b4":
        # AustralianRaptorCNN wraps the EfficientNet under .backbone
        return model.backbone.features[-1]
    if arch == "resnet50":           return model.layer4[-1]
    if arch == "mobilenet_v3_large": return model.features[-1]
    if arch == "convnext_tiny":      return model.features[-1]
    raise ValueError(f"Unsupported architecture: {arch}")


# ─── Grad-CAM core ──────────────────────────────────────
class GradCAM:
    """Minimal Grad-CAM implementation for one target layer."""

    def __init__(self, model: nn.Module, target_layer: nn.Module):
        self.model       = model.eval()
        self.activations = None
        self.gradients   = None
        target_layer.register_forward_hook(self._save_activation)
        target_layer.register_full_backward_hook(self._save_gradient)

    def _save_activation(self, _module, _inp, out):
        self.activations = out.detach()

    def _save_gradient(self, _module, _grad_in, grad_out):
        self.gradients = grad_out[0].detach()

    def __call__(self, x: torch.Tensor,
                 class_idx: int | None = None
                 ) -> tuple[np.ndarray, int, np.ndarray]:
        logits = self.model(x)
        probs  = F.softmax(logits, dim=1)[0].detach().cpu().numpy()
        if class_idx is None:
            class_idx = int(probs.argmax())
        score = logits[0, class_idx]
        self.model.zero_grad()
        score.backward()

        weights = self.gradients.mean(dim=(2, 3), keepdim=True)
        cam = F.relu((weights * self.activations).sum(dim=1, keepdim=True))
        cam = F.interpolate(cam, size=x.shape[-2:],
                            mode="bilinear", align_corners=False)
        cam = cam.squeeze().cpu().numpy()
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        return cam, class_idx, probs


# ─── Inference + plotting ───────────────────────────────
def get_eval_transform():
    return transforms.Compose([
        transforms.Resize((420, 420)),
        transforms.CenterCrop(INPUT_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def render(image_path: Path, cam: np.ndarray, pred_idx: int,
           probs: np.ndarray, out_path: Path) -> None:
    img = Image.open(image_path).convert("RGB").resize(
        (INPUT_SIZE, INPUT_SIZE))

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    axes[0].imshow(img)
    axes[0].set_title(f"Input — {image_path.name}", fontsize=11)
    axes[0].axis("off")

    axes[1].imshow(img)
    axes[1].imshow(cam, cmap="jet", alpha=0.5)
    axes[1].set_title(f"Grad-CAM — {SPECIES_LABELS[pred_idx]}\n"
                       f"top-1 conf: {probs[pred_idx]*100:.1f}%",
                       fontsize=11)
    axes[1].axis("off")

    top3 = np.argsort(probs)[::-1][:3]
    bars = [SPECIES_LABELS[i] for i in top3]
    vals = [probs[i] * 100 for i in top3]
    colors = ["#1A7C6E" if i == 0 else "#1B4F72" for i in range(3)]
    axes[2].barh(bars[::-1], vals[::-1], color=colors[::-1])
    axes[2].set_xlim(0, 100)
    axes[2].set_xlabel("Confidence (%)")
    axes[2].set_title("Top-3 predictions", fontsize=11)
    for spine in ("top", "right"):
        axes[2].spines[spine].set_visible(False)

    fig.tight_layout()
    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ Saved {out_path}")


# ─── CLI ────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--image", required=True,
                   help="Path to the JPG/PNG to analyse")
    p.add_argument("--arch", default="efficientnet_b4",
                   choices=["efficientnet_b4", "resnet50",
                            "mobilenet_v3_large", "convnext_tiny"])
    p.add_argument("--weights", default=str(MODEL_PATH),
                   help="Path to .pth checkpoint (default: models/best_model.pth)")
    p.add_argument("--class-idx", type=int, default=None,
                   help="Force a specific class index (0-7). "
                        "If omitted, uses the top-1 prediction.")
    p.add_argument("--out", default=None,
                   help="Output path (default: results/gradcam_<stem>.png)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available()
                          else "cpu")
    print(f"Grad-CAM — arch={args.arch} · device={device}")

    model = build_model(args.arch).to(device)

    ck = torch.load(args.weights, map_location=device)
    if isinstance(ck, dict) and "model_state_dict" in ck:
        model.load_state_dict(ck["model_state_dict"])
    else:
        model.load_state_dict(ck)
    model.eval()

    tf  = get_eval_transform()
    img = Image.open(args.image).convert("RGB")
    x   = tf(img).unsqueeze(0).to(device)

    cam_engine = GradCAM(model, get_target_layer(model, args.arch))
    cam, pred_idx, probs = cam_engine(x, args.class_idx)

    out_path = Path(args.out) if args.out else (
        RESULTS_DIR / f"gradcam_{Path(args.image).stem}.png")
    render(Path(args.image), cam, pred_idx, probs, out_path)


if __name__ == "__main__":
    main()
