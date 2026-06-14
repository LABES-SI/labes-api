from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_filtros_service
from app.schemas.filtros import FiltrosResponse
from app.services.filtros_service import FiltrosService, PainelDisponivel

router = APIRouter(prefix="/filtros", tags=["filtros"])


@router.get(
    "",
    response_model=FiltrosResponse,
    summary="Filtros aplicáveis (genérico, compartilhável entre painéis)",
)
async def get_filtros(
    painel: PainelDisponivel | None = Query(
        None,
        description=(
            "Painel para incluir o catálogo de métricas (ex: acessibilidade). "
            "Se omitido, retorna apenas os filtros dimensionais."
        ),
    ),
    service: FiltrosService = Depends(get_filtros_service),
) -> FiltrosResponse:
    """Retorna as opções de filtro aplicáveis (municípios, anos, rede de ensino
    e tipo de localização) para popular dropdowns do frontend. Buscado uma única
    vez e reaproveitado por todos os painéis. Com `?painel=<nome>`, anexa as
    métricas específicas daquele painel."""
    envelope = await service.build_filtros(painel=painel.value if painel else None)
    return FiltrosResponse(**envelope)
