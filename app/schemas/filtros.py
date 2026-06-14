from pydantic import BaseModel, Field


class MunicipioFiltro(BaseModel):
    codigo: int
    nome: str


class MetricaFiltro(BaseModel):
    chave: str = Field(
        ..., description="Identificador interno da métrica (ex: 'in_acessibilidade_rampas')."
    )
    label: str = Field(..., description="Label PT-BR para exibição (ex: 'Rampas').")


class FiltrosData(BaseModel):
    """Opções de filtro aplicáveis, compartilháveis entre painéis."""

    municipios: list[MunicipioFiltro] = Field(
        ..., description="Municípios disponíveis no recorte."
    )
    anos: list[int] = Field(..., description="Anos de censo disponíveis.")
    rede_ensino: list[str] = Field(
        ..., description="Redes de ensino: Federal, Estadual, Municipal, Privada."
    )
    tp_localizacao: list[str] = Field(
        ..., description="Tipos de localização: Urbana, Rural."
    )
    metricas: list[MetricaFiltro] | None = Field(
        None,
        description=(
            "Catálogo de métricas do painel informado em ?painel. "
            "Omitido quando nenhum painel é informado."
        ),
    )


class FiltrosResponse(BaseModel):
    """Resposta do endpoint genérico de filtros aplicáveis."""

    descricao: str = Field(..., description="Identificador semântico do recurso.")
    data: FiltrosData
