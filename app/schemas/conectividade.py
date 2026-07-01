from typing import Literal

from pydantic import BaseModel, Field

# Envelopes genéricos reaproveitados de acessibilidade (PlotlyFigure, Grafico,
# Paginacao e os blocos de dados são idênticos entre os painéis).
from app.schemas.acessibilidade import (
    AnaliseTemporalData,
    Grafico,
    Paginacao,
    PainelData,
)

__all__ = [
    "PainelData",
    "PainelResponse",
    "PainelEscolasData",
    "PainelEscolasResponse",
    "MapaPonto",
    "MapaData",
    "MapaResponse",
    "AnaliseTemporalData",
    "AnaliseTemporalResponse",
]


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
    """Linha de gold.fato_score_conectividade: escola por ano censo com as 17
    métricas e score/classificação de conectividade já pré-computados.

    O `score_conectividade` é o valor pré-computado pelo pipeline de dados — não
    é a soma binária das 17 métricas (colunas qt_* somam a quantidade), então
    excede 17 (observado até 26). Sem teto fixo no schema para não acoplar ao
    intervalo do mart, cujo cálculo é de responsabilidade da squad de dados."""

    co_entidade: int
    nu_ano_censo: int
    pibid: int | None
    in_internet: float
    in_internet_alunos: float
    in_internet_administrativo: float
    in_internet_aprendizagem: float
    in_internet_comunidade: float
    in_banda_larga: float
    in_acesso_internet_computador: float
    in_aces_internet_disp_pessoais: float
    tp_rede_local: float
    in_computador: float
    in_desktop_aluno: float
    qt_desktop_aluno: float
    in_comp_portatil_aluno: float
    qt_comp_portatil_aluno: float
    in_tablet_aluno: float
    qt_tablet_aluno: float
    in_redes_sociais: float
    score_conectividade: int = Field(..., ge=0)
    classificacao_conectividade: Literal["Boa", "Média", "Baixa", "Inexistente"]
    ideb_2023_anos_iniciais: float | None
    ideb_2023_anos_finais: float | None
    ideb_2023_ensino_medio: float | None
    ideb_2023_anos_iniciais_mun: float | None
    ideb_2023_anos_finais_mun: float | None
    ideb_2023_ensino_medio_mun: float | None
    dt_carga: str | None


class MapaData(BaseModel):
    pontos: list[MapaPonto]


class MapaResponse(BaseModel):
    """Resposta do mapa: descrição + lista de pontos georreferenciados."""

    descricao: str = Field(..., description="Identificador semântico do mapa.")
    data: MapaData


class AnaliseTemporalResponse(BaseModel):
    """Resposta da análise temporal por tipo de localização e dependência."""

    descricao: str = Field(..., description="Identificador semântico do recurso.")
    data: AnaliseTemporalData
