from dataclasses import dataclass

# TotalEscolas é genérico (apenas um inteiro) — reaproveitado de acessibilidade
# em vez de duplicar.
from app.domain.acessibilidade import TotalEscolas

__all__ = [
    "ConectividadeMunicipio",
    "ConectividadeTemporal",
    "TotalEscolas",
    "ConectividadeDependencia",
    "ConectividadeLocalizacao",
    "ConectividadeEscola",
    "ConectividadeTemporalDependencia",
]


@dataclass(frozen=True)
class ConectividadeMunicipio:
    """
    Percentual de escolas por município que possuem a(s) métrica(s) de
    conectividade selecionada(s), sobre o total de escolas do município no
    recorte (ano + filtros de rede/localização).

    Fonte: gold.fato_conectividade + gold.dim_entidade +
    gold.dim_municipio. Valor de `percentual` em 0.0 - 100.0, com 2 casas.
    """

    codigo_municipio: int
    municipio: str
    percentual: float
    total_escolas: int


@dataclass(frozen=True)
class ConectividadeTemporal:
    """
    Percentual de escolas com a métrica de conectividade selecionada, por
    (ano censo, tipo de localização). Alimenta o gráfico de evolução temporal
    por tipo de localização (urbana/rural).

    Fonte: gold.fato_conectividade + gold.dim_entidade +
    gold.dim_tp_localizacao.
    """

    ano: int
    codigo_localizacao: int
    localizacao: str
    percentual: float


@dataclass(frozen=True)
class ConectividadeDependencia:
    """
    Percentual de escolas por tipo de dependência administrativa com a métrica
    de conectividade selecionada = 1, sobre o total de escolas daquela
    dependência no recorte filtrado.

    Fonte: gold.fato_conectividade + gold.dim_entidade + gold.dim_tp_dependencia.
    """

    codigo_dependencia: int
    dependencia: str
    percentual: float
    total_escolas: int


@dataclass(frozen=True)
class ConectividadeLocalizacao:
    """
    Percentual de escolas por tipo de localização (Urbana/Rural) com a métrica
    de conectividade selecionada = 1, sobre o total de escolas daquela
    localização no recorte filtrado.

    Fonte: gold.fato_conectividade + gold.dim_entidade +
    gold.dim_tp_localizacao.
    """

    codigo_localizacao: int
    localizacao: str
    percentual: float
    total_escolas: int


@dataclass(frozen=True)
class ConectividadeEscola:
    """
    Uma escola com o valor (0/1) de cada uma das 17 métricas de
    conectividade e o score (soma das 17). Quando o filtro de `ano` não é
    informado, representa o censo mais recente disponível para a escola.

    Fonte: gold.fato_conectividade + gold.dim_entidade. Alimenta o
    gráfico de barras empilhadas "Métricas de conectividade por escola"
    do painel.
    """

    co_entidade: int
    no_entidade: str
    nu_ano_censo: int
    metricas: dict[str, int]
    score: int


@dataclass(frozen=True)
class ConectividadeTemporalDependencia:
    """
    Percentual de escolas com a métrica de conectividade selecionada,
    por (ano censo, tipo de dependência administrativa). Alimenta o
    gráfico de evolução temporal por dependência no endpoint
    /analise-temporal.

    Fonte: gold.fato_conectividade + gold.dim_entidade +
    gold.dim_tp_dependencia.
    """

    ano: int
    codigo_dependencia: int
    dependencia: str
    percentual: float
