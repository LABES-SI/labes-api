from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.acessibilidade import AcessibilidadeMunicipio


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
        municipios: list[str],
    ) -> list[AcessibilidadeMunicipio]:
        if not municipios:
            return []

        query = text(
            """
            SELECT
                "NO_MUNICIPIO" AS municipio,
                ROUND(AVG("IN_ACESSIBILIDADE_RAMPAS")::numeric       * 100, 1) AS rampas,
                ROUND(AVG("IN_ACESSIBILIDADE_CORRIMAO")::numeric     * 100, 1) AS corrimao,
                ROUND(AVG("IN_ACESSIBILIDADE_ELEVADOR")::numeric     * 100, 1) AS elevador,
                ROUND(AVG("IN_ACESSIBILIDADE_PISOS_TATEIS")::numeric * 100, 1) AS pisos_tateis,
                ROUND(AVG("IN_ACESSIBILIDADE_VAO_LIVRE")::numeric    * 100, 1) AS vao_livre,
                ROUND(AVG("IN_BANHEIRO_PNE")::numeric                * 100, 1) AS banheiro_pne
            FROM silver.acessibilidade
            WHERE (CAST(:ano AS BIGINT) IS NULL OR "NU_ANO_CENSO" = :ano)
              AND "NO_MUNICIPIO" = ANY(:municipios)
            GROUP BY "NO_MUNICIPIO"
            ORDER BY "NO_MUNICIPIO"
            """
        )

        result = await self._session.execute(
            query,
            {"ano": ano, "municipios": municipios},
        )

        return [_row_to_municipio(row) for row in result]

    async def find_acessibilidade_todos_municipios(
        self,
        ano: int | None,
    ) -> list[AcessibilidadeMunicipio]:
        """Médias por município para todos os municípios do recorte.

        Usado quando o usuário não envia filtro de municípios — o frontend
        ordena/seleciona conforme a métrica escolhida.
        """
        query = text(
            """
            SELECT
                "NO_MUNICIPIO" AS municipio,
                ROUND(AVG("IN_ACESSIBILIDADE_RAMPAS")::numeric       * 100, 1) AS rampas,
                ROUND(AVG("IN_ACESSIBILIDADE_CORRIMAO")::numeric     * 100, 1) AS corrimao,
                ROUND(AVG("IN_ACESSIBILIDADE_ELEVADOR")::numeric     * 100, 1) AS elevador,
                ROUND(AVG("IN_ACESSIBILIDADE_PISOS_TATEIS")::numeric * 100, 1) AS pisos_tateis,
                ROUND(AVG("IN_ACESSIBILIDADE_VAO_LIVRE")::numeric    * 100, 1) AS vao_livre,
                ROUND(AVG("IN_BANHEIRO_PNE")::numeric                * 100, 1) AS banheiro_pne
            FROM silver.acessibilidade
            WHERE (CAST(:ano AS BIGINT) IS NULL OR "NU_ANO_CENSO" = :ano)
              AND "NO_MUNICIPIO" IS NOT NULL
            GROUP BY "NO_MUNICIPIO"
            ORDER BY "NO_MUNICIPIO" ASC
            """
        )

        result = await self._session.execute(query, {"ano": ano})

        return [_row_to_municipio(row) for row in result]

    async def find_municipios_disponiveis(self) -> list[tuple[int, str]]:
        """Lista (codigo, nome) de todos os municípios presentes na tabela."""
        query = text(
            """
            SELECT DISTINCT "CO_MUNICIPIO" AS codigo, "NO_MUNICIPIO" AS nome
            FROM silver.acessibilidade
            WHERE "CO_MUNICIPIO" IS NOT NULL AND "NO_MUNICIPIO" IS NOT NULL
            ORDER BY "NO_MUNICIPIO"
            """
        )
        result = await self._session.execute(query)
        return [(int(row.codigo), row.nome) for row in result]

    async def find_anos_disponiveis(self) -> list[int]:
        """Lista de anos do censo presentes na tabela, em ordem crescente."""
        query = text(
            """
            SELECT DISTINCT "NU_ANO_CENSO" AS ano
            FROM silver.acessibilidade
            WHERE "NU_ANO_CENSO" IS NOT NULL
            ORDER BY "NU_ANO_CENSO"
            """
        )
        result = await self._session.execute(query)
        return [int(row.ano) for row in result]
