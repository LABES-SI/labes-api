from sqlalchemy import Numeric, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.acessibilidade import AcessibilidadeMunicipio
from app.models.acessibilidade import acessibilidade as t


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


def _avg_pct(col):
    return func.round((func.avg(col).cast(Numeric) * 100), 1)


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
