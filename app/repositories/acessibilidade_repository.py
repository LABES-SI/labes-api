from sqlalchemy import Numeric, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.acessibilidade import (
    AcessibilidadeMunicipio,
    AcessibilidadeTemporal,
)
from app.models.acessibilidade import acessibilidade as t
from app.models.acessibilidade import (
    dim_entidade as de,
    dim_tp_localizacao as dl,
    fato_acessibilidade as f,
)


def _row_to_municipio(row) -> AcessibilidadeMunicipio:
    return AcessibilidadeMunicipio(
        municipio=row.municipio,
        rampas=float(row.rampas),
        corrimao=float(row.corrimao),
        elevador=float(row.elevador),
        pisos_tateis=float(row.pisos_tateis),
        vao_livre=float(row.vao_livre),
        banheiro_pne=float(row.banheiro_pne),
    )


def _row_to_temporal(row) -> AcessibilidadeTemporal:
    return AcessibilidadeTemporal(
        ano=int(row.ano),
        codigo_localizacao=int(row.codigo_localizacao),
        localizacao=row.localizacao,
        percentual=float(row.percentual),
    )


def _avg_pct(col):
    return func.round((func.avg(col).cast(Numeric) * 100), 1)


METRIC_TO_FATO_COLUMN = {
    "rampas": f.c.in_acessibilidade_rampas,
    "corrimao": f.c.in_acessibilidade_corrimao,
    "elevador": f.c.in_acessibilidade_elevador,
    "pisos_tateis": f.c.in_acessibilidade_pisos_tateis,
    "vao_livre": f.c.in_acessibilidade_vao_livre,
    "banheiro_pne": f.c.in_banheiro_pne,
}


class AcessibilidadeRepository:
    """
    Acessa silver.acessibilidade no warehouse.

    Tabela: silver.acessibilidade
    Owner do mart: squad de dados
    Granularidade: uma linha por escola por ano censo.

    AVG ignora NULL automaticamente — denominadores podem diferir
    por métrica, o que é o comportamento esperado para este tipo de
    indicador de censo.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_media_por_municipio(
        self,
        ano: int | None,
        municipios: list[str] | None,
    ) -> list[AcessibilidadeMunicipio]:
        stmt = (
            select(
                t.c.NO_MUNICIPIO.label("municipio"),
                _avg_pct(t.c.IN_ACESSIBILIDADE_RAMPAS).label("rampas"),
                _avg_pct(t.c.IN_ACESSIBILIDADE_CORRIMAO).label("corrimao"),
                _avg_pct(t.c.IN_ACESSIBILIDADE_ELEVADOR).label("elevador"),
                _avg_pct(t.c.IN_ACESSIBILIDADE_PISOS_TATEIS).label("pisos_tateis"),
                _avg_pct(t.c.IN_ACESSIBILIDADE_VAO_LIVRE).label("vao_livre"),
                _avg_pct(t.c.IN_BANHEIRO_PNE).label("banheiro_pne"),
            )
            .where(t.c.NO_MUNICIPIO.is_not(None))
            .group_by(t.c.NO_MUNICIPIO)
            .order_by(t.c.NO_MUNICIPIO)
        )

        if ano is not None:
            stmt = stmt.where(t.c.NU_ANO_CENSO == ano)
        if municipios:
            stmt = stmt.where(t.c.NO_MUNICIPIO.in_(municipios))

        result = await self._session.execute(stmt)
        return [_row_to_municipio(row) for row in result]

    async def find_municipios_disponiveis(self) -> list[tuple[int, str]]:
        """Lista (codigo, nome) de todos os municípios presentes na tabela."""
        stmt = (
            select(
                t.c.CO_MUNICIPIO.label("codigo"),
                t.c.NO_MUNICIPIO.label("nome"),
            )
            .where(t.c.CO_MUNICIPIO.is_not(None), t.c.NO_MUNICIPIO.is_not(None))
            .distinct()
            .order_by(t.c.NO_MUNICIPIO)
        )
        result = await self._session.execute(stmt)
        return [(int(row.codigo), row.nome) for row in result]

    async def find_anos_disponiveis(self) -> list[int]:
        """Lista de anos do censo presentes na tabela, em ordem crescente."""
        return [int(v) for v in await self._find_distinct(t.c.NU_ANO_CENSO)]

    async def find_evolucao_por_localizacao(
        self,
        metrica: str,
    ) -> list[AcessibilidadeTemporal]:
        """Percentual da métrica por (ano, tipo de localização).

        Denominador é o total de entidades naquele ano + tipo de localização;
        numerador é o total com a métrica = 1. Equivale à query original com
        subquery, escrita aqui via agregação condicional (COUNT(CASE WHEN...))
        para evitar a subquery correlacionada.
        """
        if metrica not in METRIC_TO_FATO_COLUMN:
            raise ValueError(
                f"Métrica inválida: {metrica!r}. Esperado uma de: "
                f"{sorted(METRIC_TO_FATO_COLUMN)}"
            )
        col = METRIC_TO_FATO_COLUMN[metrica]

        percentual = func.round(
            (
                func.count(case((col == 1, 1)))
                * 100.0
                / func.nullif(func.count(f.c.co_entidade), 0)
            ).cast(Numeric),
            2,
        )

        stmt = (
            select(
                f.c.nu_ano_censo.label("ano"),
                dl.c.co_tp_localizacao.label("codigo_localizacao"),
                dl.c.no_tp_localizacao.label("localizacao"),
                percentual.label("percentual"),
            )
            .select_from(
                f.outerjoin(de, f.c.co_entidade == de.c.co_entidade).outerjoin(
                    dl, de.c.tp_localizacao == dl.c.co_tp_localizacao
                )
            )
            .where(
                dl.c.no_tp_localizacao.is_not(None),
                f.c.nu_ano_censo.is_not(None),
            )
            .group_by(
                f.c.nu_ano_censo,
                dl.c.co_tp_localizacao,
                dl.c.no_tp_localizacao,
            )
            .order_by(f.c.nu_ano_censo, dl.c.no_tp_localizacao)
        )

        result = await self._session.execute(stmt)
        return [_row_to_temporal(row) for row in result]

    async def _find_distinct(self, column) -> list:
        """SELECT DISTINCT column WHERE column IS NOT NULL ORDER BY column.

        Helper para listas de valores únicos de uma coluna — usado pelas
        funções `find_*_disponiveis` que alimentam os dropdowns de filtro.
        Não cobre o caso de múltiplas colunas (ex: município = código + nome).
        """
        stmt = (
            select(column)
            .where(column.is_not(None))
            .distinct()
            .order_by(column)
        )
        result = await self._session.execute(stmt)
        return [row[0] for row in result]
