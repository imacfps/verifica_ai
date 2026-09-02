"""Arquitetura do detector próprio (Fase 2 — foco: gerador do Gemini).

Transfer learning sobre um backbone convolucional pré-treinado em ImageNet,
com uma cabeça de classificação binária (real vs. gerada por IA) por cima.
Este módulo é compartilhado entre inferência (`gemini.py`) e o pipeline de
treino (`training/`) para garantir que o checkpoint salvo sempre corresponda
exatamente à arquitetura usada para carregá-lo.
"""

import torch
from torch import nn
from torchvision.models import ResNet18_Weights, resnet18
from torchvision.transforms import v2 as transforms

IMAGE_SIZE = 224

# Normalização padrão dos pesos ImageNet usados no backbone.
PREPROCESS = transforms.Compose(
    [
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToImage(),
        transforms.ToDtype(torch.float32, scale=True),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)


class GeminiDetectorModel(nn.Module):
    """ResNet-18 congelada + cabeça densa treinável para detecção binária."""

    def __init__(self, pretrained: bool = True):
        super().__init__()
        weights = ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
        backbone = resnet18(weights=weights)
        in_features = backbone.fc.in_features
        backbone.fc = nn.Identity()
        self.backbone = backbone
        self.classifier = nn.Sequential(
            nn.Linear(in_features, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(128, 1),
        )
        self.freeze_backbone()

    def freeze_backbone(self) -> None:
        for param in self.backbone.parameters():
            param.requires_grad = False

    def unfreeze_backbone(self) -> None:
        """Habilita fine-tuning completo — usar só na etapa final de treino."""
        for param in self.backbone.parameters():
            param.requires_grad = True

    def forward(self, x):
        features = self.backbone(x)
        return self.classifier(features).squeeze(-1)  # logits, não probabilidades
