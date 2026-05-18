from dataclasses import dataclass


@dataclass(frozen=True)
class AcessibilidadeMunicipio:
    """
    Percentual de escolas por município com a métrica de acessibilidade
    selecionada = 1, sobre o total de escolas do município no recorte
    (ano + filtros de rede/localização).

    Fonte: silver.fato_acessibilidade + silver.dim_entidade +
    silver.dim_municipio. Valor de `percentual` em 0.0 - 100.0, com 2 casas.
    """

    codigo_municipio: int
    municipio: str
    percentual: float


@dataclass(frozen=True)
class AcessibilidadeTemporal:
    """
    Percentual de escolas com a métrica de acessibilidade selecionada, por
    (ano censo, tipo de localização). Alimenta o gráfico de evolução temporal
    por tipo de localização (urbana/rural).

    Fonte: silver.fato_acessibilidade + silver.dim_entidade +
    silver.dim_tp_localizacao.
    """

    ano: int
    codigo_localizacao: int
    localizacao: str
    percentual: float


@dataclass(frozen=True)
class AcessibilidadeMapaPonto:
    """
    Ponto georreferenciado de uma escola com score e classificação de
    acessibilidade calculados em SQL.

    Fonte: silver.fato_acessibilidade + dimensões (entidade, município,
    tp_dependencia, tp_localizacao). Granularidade: uma linha por escola
    por ano censo. Apenas escolas com latitude/longitude não nulas.
    """

    co_entidade: int
    no_entidade: str
    no_municipio: str | None
    no_bairro: str | None
    latitude: float
    longitude: float
    no_tp_dependencia: str | None
    no_tp_localizacao: str | None
    score_acessibilidade: int
    classificacao_acessibilidade: str

# P1G4
@dataclass(frozen=True)
class TotalEscolas:
    """
    Quantidade total de escolas que atendem aos filtros selecionados e possuem
    o recurso de acessibilidade física ativo (=1). Alimenta o card KPI de 
    destaque no topo do painel

    Fonte: silver.fato_acessibilidade + silver.dim_entidade.
    Granularidade: Um único valor numérico interiro
    """

    total: int
