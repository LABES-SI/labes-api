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
