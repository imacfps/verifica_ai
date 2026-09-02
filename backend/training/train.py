"""Treina o GeminiDetectorModel sobre o banco de imagens consolidado.

Uso:
    python -m training.train --data-dir data --output models/gemini_detector.pt

Ver `training/README.md` para a convenção de diretórios esperada.
"""

import argparse
import random
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader
from tqdm import tqdm

from app.detectors.gemini_model import PREPROCESS, GeminiDetectorModel
from training.dataset import ImageFolderBinaryDataset
from training.metrics import compute_metrics


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def run_epoch(model, loader, device, optimizer=None) -> tuple[float, list[float], list[float]]:
    is_train = optimizer is not None
    model.train(is_train)
    criterion = nn.BCEWithLogitsLoss()

    total_loss = 0.0
    all_targets: list[float] = []
    all_probs: list[float] = []

    with torch.set_grad_enabled(is_train):
        for images, targets in tqdm(loader, leave=False):
            images, targets = images.to(device), targets.to(device).float()

            logits = model(images)
            loss = criterion(logits, targets)

            if is_train:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            total_loss += loss.item() * images.size(0)
            all_targets.extend(targets.detach().cpu().tolist())
            all_probs.extend(torch.sigmoid(logits).detach().cpu().tolist())

    return total_loss / len(loader.dataset), all_targets, all_probs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--output", type=Path, default=Path("models/gemini_detector.pt"))
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument(
        "--unfreeze-epoch",
        type=int,
        default=None,
        help="Época a partir da qual o backbone também é treinado (fine-tuning fino).",
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    set_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Dispositivo: {device}")

    train_ds = ImageFolderBinaryDataset(args.data_dir / "train", transform=PREPROCESS)
    val_ds = ImageFolderBinaryDataset(args.data_dir / "validation", transform=PREPROCESS)
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, num_workers=2)

    model = GeminiDetectorModel(pretrained=True).to(device)
    optimizer = torch.optim.Adam(
        (p for p in model.parameters() if p.requires_grad), lr=args.lr
    )

    best_val_loss = float("inf")
    args.output.parent.mkdir(parents=True, exist_ok=True)

    for epoch in range(1, args.epochs + 1):
        if args.unfreeze_epoch and epoch == args.unfreeze_epoch:
            print(f"Época {epoch}: descongelando backbone para fine-tuning.")
            model.unfreeze_backbone()
            optimizer = torch.optim.Adam(model.parameters(), lr=args.lr / 10)

        train_loss, _, _ = run_epoch(model, train_loader, device, optimizer)
        val_loss, y_true, y_prob = run_epoch(model, val_loader, device, optimizer=None)
        metrics = compute_metrics(y_true, y_prob)

        print(
            f"[{epoch:02d}/{args.epochs}] train_loss={train_loss:.4f} "
            f"val_loss={val_loss:.4f} val_acc={metrics.accuracy:.4f} "
            f"val_f1={metrics.f1:.4f} val_auc={metrics.roc_auc} "
            f"val_brier={metrics.brier:.4f} val_ece={metrics.ece:.4f}"
        )

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(
                {
                    "model_state": model.state_dict(),
                    "meta": {
                        "epoch": epoch,
                        "val_loss": val_loss,
                        **metrics.as_dict(),
                        "created_at": datetime.now(UTC).isoformat(),
                    },
                },
                args.output,
            )
            print(f"  -> novo melhor checkpoint salvo em {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
