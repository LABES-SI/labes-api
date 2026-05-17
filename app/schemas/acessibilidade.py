from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PlotlyFigure(BaseModel):
    """Figura Plotly bruta: o que o frontend passa direto para o Plotly.react()."""

    model_config = ConfigDict(extra="allow")

    data: list[dict[str, Any]] = Field(..., description="Traces do Plotly.")
    layout: dict[str, Any] = Field(..., description="Layout do Plotly.")


class Grafico(BaseModel):
    """Envelope de um gráfico do painel."""

    tipo: str = Field(..., description="Tipo do gráfico (ex: 'radar', 'bar').")
    titulo: str = Field(..., description="Título legível para o frontend.")
    plotly: PlotlyFigure = Field(..., description="Figura Plotly (data + layout).")


class MunicipioFiltro(BaseModel):
    codigo: int
    nome: str


class MetricaFiltro(BaseModel):
    chave: str = Field(..., description="Identificador interno da métrica (ex: 'in_acessibilidade_rampas').")
    label: str = Field(..., description="Label PT-BR para exibição (ex: 'Rampas').")


class DadosFiltros(BaseModel):
    municipios: list[MunicipioFiltro]
    anos: list[int]
    metricas: list[MetricaFiltro]


class PainelData(BaseModel):
    graficos: dict[str, Grafico] = Field(
        ...,
        description="Mapa de gráficos do painel, indexados por chave semântica.",
    )
    dados_filtros: DadosFiltros = Field(
        ...,
        description="Opções disponíveis para popular dropdowns do frontend.",
    )


class PainelResponse(BaseModel):
    """Resposta do painel: descrição + bloco de dados com gráficos e filtros."""

    descricao: str = Field(..., description="Identificador semântico do painel.")
    data: PainelData


class AnaliseTemporalFiltros(BaseModel):
    metricas: list[MetricaFiltro]


class AnaliseTemporalData(BaseModel):
    graficos: dict[str, Grafico] = Field(
        ...,
        description="Mapa de gráficos da análise temporal, indexados por chave semântica.",
    )
    dados_filtros: AnaliseTemporalFiltros = Field(
        ...,
        description="Opções disponíveis para popular dropdowns do frontend.",
    )


class AnaliseTemporalResponse(BaseModel):
    """Resposta da análise temporal por tipo de localização."""

    descricao: str = Field(..., description="Identificador semântico do recurso.")
    data: AnaliseTemporalData
