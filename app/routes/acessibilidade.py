from typing import Literal

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_acessibilidade_service
from app.schemas.acessibilidade import AnaliseTemporalResponse, PainelResponse
from app.services.acessibilidade_service import AcessibilidadeService

router = APIRouter(prefix="/acessibilidade", tags=["acessibilidade"])


MetricaAcessibilidade = Literal[
    "rampas",
    "corrimao",
    "elevador",
    "pisos_tateis",
    "vao_livre",
    "banheiro_pne",
]


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
    metrica: MetricaAcessibilidade = Query(
        "banheiro_pne",
        description=(
            "Métrica de acessibilidade a plotar. Valores aceitos: "
            "rampas, corrimao, elevador, pisos_tateis, vao_livre, banheiro_pne."
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
        metrica=metrica,
    )
    return PainelResponse(**envelope)


@router.get(
    "/analise-temporal",
    response_model=AnaliseTemporalResponse,
    summary="Evolução temporal da acessibilidade por tipo de localização",
)
async def get_analise_temporal_acessibilidade(
    metrica: MetricaAcessibilidade = Query(
        "rampas",
        description=(
            "Métrica de acessibilidade a plotar. Valores aceitos: "
            "rampas, corrimao, elevador, pisos_tateis, vao_livre, banheiro_pne."
        ),
    ),
    service: AcessibilidadeService = Depends(get_acessibilidade_service),
) -> AnaliseTemporalResponse:
    """Retorna o gráfico de evolução temporal por tipo de localização
    (uma linha por urbana/rural ao longo dos anos censo) + opções de
    filtro de métrica para popular dropdowns do frontend."""
    envelope = await service.build_analise_temporal(metrica=metrica)
    return AnaliseTemporalResponse(**envelope)
