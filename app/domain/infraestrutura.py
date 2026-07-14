from dataclasses import dataclass

# TotalEscolas é genérico (apenas um inteiro) — reaproveitado de acessibilidade
# em vez de duplicar.
from app.domain.acessibilidade import TotalEscolas

__all__ = [
    "InfraestruturaMunicipio",
    "InfraestruturaTemporal",
    "TotalEscolas",
    "InfraestruturaDependencia",
    "InfraestruturaLocalizacao",
    "InfraestruturaEscola",
    "InfraestruturaTemporalDependencia",
]


@dataclass(frozen=True)
class InfraestruturaMunicipio:
    """
    Percentual de escolas por município que possuem a(s) métrica(s) de
    infraestrutura selecionada(s), sobre o total de escolas do município no
    recorte (ano + filtros de rede/localização).

    Fonte: silver.infraestrutura_comum (município já presente na silver via
    CO_MUNICIPIO/NO_MUNICIPIO). Valor de `percentual` em 0.0 - 100.0, com 2 casas.
    """

    codigo_municipio: int
    municipio: str
    percentual: float
    total_escolas: int


@dataclass(frozen=True)
class InfraestruturaTemporal:
    """
    Percentual de escolas com a métrica de infraestrutura selecionada, por
    (ano censo, tipo de localização). Alimenta o gráfico de evolução temporal
    por tipo de localização (urbana/rural).

    Fonte: silver.infraestrutura_comum + gold.dim_tp_localizacao.
    """

    ano: int
    codigo_localizacao: int
    localizacao: str
    percentual: float


@dataclass(frozen=True)
class InfraestruturaDependencia:
    """
    Percentual de escolas por tipo de dependência administrativa com a métrica
    de infraestrutura selecionada = 1, sobre o total de escolas daquela
    dependência no recorte filtrado.

    Fonte: silver.infraestrutura_comum + gold.dim_tp_dependencia.
    """

    codigo_dependencia: int
    dependencia: str
    percentual: float
    total_escolas: int


@dataclass(frozen=True)
class InfraestruturaLocalizacao:
    """
    Percentual de escolas por tipo de localização (Urbana/Rural) com a métrica
    de infraestrutura selecionada = 1, sobre o total de escolas daquela
    localização no recorte filtrado.

    Fonte: silver.infraestrutura_comum + gold.dim_tp_localizacao.
    """

    codigo_localizacao: int
    localizacao: str
    percentual: float
    total_escolas: int


@dataclass(frozen=True)
class InfraestruturaEscola:
    """
    Uma escola com o valor (0/1) de cada uma das 17 métricas de
    infraestrutura e o score (soma das 17). Quando o filtro de `ano` não é
    informado, representa o censo mais recente disponível para a escola.

    Fonte: silver.infraestrutura_comum. Alimenta o gráfico de barras
    empilhadas "Métricas de infraestrutura por escola" do painel.
    """

    co_entidade: int
    no_entidade: str
    nu_ano_censo: int
    metricas: dict[str, int]
    score: int


@dataclass(frozen=True)
class InfraestruturaTemporalDependencia:
    """
    Percentual de escolas com a métrica de infraestrutura selecionada,
    por (ano censo, tipo de dependência administrativa). Alimenta o
    gráfico de evolução temporal por dependência no endpoint
    /analise-temporal.

    Fonte: silver.infraestrutura_comum + gold.dim_tp_dependencia.
    """

    ano: int
    codigo_dependencia: int
    dependencia: str
    percentual: float
