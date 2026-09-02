"""Avalia um checkpoint treinado sobre o split de teste.

Uso:
    python -m training.evaluate --checkpoint models/gemini_detector.pt --data-dir data
"""

import argparse
import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from app.detectors.gemini_model import PREPROCESS, GeminiDetectorModel
from training.dataset import ImageFolderBinaryDataset
from training.metrics import compute_metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--split", default="test", choices=["validation", "test"])
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = GeminiDetectorModel(pretrained=False).to(device)
    checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=True)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()

    dataset = ImageFolderBinaryDataset(args.data_dir / args.split, transform=PREPROCESS)
    loader = DataLoader(dataset, batch_size=args.batch_size, num_workers=2)

    y_true: list[float] = []
    y_prob: list[float] = []
    with torch.inference_mode():
        for images, targets in loader:
            logits = model(images.to(device))
            y_true.extend(targets.tolist())
            y_prob.extend(torch.sigmoid(logits).cpu().tolist())

    metrics = compute_metrics(y_true, y_prob)
    print(f"Split: {args.split} ({len(dataset)} imagens)")
    for name, value in metrics.as_dict().items():
        print(f"  {name}: {value}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
