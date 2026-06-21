"""Testes do ConectividadeService cobrindo TODOS os gráficos do painel.

Cada gráfico servido pela API é exercitado via service (com repositório falso,
sem banco) e validado no nível do payload Plotly: estrutura do envelope, tipo,
título, dados das traces, cores das métricas, score, paginação e propagação de
filtros para o repositório.

Gráficos cobertos:
  - build_painel: 2 cards (Indicator) + tab_percent + dependência + localização
  - build_painel_escolas: barras empilhadas por escola (17 métricas) + paginação
  - build_analise_temporal: evolução temporal por localização e por dependência
  - build_mapa: pontos pré-computados de gold.fato_score_conectividade
"""

import pytest

from app.services.conectividade_service import (
    ANALISE_TEMPORAL_DESCRICAO,
    COR_AUSENTE,
    MAPA_DESCRICAO,
    METRIC_ESCOLA_FIELDS,
    METRIC_FIELDS,
    PAINEL_DESCRICAO,
    ConectividadeService,
)
from tests.services.conftest import FakeConectividadeRepository, make_pontos_mapa


N_METRICAS = len(METRIC_ESCOLA_FIELDS)


# ---------------------------------------------------------------------------
# Sanidade do catálogo de métricas
# ---------------------------------------------------------------------------

def test_catalogo_tem_17_metricas_unicas():
    assert N_METRICAS == 17
    chaves = [c for c, *_ in METRIC_ESCOLA_FIELDS]
    assert len(set(chaves)) == 17
    # METRIC_FIELDS é derivado e bate com as chaves/labels.
    assert [c for c, _ in METRIC_FIELDS] == chaves


def test_todas_metricas_sao_infraestrutura():
    grupos = {grupo for *_, grupo in METRIC_ESCOLA_FIELDS}
    assert grupos == {"Infraestrutura"}


# ---------------------------------------------------------------------------
# build_painel — cards + tab_percent + dependência + localização
# ---------------------------------------------------------------------------

async def test_build_painel_estrutura_e_chaves(fake_repo_full):
    service = ConectividadeService(fake_repo_full)
    envelope = await service.build_painel(ano=2024, municipios=None)

    assert envelope["descricao"] == PAINEL_DESCRICAO
    graficos = envelope["data"]["graficos"]
    assert set(graficos) == {
        "card_total_escolas",
        "card_total_escolas_com_conectividade",
        "tab_percent_conectividade",
        "grafico_dependencia_conectividade",
        "grafico_tp_localizacao_conectividade",
    }
    # Todo gráfico tem o envelope tipo/titulo/plotly(data+layout).
    for g in graficos.values():
        assert {"tipo", "titulo", "plotly"} <= set(g)
        assert "data" in g["plotly"] and "layout" in g["plotly"]


async def test_painel_cards_sao_indicadores_com_totais(fake_repo_full):
    service = ConectividadeService(fake_repo_full)
    graficos = (await service.build_painel(ano=2024, municipios=None))["data"]["graficos"]

    card_geral = graficos["card_total_escolas"]
    card_com = graficos["card_total_escolas_com_conectividade"]
    assert card_geral["tipo"] == "indicator"
    assert card_com["tipo"] == "indicator"
    assert card_geral["plotly"]["data"][0]["value"] == 180  # total_geral
    assert card_com["plotly"]["data"][0]["value"] == 140     # total_com


async def test_painel_tab_percent_ordena_por_percentual_desc(fake_repo_full):
    service = ConectividadeService(fake_repo_full)
    graficos = (await service.build_painel(ano=2024, municipios=None))["data"]["graficos"]
    tab = graficos["tab_percent_conectividade"]

    assert tab["tipo"] == "bar"
    trace = tab["plotly"]["data"][0]
    # barra horizontal: y = municípios, x = percentuais (desc).
    assert list(trace["y"]) == ["Belém", "Ananindeua"]
    assert list(trace["x"]) == [80.0, 55.5]


async def test_painel_dependencia_e_localizacao_ordenadas_desc(fake_repo_full):
    service = ConectividadeService(fake_repo_full)
    graficos = (await service.build_painel(ano=2024, municipios=None))["data"]["graficos"]

    dep = graficos["grafico_dependencia_conectividade"]["plotly"]["data"][0]
    assert list(dep["x"]) == ["Federal", "Estadual", "Municipal"]
    assert list(dep["y"]) == [90.0, 70.0, 40.0]

    loc = graficos["grafico_tp_localizacao_conectividade"]["plotly"]["data"][0]
    assert list(loc["x"]) == ["Urbana", "Rural"]
    assert list(loc["y"]) == [75.0, 30.0]


async def test_painel_propaga_filtros_para_o_repositorio(fake_repo_full):
    service = ConectividadeService(fake_repo_full)
    await service.build_painel(
        ano=2024,
        municipios=["Belém"],
        rede_ensino=["Estadual"],
        tp_localizacao=["Urbana"],
        variaveis=["in_internet"],
        pibid=True,
    )
    chamada = fake_repo_full.calls["find_media_por_municipio"]
    assert chamada["ano"] == 2024
    assert chamada["municipios"] == ["Belém"]
    assert chamada["rede_ensino"] == ["Estadual"]
    assert chamada["tp_localizacao"] == ["Urbana"]
    assert chamada["pibid"] is True
    # variável única -> filtro AND (combine_or False).
    assert chamada["variaveis"] == ["in_internet"]
    assert chamada["combine_or"] is False


async def test_painel_sem_variaveis_usa_or_em_todas(fake_repo_full):
    service = ConectividadeService(fake_repo_full)
    await service.build_painel(ano=None, municipios=None, variaveis=None)
    chamada = fake_repo_full.calls["find_media_por_municipio"]
    assert chamada["combine_or"] is True
    assert set(chamada["variaveis"]) == {c for c, _ in METRIC_FIELDS}


async def test_painel_titulo_card_reflete_metrica_unica(fake_repo_full):
    service = ConectividadeService(fake_repo_full)
    graficos = (
        await service.build_painel(ano=2024, municipios=None, variaveis=["in_internet"])
    )["data"]["graficos"]
    titulo = graficos["card_total_escolas_com_conectividade"]["titulo"]
    assert "Conexão à Internet" in titulo
    assert "Censo 2024" in titulo


async def test_painel_variavel_invalida_levanta(fake_repo_full):
    service = ConectividadeService(fake_repo_full)
    with pytest.raises(ValueError):
        await service.build_painel(ano=2024, municipios=None, variaveis=["nao_existe"])


# ---------------------------------------------------------------------------
# build_painel_escolas — barras empilhadas (17 métricas) + paginação + hover
# ---------------------------------------------------------------------------

async def test_escolas_estrutura_e_paginacao(fake_repo_full):
    service = ConectividadeService(fake_repo_full)
    resultado = await service.build_painel_escolas(
        ano=2024, municipios=["Belém"], page=1, page_size=5
    )
    assert {"grafico", "paginacao"} == set(resultado)
    pag = resultado["paginacao"]
    assert pag == {
        "page": 1,
        "page_size": 5,
        "total_escolas": 12,       # total_escolas_count do fake
        "total_paginas": 3,        # ceil(12/5)
    }
    # offset = page * page_size foi passado ao repositório.
    chamada = fake_repo_full.calls["find_metricas_por_escola"]
    assert chamada["limit"] == 5
    assert chamada["offset"] == 5


async def test_escolas_uma_trace_de_barra_por_metrica(fake_repo_full):
    service = ConectividadeService(fake_repo_full)
    grafico = (await service.build_painel_escolas(ano=2024, municipios=None))["grafico"]
    assert grafico["tipo"] == "bar"
    data = grafico["plotly"]["data"]
    bar_traces = [t for t in data if t.get("type") == "bar"]
    # uma barra empilhada por métrica (17) + traces de legenda (scatter).
    assert len(bar_traces) == N_METRICAS
    # cada barra tem um slot por escola (3 escolas no fake).
    for t in bar_traces:
        assert list(t["x"]) == [1, 1, 1]


async def test_escolas_cor_presente_vs_ausente(fake_repo_full):
    service = ConectividadeService(fake_repo_full)
    grafico = (await service.build_painel_escolas(ano=2024, municipios=None))["grafico"]
    bar_traces = [t for t in grafico["plotly"]["data"] if t.get("type") == "bar"]

    # 1ª métrica do catálogo = in_internet, cor própria.
    chave0, _label0, cor0, _grupo0 = METRIC_ESCOLA_FIELDS[0]
    assert chave0 == "in_internet"
    cores = list(bar_traces[0]["marker"]["color"])
    # Escola A e B possuem in_internet (cor), Escola C também (todas têm).
    # No fake todas as 3 possuem in_internet -> todas coloridas.
    assert cores == [cor0, cor0, cor0]

    # Última métrica (in_redes_sociais): só Escola A possui -> 1 cor + 2 ausentes.
    chave_last, _l, cor_last, _g = METRIC_ESCOLA_FIELDS[-1]
    cores_last = list(bar_traces[-1]["marker"]["color"])
    assert cores_last == [cor_last, COR_AUSENTE, COR_AUSENTE]


async def test_escolas_anotacao_score_sobre_n_metricas(fake_repo_full):
    service = ConectividadeService(fake_repo_full)
    grafico = (await service.build_painel_escolas(ano=2024, municipios=None))["grafico"]
    annotations = grafico["plotly"]["layout"]["annotations"]
    textos = {a["text"] for a in annotations}
    # scores do fake: 17, 9, 1 sobre 17.
    assert f"17/{N_METRICAS}" in textos
    assert f"9/{N_METRICAS}" in textos
    assert f"1/{N_METRICAS}" in textos


async def test_escolas_hover_traz_pibid_e_ideb(fake_repo_full):
    service = ConectividadeService(fake_repo_full)
    grafico = (await service.build_painel_escolas(ano=2024, municipios=None))["grafico"]
    bar_traces = [t for t in grafico["plotly"]["data"] if t.get("type") == "bar"]
    # customdata da 1ª barra, 1ª escola (Escola A, co_entidade 101): PIBID + IDEB.
    cd_escola_a = bar_traces[0]["customdata"][0]
    # índices: [rotulo, possui, ano, subprojeto, bolsistas, ideb_texto]
    assert cd_escola_a[3] == "Matemática / Física"
    assert cd_escola_a[4] == 7
    assert "Anos Iniciais: 4.9" in cd_escola_a[5]


async def test_escolas_pagina_vazia(monkeypatch):
    repo = FakeConectividadeRepository(escolas=[], total_escolas_count=0)
    service = ConectividadeService(repo)
    resultado = await service.build_painel_escolas(ano=2024, municipios=None)
    assert resultado["paginacao"]["total_escolas"] == 0
    assert resultado["paginacao"]["total_paginas"] == 0
    assert "0 escolas" in resultado["grafico"]["titulo"]


# ---------------------------------------------------------------------------
# build_analise_temporal — evolução por localização e por dependência
# ---------------------------------------------------------------------------

async def test_temporal_estrutura_e_chaves(fake_repo_full):
    service = ConectividadeService(fake_repo_full)
    envelope = await service.build_analise_temporal(metrica="in_internet")
    assert envelope["descricao"] == ANALISE_TEMPORAL_DESCRICAO
    graficos = envelope["data"]["graficos"]
    assert set(graficos) == {
        "evolucao_temporal_por_localizacao",
        "evolucao_temporal_por_dependencia",
    }
    for g in graficos.values():
        assert g["tipo"] == "line"


async def test_temporal_uma_serie_por_categoria(fake_repo_full):
    service = ConectividadeService(fake_repo_full)
    graficos = (await service.build_analise_temporal(metrica="in_internet"))["data"]["graficos"]

    loc = graficos["evolucao_temporal_por_localizacao"]["plotly"]["data"]
    nomes_loc = {t["name"] for t in loc}
    assert nomes_loc == {"Urbana", "Rural"}

    dep = graficos["evolucao_temporal_por_dependencia"]["plotly"]["data"]
    nomes_dep = {t["name"] for t in dep}
    assert nomes_dep == {"Estadual", "Municipal"}


async def test_temporal_metrica_invalida_levanta(fake_repo_full):
    service = ConectividadeService(fake_repo_full)
    with pytest.raises(ValueError):
        await service.build_analise_temporal(metrica="nao_existe")


async def test_temporal_propaga_metrica_e_pibid(fake_repo_full):
    service = ConectividadeService(fake_repo_full)
    await service.build_analise_temporal(metrica="in_banda_larga", pibid=False)
    assert fake_repo_full.calls["find_evolucao_por_localizacao"]["metrica"] == "in_banda_larga"
    assert fake_repo_full.calls["find_evolucao_por_localizacao"]["pibid"] is False
    assert fake_repo_full.calls["find_evolucao_por_dependencia"]["metrica"] == "in_banda_larga"


# ---------------------------------------------------------------------------
# build_mapa — pontos pré-computados
# ---------------------------------------------------------------------------

async def test_mapa_envelopa_pontos_do_repositorio(fake_repo_full):
    service = ConectividadeService(fake_repo_full)
    envelope = await service.build_mapa(ano=2024, variaveis=None)
    assert envelope["descricao"] == MAPA_DESCRICAO
    pontos = envelope["data"]["pontos"]
    assert pontos == make_pontos_mapa()


async def test_mapa_score_pode_exceder_17(fake_repo_full):
    service = ConectividadeService(fake_repo_full)
    pontos = (await service.build_mapa(ano=2024, variaveis=None))["data"]["pontos"]
    scores = [p["score_conectividade"] for p in pontos]
    # o score pré-computado não é binário e pode passar de 17 (ex.: 26).
    assert max(scores) == 26


async def test_mapa_propaga_filtros(fake_repo_full):
    service = ConectividadeService(fake_repo_full)
    await service.build_mapa(ano=2023, variaveis=["in_internet"], pibid=True)
    chamada = fake_repo_full.calls["find_pontos_mapa_raw"]
    assert chamada == {"ano": 2023, "variaveis": ["in_internet"], "pibid": True}
