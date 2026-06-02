from typing import Literal

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_acessibilidade_service
from app.schemas.acessibilidade import (
    AnaliseTemporalResponse,
    MapaResponse,
    PainelResponse,
    IdebResponse,
)
from app.services.acessibilidade_service import AcessibilidadeService

router = APIRouter(prefix="/acessibilidade", tags=["acessibilidade"])


VariavelAcessibilidade = Literal[
    "in_banheiro_pne",
    "in_sala_atendimento_especial",
    "in_acessibilidade_rampas",
    "in_acessibilidade_corrimao",
    "in_acessibilidade_elevador",
    "in_acessibilidade_pisos_tateis",
    "in_acessibilidade_vao_livre",
    "in_acessibilidade_inexistente",
    "in_acessibilidade_sinal_tatil",
    "in_acessibilidade_sinal_sonoro",
    "in_acessibilidade_sinal_visual",
    "in_acessibilidade_sinalizacao",
    "in_prof_psicologo",
    "in_prof_trad_libras",
    "in_prof_revisor_braille",
    "in_prof_assist_social",
    "in_prof_fonaudiologo",
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
    )
    return PainelResponse(**envelope)


@router.get(
    "/mapa",
    response_model=MapaResponse,
    summary="Pontos georreferenciados de escolas com score de acessibilidade",
)
async def get_mapa_acessibilidade(
    ano: int | None = Query(
        None,
        description="Ano do censo escolar. Se omitido, retorna todos os anos.",
    ),
    municipios: list[str] | None = Query(
        None,
        description="Filtra por nome de município (parâmetro repetido).",
    ),
    variaveis: list[VariavelAcessibilidade] | None = Query(
        None,
        description=(
            "Filtro AND: a escola precisa ter TODAS as variáveis marcadas = 1. "
            "Use o parâmetro repetido: "
            "?variaveis=in_acessibilidade_rampas&variaveis=in_acessibilidade_elevador."
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
    service: AcessibilidadeService = Depends(get_acessibilidade_service),
) -> MapaResponse:
    """Retorna lista de escolas georreferenciadas (latitude/longitude) com
    score (0-11) e classificação (Boa/Média/Baixa/Inexistente) de
    acessibilidade calculados em SQL a partir de silver.fato_acessibilidade
    e dimensões associadas."""
    envelope = await service.build_mapa(
        ano=ano,
        municipios=municipios,
        variaveis=variaveis,
        rede_ensino=rede_ensino,
        tp_localizacao=tp_localizacao,
    )
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
    service: AcessibilidadeService = Depends(get_acessibilidade_service),
) -> AnaliseTemporalResponse:
    """Retorna os gráficos de evolução temporal: por tipo de localização
    (uma linha por urbana/rural) e por tipo de dependência administrativa
    (uma linha por Federal/Estadual/Municipal/Privada), ambos ao longo
    dos anos censo + opções de filtro de métrica para popular dropdowns
    do frontend."""
    envelope = await service.build_analise_temporal(metrica=metrica)
    return AnaliseTemporalResponse(**envelope)

@router.get(
    "/ideb",
    response_model=IdebResponse,
    summary="Cruzamento do Score de Acessibilidade vs Nota do IDEB",
)
async def get_cruzamento_ideb(
    ano: int | None = Query(
        None,
        description="Ano do censo escolar. Se omitido, retorna todos os anos.",
    ),
    municipios: list[str] | None = Query(
        None,
        description="Filtra por nome de município (parâmetro repetido).",
    ),
    variaveis: list[VariavelAcessibilidade] | None = Query(
        None,
        description="Filtro AND das variáveis de acessibilidade.",
    ),
    rede_ensino: list[RedeEnsino] | None = Query(
        None,
        description="Rede(s) de ensino: Federal, Estadual, Municipal, Privada.",
    ),
    tp_localizacao: list[TpLocalizacao] | None = Query(
        None,
        description="Localização da escola: Urbana ou Rural.",
    ),
    service: AcessibilidadeService = Depends(get_acessibilidade_service),
) -> IdebResponse:
    """Retorna gráfico de dispersão (scatter plot) cruzando o score de 
    acessibilidade com a nota estimada do IDEB (mockada para fins de homologação)."""
    
    grafico = await service.build_analise_ideb(
        ano=ano,
        municipios=municipios,
        variaveis=variaveis,
        rede_ensino=rede_ensino,
        tp_localizacao=tp_localizacao,
    )
    
    envelope = {
        "descricao": "cruzamento_ideb",
        "data": {
            "graficos": {
                "scatter_ideb": grafico
            }
        }
    }
    
    return IdebResponse(**envelope)
