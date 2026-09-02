from typing import Literal

from pydantic import BaseModel, Field


class AnalysisResult(BaseModel):
    prob_ai: float = Field(
        ge=0.0, le=1.0, description="Probabilidade de a imagem ser gerada por IA"
    )
    prob_real: float = Field(ge=0.0, le=1.0, description="Probabilidade complementar")
    label: Literal["ai-generated", "real"]
    model: str = Field(description="Identificador do modelo/detector usado")


class HealthStatus(BaseModel):
    status: Literal["ok"]
    model: str
    mock: bool
