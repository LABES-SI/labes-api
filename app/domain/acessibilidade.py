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
