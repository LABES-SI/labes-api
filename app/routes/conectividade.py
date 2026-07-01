from typing import Literal

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_conectividade_service
from app.schemas.conectividade import (
    AnaliseTemporalResponse,
    MapaResponse,
    PainelEscolasResponse,
    PainelResponse,
)
from app.services.conectividade_service import ConectividadeService

router = APIRouter(prefix="/conectividade", tags=["conectividade"])


# Variáveis dos painéis (gold) — as 17 métricas do notebook. Usadas em /painel,
# /painel/escolas e /analise-temporal.
VariavelConectividade = Literal[
    "in_internet",
    "in_internet_alunos",
    "in_internet_administrativo",
    "in_internet_aprendizagem",
    "in_internet_comunidade",
    "in_banda_larga",
    "in_acesso_internet_computador",
    "in_aces_internet_disp_pessoais",
    "tp_rede_local",
    "in_computador",
    "in_desktop_aluno",
    "qt_desktop_aluno",
    "in_comp_portatil_aluno",
    "qt_comp_portatil_aluno",
    "in_tablet_aluno",
    "qt_tablet_aluno",
    "in_redes_sociais",
]

# Variáveis do mapa — as 17 métricas gold de gold.fato_score_conectividade.
# Usadas só como filtro AND opcional do /mapa.
VariavelConectividadeMapa = Literal[
    "in_internet",
    "in_internet_alunos",
    "in_internet_administrativo",
    "in_internet_aprendizagem",
    "in_internet_comunidade",
    "in_banda_larga",
    "in_acesso_internet_computador",
    "in_aces_internet_disp_pessoais",
    "tp_rede_local",
    "in_computador",
    "in_desktop_aluno",
    "qt_desktop_aluno",
    "in_comp_portatil_aluno",
    "qt_comp_portatil_aluno",
    "in_tablet_aluno",
    "qt_tablet_aluno",
    "in_redes_sociais",
]

RedeEnsino = Literal["Federal", "Estadual", "Municipal", "Privada"]
TpLocalizacao = Literal["Urbana", "Rural"]


@router.get(
    "/painel",
    response_model=PainelResponse,
    summary="Painel de conectividade (gráficos + cards)",
)
async def get_painel_conectividade(
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
    variaveis: list[VariavelConectividade] | None = Query(
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
    service: ConectividadeService = Depends(get_conectividade_service),
) -> PainelResponse:
    """Retorna o painel completo de conectividade: cards de total de escolas,
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
    summary="Gráfico paginado de métricas de conectividade por escola",
)
async def get_painel_escolas_conectividade(
    ano: int | None = Query(
        None,
        description="Ano do censo escolar (ex: 2024). Se omitido, usa o censo mais recente de cada escola.",
    ),
    municipios: list[str] | None = Query(
        None,
        max_length=4,
        description="Lista de municípios (até 4). Use o parâmetro repetido.",
    ),
    variaveis: list[VariavelConectividade] | None = Query(
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
    service: ConectividadeService = Depends(get_conectividade_service),
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
        descricao="painel_conectividade_escolas",
        data=resultado,
    )


@router.get(
    "/mapa",
    response_model=MapaResponse,
    summary="Escolas com score e classificação de conectividade pré-computados",
)
async def get_mapa_conectividade(
    ano: int | None = Query(
        None,
        description="Ano do censo escolar (nu_ano_censo). Se omitido, retorna todos os anos.",
    ),
    variaveis: list[VariavelConectividadeMapa] | None = Query(
        None,
        description=(
            "Filtro AND: a escola precisa ter TODAS as variáveis marcadas > 0. "
            "Conjunto das 17 métricas gold. Use o parâmetro repetido: "
            "?variaveis=in_internet&variaveis=in_banda_larga."
        ),
    ),
    pibid: bool | None = Query(
        None,
        description=(
            "Filtra escolas por participação no PIBID. true = só com PIBID; "
            "false = só sem PIBID; omitido = todas."
        ),
    ),
    service: ConectividadeService = Depends(get_conectividade_service),
) -> MapaResponse:
    """Retorna as linhas de gold.fato_score_conectividade (uma por escola por
    ano censo) com as 17 métricas e o score e classificação
    (Excelente/Boa/Média/Baixa/Inexistente) já pré-computados pelo pipeline de dados. O
    score pré-computado não é binário (colunas qt_* somam quantidade), então
    excede 17."""
    envelope = await service.build_mapa(ano=ano, variaveis=variaveis, pibid=pibid)
    return MapaResponse(**envelope)


@router.get(
    "/analise-temporal",
    response_model=AnaliseTemporalResponse,
    summary="Evolução temporal da conectividade (por localização e por dependência)",
)
async def get_analise_temporal_conectividade(
    metrica: VariavelConectividade = Query(
        "in_internet",
        description="Métrica de conectividade a plotar nos dois gráficos.",
    ),
    pibid: bool | None = Query(
        None,
        description=(
            "Filtra escolas por participação no PIBID. true = só com PIBID; "
            "false = só sem PIBID; omitido = todas."
        ),
    ),
    service: ConectividadeService = Depends(get_conectividade_service),
) -> AnaliseTemporalResponse:
    """Retorna os gráficos de evolução temporal: por tipo de localização
    (uma linha por urbana/rural) e por tipo de dependência administrativa
    (uma linha por Federal/Estadual/Municipal/Privada), ambos ao longo
    dos anos censo."""
    envelope = await service.build_analise_temporal(metrica=metrica, pibid=pibid)
    return AnaliseTemporalResponse(**envelope)
