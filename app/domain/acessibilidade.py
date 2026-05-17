from dataclasses import dataclass


@dataclass(frozen=True)
class AcessibilidadeMunicipio:
    """
    Percentual de escolas por município que possuem cada recurso de
    acessibilidade física, para um dado ano censo.

    Fonte: silver.acessibilidade (owner: squad de dados).
    Valores são percentuais (0.0 - 100.0), já arredondados para 1 casa.
    """

    municipio: str
    in_acessibilidade_rampas: float
    in_acessibilidade_corrimao: float
    in_acessibilidade_elevador: float
    in_acessibilidade_pisos_tateis: float
    in_acessibilidade_vao_livre: float
    in_banheiro_pne: float


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
