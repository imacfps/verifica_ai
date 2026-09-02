"""Dataset em disco para treino do GeminiDetector.

Convenção de diretórios (compatível com `torchvision.datasets.ImageFolder`,
mas com mapeamento de rótulo explícito — nunca inferido pela ordem
alfabética, que já causou bugs silenciosos em outros projetos):

    data/
      train/
        real/*.jpg
        ai_generated/*.jpg
      validation/
        real/*.jpg
        ai_generated/*.jpg
      test/
        real/*.jpg
        ai_generated/*.jpg

Quando a ingestão via banco de imagens consolidado (`docs/dataset.md`)
estiver disponível, este módulo pode ser trocado por uma versão que lê de
`dataset_images` + object storage sem alterar `train.py`.
"""

from pathlib import Path

from PIL import Image
from torch.utils.data import Dataset

LABEL_TO_TARGET = {"real": 0.0, "ai_generated": 1.0}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


class ImageFolderBinaryDataset(Dataset):
    def __init__(self, root: str | Path, transform=None):
        self.root = Path(root)
        self.transform = transform
        self.samples: list[tuple[Path, float]] = []

        for label, target in LABEL_TO_TARGET.items():
            label_dir = self.root / label
            if not label_dir.is_dir():
                continue
            for path in sorted(label_dir.iterdir()):
                if path.suffix.lower() in IMAGE_EXTENSIONS:
                    self.samples.append((path, target))

        if not self.samples:
            raise ValueError(
                f"Nenhuma imagem encontrada em '{self.root}'. Esperado "
                f"'{self.root}/real/' e '{self.root}/ai_generated/' com imagens."
            )

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int):
        path, target = self.samples[index]
        image = Image.open(path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, target
