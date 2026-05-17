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
    rampas: float
    corrimao: float
    elevador: float
    pisos_tateis: float
    vao_livre: float
    banheiro_pne: float


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
