from typing import Literal

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_infraestrutura_service
from app.schemas.infraestrutura import (
    AnaliseTemporalResponse,
    MapaResponse,
    PainelEscolasResponse,
    PainelResponse,
)
from app.services.infraestrutura_service import InfraestruturaService

router = APIRouter(prefix="/infraestrutura", tags=["infraestrutura"])


# As 17 métricas curadas do notebook (cell-1). Usadas em /painel, /painel/escolas,
# /mapa e /analise-temporal (fonte: silver.infraestrutura_comum).
VariavelInfraestrutura = Literal[
    "in_agua_potavel",
    "in_energia_rede_publica",
    "in_esgoto_rede_publica",
    "in_lixo_servico_coleta",
    "in_banheiro",
    "in_banheiro_pne",
    "in_biblioteca",
    "in_sala_leitura",
    "in_laboratorio_ciencias",
    "in_laboratorio_informatica",
    "in_sala_multiuso",
    "in_sala_atendimento_especial",
    "in_cozinha",
    "in_refeitorio",
    "in_quadra_esportes",
    "in_patio_coberto",
    "in_auditorio",
]

RedeEnsino = Literal["Federal", "Estadual", "Municipal", "Privada"]
TpLocalizacao = Literal["Urbana", "Rural"]


@router.get(
    "/painel",
    response_model=PainelResponse,
    summary="Painel de infraestrutura (gráficos + cards)",
)
async def get_painel_infraestrutura(
    ano: int | None = Query(
        None,
        description="Ano do censo escolar (ex: 2024). Se omitido, agrega todos os censos.",
    ),
    municipios: list[str] | None = Query(
        None,
        max_length=4,
        description=(
            "Lista de municípios (até 4). Use o parâmetro repetido: "
            "?municipios=Belém&municipios=Ananindeua. "
            "Se omitido, o tab_percent cobre todos os municípios do recorte."
        ),
    ),
    variaveis: list[VariavelInfraestrutura] | None = Query(
        None,
        description=(
            "Filtro AND: escolas precisam ter TODAS as variáveis marcadas = 1."
        ),
    ),
    rede_ensino: list[RedeEnsino] | None = Query(
        None,
        description="Rede(s) de ensino: Federal, Estadual, Municipal, Privada.",
    ),
    tp_localizacao: list[TpLocalizacao] | None = Query(
        None,
        description="Localização da escola: Urbana ou Rural.",
    ),
    pibid: bool | None = Query(
        None,
        description=(
            "Filtra escolas por participação no PIBID. true = só com PIBID; "
            "false = só sem PIBID; omitido = todas."
        ),
    ),
    service: InfraestruturaService = Depends(get_infraestrutura_service),
) -> PainelResponse:
    """Retorna o painel completo de infraestrutura: cards de total de escolas,
    tab_percent (barras horizontais por município), barras por dependência e
    por tipo de localização para a(s) métrica(s) escolhida(s)."""
    envelope = await service.build_painel(
        ano=ano,
        municipios=municipios,
        rede_ensino=rede_ensino,
        tp_localizacao=tp_localizacao,
        variaveis=variaveis,
        pibid=pibid,
    )
    return PainelResponse(**envelope)


@router.get(
    "/painel/escolas",
    response_model=PainelEscolasResponse,
    summary="Gráfico paginado de métricas de infraestrutura por escola",
)
async def get_painel_escolas_infraestrutura(
    ano: int | None = Query(
        None,
        description="Ano do censo escolar (ex: 2024). Se omitido, usa o censo mais recente de cada escola.",
    ),
    municipios: list[str] | None = Query(
        None,
        max_length=4,
        description="Lista de municípios (até 4). Use o parâmetro repetido.",
    ),
    variaveis: list[VariavelInfraestrutura] | None = Query(
        None,
        description="Filtro AND: escolas precisam ter TODAS as variáveis marcadas = 1.",
    ),
    rede_ensino: list[RedeEnsino] | None = Query(
        None,
        description="Rede(s) de ensino: Federal, Estadual, Municipal, Privada.",
    ),
    tp_localizacao: list[TpLocalizacao] | None = Query(
        None,
        description="Localização da escola: Urbana ou Rural.",
    ),
    pibid: bool | None = Query(
        None,
        description=(
            "Filtra escolas por participação no PIBID. true = só com PIBID; "
            "false = só sem PIBID; omitido = todas."
        ),
    ),
    page: int = Query(0, ge=0, description="Página (base 0)."),
    page_size: int = Query(5, ge=1, le=50, description="Escolas por página (1–50)."),
    service: InfraestruturaService = Depends(get_infraestrutura_service),
) -> PainelEscolasResponse:
    """Retorna uma página do gráfico de métricas por escola (barras empilhadas,
    ordenado por score DESC) + metadados de paginação."""
    resultado = await service.build_painel_escolas(
        ano=ano,
        municipios=municipios,
        rede_ensino=rede_ensino,
        tp_localizacao=tp_localizacao,
        variaveis=variaveis,
        pibid=pibid,
        page=page,
        page_size=page_size,
    )
    return PainelEscolasResponse(
        descricao="painel_infraestrutura_escolas",
        data=resultado,
    )


@router.get(
    "/mapa",
    response_model=MapaResponse,
    summary="Escolas com score e classificação de infraestrutura (on-the-fly)",
)
async def get_mapa_infraestrutura(
    ano: int | None = Query(
        None,
        description="Ano do censo escolar (nu_ano_censo). Se omitido, retorna todos os anos.",
    ),
    variaveis: list[VariavelInfraestrutura] | None = Query(
        None,
        description=(
            "Filtro AND: a escola precisa ter TODAS as variáveis marcadas > 0. "
            "Use o parâmetro repetido: ?variaveis=in_agua_potavel&variaveis=in_biblioteca."
        ),
    ),
    pibid: bool | None = Query(
        None,
        description=(
            "Filtra escolas por participação no PIBID. true = só com PIBID; "
            "false = só sem PIBID; omitido = todas."
        ),
    ),
    service: InfraestruturaService = Depends(get_infraestrutura_service),
) -> MapaResponse:
    """Retorna as escolas de silver.infraestrutura_comum (uma por escola por ano
    censo) com as 17 métricas e o score (0–17) e classificação
    (Boa/Média/Baixa/Inexistente) calculados on-the-fly — não há tabela de score
    pré-computada na camada gold para infraestrutura."""
    envelope = await service.build_mapa(ano=ano, variaveis=variaveis, pibid=pibid)
    return MapaResponse(**envelope)


@router.get(
    "/analise-temporal",
    response_model=AnaliseTemporalResponse,
    summary="Evolução temporal da infraestrutura (por localização e por dependência)",
)
async def get_analise_temporal_infraestrutura(
    metrica: VariavelInfraestrutura = Query(
        "in_agua_potavel",
        description="Métrica de infraestrutura a plotar nos dois gráficos.",
    ),
    pibid: bool | None = Query(
        None,
        description=(
            "Filtra escolas por participação no PIBID. true = só com PIBID; "
            "false = só sem PIBID; omitido = todas."
        ),
    ),
    service: InfraestruturaService = Depends(get_infraestrutura_service),
) -> AnaliseTemporalResponse:
    """Retorna os gráficos de evolução temporal: por tipo de localização
    (uma linha por urbana/rural) e por tipo de dependência administrativa
    (uma linha por Federal/Estadual/Municipal/Privada), ambos ao longo
    dos anos censo."""
    envelope = await service.build_analise_temporal(metrica=metrica, pibid=pibid)
    return AnaliseTemporalResponse(**envelope)
