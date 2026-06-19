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
    """Linha de gold.fato_score_acessibilidade: escola por ano censo com as 15
    métricas e score/classificação de acessibilidade já pré-computados."""

    co_entidade: int
    nu_ano_censo: int
    pibid: int | None
    in_acessibilidade_rampas: float
    in_acessibilidade_corrimao: float
    in_acessibilidade_elevador: float
    in_acessibilidade_pisos_tateis: float
    in_acessibilidade_vao_livre: float
    in_acessibilidade_inexistente: float
    in_acessibilidade_sinal_tatil: float
    in_acessibilidade_sinal_sonoro: float
    in_acessibilidade_sinal_visual: float
    in_sala_atendimento_especial: float
    in_reserva_pcd: float
    qt_salas_utilizadas_acessiveis: float
    tp_aee: float
    qt_prof_psicologo: float
    qt_prof_assist_social: float
    score_acessibilidade: int = Field(..., ge=0, le=15)
    classificacao_acessibilidade: Literal["Boa", "Média", "Baixa", "Inexistente"]
    dt_carga: str | None


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
