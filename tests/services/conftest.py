"""Fixtures compartilhadas dos testes de service.

`FakeConectividadeRepository`/`FakeInfraestruturaRepository` substituem o
repositório real (warehouse) por dubles assíncronos com dados em memória, para
que os testes de service exercitem TODOS os gráficos sem tocar o banco. Cada
método espelha a assinatura usada pelo service e devolve os domain objects
configurados no construtor.
"""

import pytest

from app.domain.conectividade import (
    ConectividadeDependencia,
    ConectividadeEscola,
    ConectividadeLocalizacao,
    ConectividadeMunicipio,
    ConectividadeTemporal,
    ConectividadeTemporalDependencia,
    TotalEscolas,
)
from app.domain.infraestrutura import (
    InfraestruturaDependencia,
    InfraestruturaEscola,
    InfraestruturaLocalizacao,
    InfraestruturaMunicipio,
    InfraestruturaTemporal,
    InfraestruturaTemporalDependencia,
)
from app.services.conectividade_service import METRIC_FIELDS
from app.services.infraestrutura_service import (
    METRIC_FIELDS as INFRAESTRUTURA_METRIC_FIELDS,
)


class FakeConectividadeRepository:
    """Duble do ConectividadeRepository: devolve dados em memória e registra as
    chamadas recebidas (para asserções sobre filtros/paginação)."""

    def __init__(
        self,
        *,
        municipios=None,
        total_com=None,
        total_geral=None,
        dependencias=None,
        localizacoes=None,
        escolas=None,
        total_escolas_count=0,
        ideb=None,
        pibid=None,
        temporal_localizacao=None,
        temporal_dependencia=None,
        pontos_mapa=None,
    ):
        self._municipios = municipios or []
        self._total_com = total_com if total_com is not None else TotalEscolas(total=0)
        self._total_geral = (
            total_geral if total_geral is not None else TotalEscolas(total=0)
        )
        self._dependencias = dependencias or []
        self._localizacoes = localizacoes or []
        self._escolas = escolas or []
        self._total_escolas_count = total_escolas_count
        self._ideb = ideb or {}
        self._pibid = pibid or {}
        self._temporal_localizacao = temporal_localizacao or []
        self._temporal_dependencia = temporal_dependencia or []
        self._pontos_mapa = pontos_mapa or []
        self.calls: dict[str, dict] = {}

    async def find_media_por_municipio(self, **kwargs):
        self.calls["find_media_por_municipio"] = kwargs
        return self._municipios

    async def find_total_escolas(self, **kwargs):
        self.calls["find_total_escolas"] = kwargs
        return self._total_com

    async def find_total_escolas_geral(self, **kwargs):
        self.calls["find_total_escolas_geral"] = kwargs
        return self._total_geral

    async def find_media_por_dependencia(self, **kwargs):
        self.calls["find_media_por_dependencia"] = kwargs
        return self._dependencias

    async def find_media_por_localizacao(self, **kwargs):
        self.calls["find_media_por_localizacao"] = kwargs
        return self._localizacoes

    async def count_metricas_por_escola(self, **kwargs):
        self.calls["count_metricas_por_escola"] = kwargs
        return self._total_escolas_count

    async def find_metricas_por_escola(self, **kwargs):
        self.calls["find_metricas_por_escola"] = kwargs
        return self._escolas

    async def find_ideb_por_entidades(self, entidades):
        self.calls["find_ideb_por_entidades"] = {"entidades": entidades}
        return self._ideb

    async def find_pibid_por_entidades(self, entidades):
        self.calls["find_pibid_por_entidades"] = {"entidades": entidades}
        return self._pibid

    async def find_evolucao_por_localizacao(self, **kwargs):
        self.calls["find_evolucao_por_localizacao"] = kwargs
        return self._temporal_localizacao

    async def find_evolucao_por_dependencia(self, **kwargs):
        self.calls["find_evolucao_por_dependencia"] = kwargs
        return self._temporal_dependencia

    async def find_pontos_mapa_raw(self, **kwargs):
        self.calls["find_pontos_mapa_raw"] = kwargs
        return self._pontos_mapa


# ---------------------------------------------------------------------------
# Builders de dados de exemplo — coerentes com as 17 métricas de conectividade.
# ---------------------------------------------------------------------------

ALL_KEYS = [chave for chave, _ in METRIC_FIELDS]


def make_municipios():
    return [
        ConectividadeMunicipio(
            codigo_municipio=1, municipio="Belém", percentual=80.0, total_escolas=100
        ),
        ConectividadeMunicipio(
            codigo_municipio=2, municipio="Ananindeua", percentual=55.5, total_escolas=40
        ),
    ]


def make_dependencias():
    return [
        ConectividadeDependencia(
            codigo_dependencia=1, dependencia="Federal", percentual=90.0, total_escolas=10
        ),
        ConectividadeDependencia(
            codigo_dependencia=2, dependencia="Estadual", percentual=70.0, total_escolas=50
        ),
        ConectividadeDependencia(
            codigo_dependencia=3, dependencia="Municipal", percentual=40.0, total_escolas=80
        ),
    ]


def make_localizacoes():
    return [
        ConectividadeLocalizacao(
            codigo_localizacao=1, localizacao="Urbana", percentual=75.0, total_escolas=120
        ),
        ConectividadeLocalizacao(
            codigo_localizacao=2, localizacao="Rural", percentual=30.0, total_escolas=60
        ),
    ]


def make_escola(co_entidade, no_entidade, possui_keys, ano=2024):
    """Cria uma ConectividadeEscola com 0/1 por métrica e score = nº de possuídas."""
    metricas = {k: (1 if k in possui_keys else 0) for k in ALL_KEYS}
    return ConectividadeEscola(
        co_entidade=co_entidade,
        no_entidade=no_entidade,
        nu_ano_censo=ano,
        metricas=metricas,
        score=sum(metricas.values()),
    )


def make_escolas():
    # Ordenadas por score DESC como o repositório real entrega.
    return [
        make_escola(101, "Escola A", ALL_KEYS),                      # score 17
        make_escola(102, "Escola B", ALL_KEYS[:9]),                  # score 9
        make_escola(103, "Escola C", ["in_internet"]),              # score 1
    ]


def make_temporal_localizacao():
    return [
        ConectividadeTemporal(ano=2022, codigo_localizacao=1, localizacao="Urbana", percentual=60.0),
        ConectividadeTemporal(ano=2023, codigo_localizacao=1, localizacao="Urbana", percentual=70.0),
        ConectividadeTemporal(ano=2022, codigo_localizacao=2, localizacao="Rural", percentual=20.0),
        ConectividadeTemporal(ano=2023, codigo_localizacao=2, localizacao="Rural", percentual=25.0),
    ]


def make_temporal_dependencia():
    return [
        ConectividadeTemporalDependencia(ano=2022, codigo_dependencia=2, dependencia="Estadual", percentual=50.0),
        ConectividadeTemporalDependencia(ano=2023, codigo_dependencia=2, dependencia="Estadual", percentual=65.0),
        ConectividadeTemporalDependencia(ano=2022, codigo_dependencia=3, dependencia="Municipal", percentual=30.0),
        ConectividadeTemporalDependencia(ano=2023, codigo_dependencia=3, dependencia="Municipal", percentual=35.0),
    ]


def make_pontos_mapa():
    base = {k: 0.0 for k in ALL_KEYS}
    return [
        {
            "co_entidade": 101,
            "nu_ano_censo": 2024,
            "pibid": 1,
            **{**base, "in_internet": 1.0, "qt_desktop_aluno": 9.0},
            "score_conectividade": 26,  # pré-computado, pode passar de 17
            "classificacao_conectividade": "Boa",
            "ideb_2023_anos_iniciais": 5.8,
            "ideb_2023_anos_finais": 4.9,
            "ideb_2023_ensino_medio": 4.1,
            "ideb_2023_anos_iniciais_mun": 5.2,
            "ideb_2023_anos_finais_mun": 4.5,
            "ideb_2023_ensino_medio_mun": 3.9,
            "dt_carga": "2026-06-17T02:53:00.378258+00:00",
        },
        {
            "co_entidade": 102,
            "nu_ano_censo": 2024,
            "pibid": 0,
            **base,
            "score_conectividade": 0,
            "classificacao_conectividade": "Inexistente",
            "ideb_2023_anos_iniciais": None,  # escola sem nota → NULL preservado
            "ideb_2023_anos_finais": None,
            "ideb_2023_ensino_medio": None,
            "ideb_2023_anos_iniciais_mun": None,
            "ideb_2023_anos_finais_mun": None,
            "ideb_2023_ensino_medio_mun": None,
            "dt_carga": None,
        },
    ]


@pytest.fixture
def fake_repo_full():
    """Repositório com dados em todos os campos — usado pela maioria dos testes."""
    return FakeConectividadeRepository(
        municipios=make_municipios(),
        total_com=TotalEscolas(total=140),
        total_geral=TotalEscolas(total=180),
        dependencias=make_dependencias(),
        localizacoes=make_localizacoes(),
        escolas=make_escolas(),
        total_escolas_count=12,
        ideb={101: {"iniciais": 4.9, "finais": 4.2, "medio": 3.6}},
        pibid={101: {"subprojetos": "Matemática / Física", "bolsistas": 7}},
        temporal_localizacao=make_temporal_localizacao(),
        temporal_dependencia=make_temporal_dependencia(),
        pontos_mapa=make_pontos_mapa(),
    )


# ===========================================================================
# INFRAESTRUTURA — duble + builders coerentes com as 17 métricas de infra.
# Estrutura idêntica ao fake de conectividade; muda só o domínio e o /mapa
# (score calculado on-the-fly, sem IDEB/dt_carga).
# ===========================================================================


class FakeInfraestruturaRepository:
    """Duble do InfraestruturaRepository: devolve dados em memória e registra as
    chamadas recebidas (para asserções sobre filtros/paginação)."""

    def __init__(
        self,
        *,
        municipios=None,
        total_com=None,
        total_geral=None,
        dependencias=None,
        localizacoes=None,
        escolas=None,
        total_escolas_count=0,
        ideb=None,
        pibid=None,
        temporal_localizacao=None,
        temporal_dependencia=None,
        pontos_mapa=None,
    ):
        self._municipios = municipios or []
        self._total_com = total_com if total_com is not None else TotalEscolas(total=0)
        self._total_geral = (
            total_geral if total_geral is not None else TotalEscolas(total=0)
        )
        self._dependencias = dependencias or []
        self._localizacoes = localizacoes or []
        self._escolas = escolas or []
        self._total_escolas_count = total_escolas_count
        self._ideb = ideb or {}
        self._pibid = pibid or {}
        self._temporal_localizacao = temporal_localizacao or []
        self._temporal_dependencia = temporal_dependencia or []
        self._pontos_mapa = pontos_mapa or []
        self.calls: dict[str, dict] = {}

    async def find_media_por_municipio(self, **kwargs):
        self.calls["find_media_por_municipio"] = kwargs
        return self._municipios

    async def find_total_escolas(self, **kwargs):
        self.calls["find_total_escolas"] = kwargs
        return self._total_com

    async def find_total_escolas_geral(self, **kwargs):
        self.calls["find_total_escolas_geral"] = kwargs
        return self._total_geral

    async def find_media_por_dependencia(self, **kwargs):
        self.calls["find_media_por_dependencia"] = kwargs
        return self._dependencias

    async def find_media_por_localizacao(self, **kwargs):
        self.calls["find_media_por_localizacao"] = kwargs
        return self._localizacoes

    async def count_metricas_por_escola(self, **kwargs):
        self.calls["count_metricas_por_escola"] = kwargs
        return self._total_escolas_count

    async def find_metricas_por_escola(self, **kwargs):
        self.calls["find_metricas_por_escola"] = kwargs
        return self._escolas

    async def find_ideb_por_entidades(self, entidades):
        self.calls["find_ideb_por_entidades"] = {"entidades": entidades}
        return self._ideb

    async def find_pibid_por_entidades(self, entidades):
        self.calls["find_pibid_por_entidades"] = {"entidades": entidades}
        return self._pibid

    async def find_evolucao_por_localizacao(self, **kwargs):
        self.calls["find_evolucao_por_localizacao"] = kwargs
        return self._temporal_localizacao

    async def find_evolucao_por_dependencia(self, **kwargs):
        self.calls["find_evolucao_por_dependencia"] = kwargs
        return self._temporal_dependencia

    async def find_pontos_mapa_raw(self, **kwargs):
        self.calls["find_pontos_mapa_raw"] = kwargs
        return self._pontos_mapa


ALL_KEYS_INFRA = [chave for chave, _ in INFRAESTRUTURA_METRIC_FIELDS]


def make_municipios_infra():
    return [
        InfraestruturaMunicipio(
            codigo_municipio=1, municipio="Belém", percentual=80.0, total_escolas=100
        ),
        InfraestruturaMunicipio(
            codigo_municipio=2, municipio="Ananindeua", percentual=55.5, total_escolas=40
        ),
    ]


def make_dependencias_infra():
    return [
        InfraestruturaDependencia(
            codigo_dependencia=1, dependencia="Federal", percentual=90.0, total_escolas=10
        ),
        InfraestruturaDependencia(
            codigo_dependencia=2, dependencia="Estadual", percentual=70.0, total_escolas=50
        ),
        InfraestruturaDependencia(
            codigo_dependencia=3, dependencia="Municipal", percentual=40.0, total_escolas=80
        ),
    ]


def make_localizacoes_infra():
    return [
        InfraestruturaLocalizacao(
            codigo_localizacao=1, localizacao="Urbana", percentual=75.0, total_escolas=120
        ),
        InfraestruturaLocalizacao(
            codigo_localizacao=2, localizacao="Rural", percentual=30.0, total_escolas=60
        ),
    ]


def make_escola_infra(co_entidade, no_entidade, possui_keys, ano=2024):
    """Cria uma InfraestruturaEscola com 0/1 por métrica e score = nº de possuídas."""
    metricas = {k: (1 if k in possui_keys else 0) for k in ALL_KEYS_INFRA}
    return InfraestruturaEscola(
        co_entidade=co_entidade,
        no_entidade=no_entidade,
        nu_ano_censo=ano,
        metricas=metricas,
        score=sum(metricas.values()),
    )


def make_escolas_infra():
    # Ordenadas por score DESC como o repositório real entrega.
    return [
        make_escola_infra(101, "Escola A", ALL_KEYS_INFRA),               # score 17
        make_escola_infra(102, "Escola B", ALL_KEYS_INFRA[:9]),           # score 9
        make_escola_infra(103, "Escola C", ["in_agua_potavel"]),          # score 1
    ]


def make_temporal_localizacao_infra():
    return [
        InfraestruturaTemporal(ano=2022, codigo_localizacao=1, localizacao="Urbana", percentual=60.0),
        InfraestruturaTemporal(ano=2023, codigo_localizacao=1, localizacao="Urbana", percentual=70.0),
        InfraestruturaTemporal(ano=2022, codigo_localizacao=2, localizacao="Rural", percentual=20.0),
        InfraestruturaTemporal(ano=2023, codigo_localizacao=2, localizacao="Rural", percentual=25.0),
    ]


def make_temporal_dependencia_infra():
    return [
        InfraestruturaTemporalDependencia(ano=2022, codigo_dependencia=2, dependencia="Estadual", percentual=50.0),
        InfraestruturaTemporalDependencia(ano=2023, codigo_dependencia=2, dependencia="Estadual", percentual=65.0),
        InfraestruturaTemporalDependencia(ano=2022, codigo_dependencia=3, dependencia="Municipal", percentual=30.0),
        InfraestruturaTemporalDependencia(ano=2023, codigo_dependencia=3, dependencia="Municipal", percentual=35.0),
    ]


def make_pontos_mapa_infra():
    base = {k: 0.0 for k in ALL_KEYS_INFRA}
    return [
        {
            "co_entidade": 101,
            "nu_ano_censo": 2024,
            "pibid": 1,
            **{**base, "in_agua_potavel": 1.0, "in_biblioteca": 1.0},
            "score_infraestrutura": 15,
            "classificacao_infraestrutura": "Boa",
        },
        {
            "co_entidade": 102,
            "nu_ano_censo": 2024,
            "pibid": 0,
            **base,
            "score_infraestrutura": 0,
            "classificacao_infraestrutura": "Inexistente",
        },
    ]


@pytest.fixture
def fake_infra_repo_full():
    """Repositório de infraestrutura com dados em todos os campos."""
    return FakeInfraestruturaRepository(
        municipios=make_municipios_infra(),
        total_com=TotalEscolas(total=140),
        total_geral=TotalEscolas(total=180),
        dependencias=make_dependencias_infra(),
        localizacoes=make_localizacoes_infra(),
        escolas=make_escolas_infra(),
        total_escolas_count=12,
        ideb={101: {"iniciais": 4.9, "finais": 4.2, "medio": 3.6}},
        pibid={101: {"subprojetos": "Matemática / Física", "bolsistas": 7}},
        temporal_localizacao=make_temporal_localizacao_infra(),
        temporal_dependencia=make_temporal_dependencia_infra(),
        pontos_mapa=make_pontos_mapa_infra(),
    )
