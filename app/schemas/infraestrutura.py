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
    """Escola por ano censo com as 17 métricas de infraestrutura e o score/
    classificação calculados on-the-fly a partir de silver.infraestrutura_comum
    (não há tabela pré-computada gold, notebook cell-9).

    O `score_infraestrutura` é a soma binária das 17 métricas (0–17). A
    classificação segue as faixas do notebook (`classificar_infraestrutura`) e,
    diferente dos outros painéis, NÃO tem faixa "Excelente"."""

    co_entidade: int
    nu_ano_censo: int
    pibid: int | None
    in_agua_potavel: float
    in_energia_rede_publica: float
    in_esgoto_rede_publica: float
    in_lixo_servico_coleta: float
    in_banheiro: float
    in_banheiro_pne: float
    in_biblioteca: float
    in_sala_leitura: float
    in_laboratorio_ciencias: float
    in_laboratorio_informatica: float
    in_sala_multiuso: float
    in_sala_atendimento_especial: float
    in_cozinha: float
    in_refeitorio: float
    in_quadra_esportes: float
    in_patio_coberto: float
    in_auditorio: float
    score_infraestrutura: int = Field(..., ge=0, le=17)
    classificacao_infraestrutura: Literal["Boa", "Média", "Baixa", "Inexistente"]


class MapaData(BaseModel):
    pontos: list[MapaPonto]


class MapaResponse(BaseModel):
    """Resposta do mapa: descrição + lista de pontos com score/classificação."""

    descricao: str = Field(..., description="Identificador semântico do mapa.")
    data: MapaData


class AnaliseTemporalResponse(BaseModel):
    """Resposta da análise temporal por tipo de localização e dependência."""

    descricao: str = Field(..., description="Identificador semântico do recurso.")
    data: AnaliseTemporalData


class IntegridadeEscolaMunicipio(BaseModel):
    school_id: int | None = None
    year: int
    issue: Literal["duplicate_school_year", "invalid_indicator", "missing_school_id"]
    indicator: str | None = None


class EscolaMunicipioAnoExperimental(BaseModel):
    year: int
    school_id: int
    municipality_code: int | None
    municipality_name: str | None
    n_selected_indicators: int
    n_valid_indicators: int | None
    n_yes: int | None
    n_no: int | None
    n_null: int | None
    n_invalid_indicators: int | None
    coverage_exact: str | None
    eligible_for_comparison: bool | None
    school_index_pct_exact: str | None
    index_status: Literal[
        "complete",
        "partial",
        "observada_sem_indicadores_validos",
        "nao_observada",
        "entrada_invalida",
        "duplicidade_escola_ano",
    ]
    n_comparable_schools: int | None
    municipal_mean_excluding_school_pct_exact: str | None
    difference_pp_exact: str | None
    reference_status: Literal[
        "available",
        "sem_comparadoras",
        "comparadora_unica",
        "integridade_referencia",
        "territorio_pendente",
        "nao_avaliada",
    ]
    unavailability_reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    integrity_issues: list[IntegridadeEscolaMunicipio] = Field(default_factory=list)


class EscolaMunicipioDataExperimental(BaseModel):
    status: Literal["experimental_nao_homologado"]
    methodology_version: str
    indicator_set_version: str
    indicator_set_homologated: Literal[False]
    records: list[EscolaMunicipioAnoExperimental]


class EscolaMunicipioResponseExperimental(BaseModel):
    descricao: str
    data: EscolaMunicipioDataExperimental
