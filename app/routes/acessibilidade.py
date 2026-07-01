from typing import Literal

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_acessibilidade_service
from app.schemas.acessibilidade import (
    AnaliseTemporalResponse,
    MapaResponse,
    PainelEscolasResponse,
    PainelResponse,
)
from app.services.acessibilidade_service import AcessibilidadeService

router = APIRouter(prefix="/acessibilidade", tags=["acessibilidade"])


# Variáveis dos painéis (gold) — as 15 métricas do notebook. Usadas em /painel,
# /painel/escolas e /analise-temporal.
VariavelAcessibilidade = Literal[
    "in_acessibilidade_rampas",
    "in_acessibilidade_corrimao",
    "in_acessibilidade_elevador",
    "in_acessibilidade_pisos_tateis",
    "in_acessibilidade_vao_livre",
    "qt_salas_utilizadas_acessiveis",
    "in_acessibilidade_inexistente",
    "in_acessibilidade_sinal_tatil",
    "in_acessibilidade_sinal_sonoro",
    "in_acessibilidade_sinal_visual",
    "tp_aee",
    "in_sala_atendimento_especial",
    "in_reserva_pcd",
    "qt_prof_psicologo",
    "qt_prof_assist_social",
]

# Variáveis do mapa — as 15 métricas gold de gold.fato_score_acessibilidade.
# Usadas só como filtro AND opcional do /mapa.
VariavelAcessibilidadeMapa = Literal[
    "in_acessibilidade_rampas",
    "in_acessibilidade_corrimao",
    "in_acessibilidade_elevador",
    "in_acessibilidade_pisos_tateis",
    "in_acessibilidade_vao_livre",
    "qt_salas_utilizadas_acessiveis",
    "in_acessibilidade_inexistente",
    "in_acessibilidade_sinal_tatil",
    "in_acessibilidade_sinal_sonoro",
    "in_acessibilidade_sinal_visual",
    "tp_aee",
    "in_sala_atendimento_especial",
    "in_reserva_pcd",
    "qt_prof_psicologo",
    "qt_prof_assist_social",
]

RedeEnsino = Literal["Federal", "Estadual", "Municipal", "Privada"]
TpLocalizacao = Literal["Urbana", "Rural"]


@router.get(
    "/painel",
    response_model=PainelResponse,
    summary="Painel de acessibilidade (gráfico + filtros disponíveis)",
)
async def get_painel_acessibilidade(
    ano: int | None = Query(
        None,
        description="Ano do censo escolar (ex: 2023). Se omitido, agrega todos os censos.",
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
    variaveis: list[VariavelAcessibilidade] | None = Query(
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
    service: AcessibilidadeService = Depends(get_acessibilidade_service),
) -> PainelResponse:
    """Retorna o painel completo: gráfico tab_percent (barras horizontais por
    município para a métrica escolhida) + opções de filtro (municípios, anos
    e métricas) para popular dropdowns do frontend."""
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
    summary="Gráfico paginado de métricas de acessibilidade por escola",
)
async def get_painel_escolas_acessibilidade(
    ano: int | None = Query(
        None,
        description="Ano do censo escolar (ex: 2023). Se omitido, usa o censo mais recente de cada escola.",
    ),
    municipios: list[str] | None = Query(
        None,
        max_length=4,
        description="Lista de municípios (até 4). Use o parâmetro repetido.",
    ),
    variaveis: list[VariavelAcessibilidade] | None = Query(
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
    service: AcessibilidadeService = Depends(get_acessibilidade_service),
) -> PainelEscolasResponse:
    """Retorna uma página do gráfico de métricas por escola (barras empilhadas,
    ordenado por score DESC) + metadados de paginação. Pensado para o frontend
    navegar as demais escolas sem reprocessar o painel inteiro."""
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
        descricao="painel_acessibilidade_escolas",
        data=resultado,
    )


@router.get(
    "/mapa",
    response_model=MapaResponse,
    summary="Escolas com score e classificação de acessibilidade pré-computados",
)
async def get_mapa_acessibilidade(
    ano: int | None = Query(
        None,
        description="Ano do censo escolar (nu_ano_censo). Se omitido, retorna todos os anos.",
    ),
    variaveis: list[VariavelAcessibilidadeMapa] | None = Query(
        None,
        description=(
            "Filtro AND: a escola precisa ter TODAS as variáveis marcadas > 0. "
            "Conjunto das 15 métricas gold. Use o parâmetro repetido: "
            "?variaveis=in_acessibilidade_rampas&variaveis=in_acessibilidade_elevador."
        ),
    ),
    pibid: bool | None = Query(
        None,
        description=(
            "Filtra escolas por participação no PIBID. true = só com PIBID; "
            "false = só sem PIBID; omitido = todas."
        ),
    ),
    service: AcessibilidadeService = Depends(get_acessibilidade_service),
) -> MapaResponse:
    """Retorna as linhas de gold.fato_score_acessibilidade (uma por escola por
    ano censo) com as 15 métricas e o score (0-15) e classificação
    (Excelente/Boa/Média/Baixa/Inexistente) já pré-computados pelo pipeline de dados."""
    envelope = await service.build_mapa(ano=ano, variaveis=variaveis, pibid=pibid)
    return MapaResponse(**envelope)


@router.get(
    "/analise-temporal",
    response_model=AnaliseTemporalResponse,
    summary="Evolução temporal da acessibilidade (por localização e por dependência)",
)
async def get_analise_temporal_acessibilidade(
    metrica: VariavelAcessibilidade = Query(
        "in_acessibilidade_rampas",
        description="Métrica de acessibilidade a plotar nos dois gráficos.",
    ),
    pibid: bool | None = Query(
        None,
        description=(
            "Filtra escolas por participação no PIBID. true = só com PIBID; "
            "false = só sem PIBID; omitido = todas."
        ),
    ),
    service: AcessibilidadeService = Depends(get_acessibilidade_service),
) -> AnaliseTemporalResponse:
    """Retorna os gráficos de evolução temporal: por tipo de localização
    (uma linha por urbana/rural) e por tipo de dependência administrativa
    (uma linha por Federal/Estadual/Municipal/Privada), ambos ao longo
    dos anos censo + opções de filtro de métrica para popular dropdowns
    do frontend."""
    envelope = await service.build_analise_temporal(metrica=metrica, pibid=pibid)
    return AnaliseTemporalResponse(**envelope)
