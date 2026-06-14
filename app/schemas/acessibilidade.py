from typing import Any, Literal

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


class Paginacao(BaseModel):
    """Metadados de paginação do gráfico de métricas por escola."""

    page: int = Field(..., ge=0, description="Página atual (base 0).")
    page_size: int = Field(..., ge=1, description="Escolas por página.")
    total_escolas: int = Field(..., ge=0, description="Total de escolas no recorte.")
    total_paginas: int = Field(..., ge=0, description="Total de páginas disponíveis.")


class PainelData(BaseModel):
    graficos: dict[str, Grafico] = Field(
        ...,
        description="Mapa de gráficos do painel, indexados por chave semântica.",
    )


class PainelResponse(BaseModel):
    """Resposta do painel: descrição + bloco de dados com gráficos e filtros."""

    descricao: str = Field(..., description="Identificador semântico do painel.")
    data: PainelData


class PainelEscolasData(BaseModel):
    grafico: Grafico = Field(..., description="Gráfico de métricas por escola (página atual).")
    paginacao: Paginacao = Field(..., description="Metadados de paginação.")


class PainelEscolasResponse(BaseModel):
    """Resposta paginada do gráfico de métricas por escola."""

    descricao: str = Field(..., description="Identificador semântico do recurso.")
    data: PainelEscolasData


class MapaPonto(BaseModel):
    """Escola georreferenciada com score e classificação de acessibilidade."""

    co_entidade: int
    no_entidade: str
    no_municipio: str | None
    no_bairro: str | None
    latitude: float
    longitude: float
    no_tp_dependencia: str | None
    no_tp_localizacao: str | None
    score_acessibilidade: int = Field(..., ge=0, le=11)
    classificacao_acessibilidade: Literal["Boa", "Média", "Baixa", "Inexistente"]


class MapaData(BaseModel):
    pontos: list[MapaPonto]


class MapaResponse(BaseModel):
    """Resposta do mapa: descrição + lista de pontos georreferenciados."""

    descricao: str = Field(..., description="Identificador semântico do mapa.")
    data: MapaData


class AnaliseTemporalData(BaseModel):
    graficos: dict[str, Grafico] = Field(
        ...,
        description="Mapa de gráficos da análise temporal, indexados por chave semântica.",
    )


class AnaliseTemporalResponse(BaseModel):
    """Resposta da análise temporal por tipo de localização."""

    descricao: str = Field(..., description="Identificador semântico do recurso.")
    data: AnaliseTemporalData
