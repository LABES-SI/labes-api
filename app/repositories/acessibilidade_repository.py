from sqlalchemy import Numeric, case, func, literal, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.acessibilidade import AcessibilidadeMapaPonto, AcessibilidadeMunicipio
from app.models.acessibilidade import (
    acessibilidade as t,
    dim_entidade,
    dim_municipio,
    dim_tp_dependencia,
    dim_tp_localizacao,
    fato_acessibilidade,
)


# Whitelist única de variáveis indicadoras que podem vir como filtro no
# endpoint /mapa. É a fonte de verdade consumida pelo Literal da rota e pelo
# filtro AND no repository — protege contra string crua do usuário virar
# coluna SQL.
VARIAVEIS_ACESSIBILIDADE: dict[str, "object"] = {
    col.name: col for col in fato_acessibilidade.c if col.name.startswith("in_")
}


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


def _row_to_mapa_ponto(row) -> AcessibilidadeMapaPonto:
    return AcessibilidadeMapaPonto(
        co_entidade=int(row.co_entidade),
        no_entidade=row.no_entidade,
        no_municipio=row.no_municipio,
        no_bairro=row.no_bairro,
        latitude=float(row.latitude),
        longitude=float(row.longitude),
        no_tp_dependencia=row.no_tp_dependencia,
        no_tp_localizacao=row.no_tp_localizacao,
        score_acessibilidade=int(row.score_acessibilidade),
        classificacao_acessibilidade=row.classificacao_acessibilidade,
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

    def _build_pontos_mapa_stmt(
        self,
        ano: int | None,
        municipios: list[str] | None,
        variaveis: list[str] | None,
        rede_ensino: list[str] | None,
        tp_localizacao: list[str] | None,
    ):
        """Monta o SELECT do mapa de acessibilidade (joins + score +
        classificação + filtros). Helper compartilhado por
        `find_pontos_mapa` (dataclass path, usado pelos testes visuais) e
        `find_pontos_mapa_raw` (dict path, usado pela rota HTTP)."""
        f = fato_acessibilidade.c
        e = dim_entidade.c
        m = dim_municipio.c
        d = dim_tp_dependencia.c
        l = dim_tp_localizacao.c

        def coalesce0(col):
            return func.coalesce(col, 0)

        score_cols = [
            f.in_sala_atendimento_especial,
            f.in_banheiro_pne,
            f.in_acessibilidade_rampas,
            f.in_acessibilidade_corrimao,
            f.in_acessibilidade_elevador,
            f.in_acessibilidade_pisos_tateis,
            f.in_acessibilidade_vao_livre,
            f.in_acessibilidade_sinal_visual,
            f.in_acessibilidade_sinal_sonoro,
            f.in_acessibilidade_sinal_tatil,
            f.in_acessibilidade_sinalizacao,
        ]
        score_expr = sum((coalesce0(c) for c in score_cols), literal(0))

        baixa_cols = [c for c in score_cols if c is not f.in_acessibilidade_corrimao]
        baixa_sum = sum((coalesce0(c) for c in baixa_cols), literal(0))

        classificacao_expr = case(
            (score_expr >= 8, literal("Boa")),
            (score_expr >= 5, literal("Média")),
            (baixa_sum >= 1, literal("Baixa")),
            else_=literal("Inexistente"),
        )

        join_tree = (
            fato_acessibilidade
            .join(dim_entidade, f.co_entidade == e.co_entidade)
            .outerjoin(dim_municipio, e.co_municipio == m.co_municipio)
            .outerjoin(dim_tp_dependencia, e.tp_dependencia == d.co_tp_dependencia)
            .outerjoin(dim_tp_localizacao, e.tp_localizacao == l.co_tp_localizacao)
        )

        stmt = (
            select(
                e.co_entidade.label("co_entidade"),
                e.no_entidade.label("no_entidade"),
                m.no_municipio.label("no_municipio"),
                e.no_bairro.label("no_bairro"),
                e.latitude.label("latitude"),
                e.longitude.label("longitude"),
                d.no_tp_dependencia.label("no_tp_dependencia"),
                l.no_tp_localizacao.label("no_tp_localizacao"),
                score_expr.label("score_acessibilidade"),
                classificacao_expr.label("classificacao_acessibilidade"),
            )
            .select_from(join_tree)
            .where(e.latitude.is_not(None), e.longitude.is_not(None))
        )

        if ano is not None:
            stmt = stmt.where(f.nu_ano_censo == ano)
        if municipios:
            stmt = stmt.where(m.no_municipio.in_(municipios))
        if rede_ensino:
            stmt = stmt.where(d.no_tp_dependencia.in_(rede_ensino))
        if tp_localizacao:
            stmt = stmt.where(l.no_tp_localizacao.in_(tp_localizacao))
        if variaveis:
            for nome in variaveis:
                col = VARIAVEIS_ACESSIBILIDADE.get(nome)
                if col is None:
                    raise ValueError(f"Variável inválida: {nome!r}")
                stmt = stmt.where(col == 1)

        return stmt

    async def find_pontos_mapa(
        self,
        ano: int | None,
        municipios: list[str] | None,
        variaveis: list[str] | None,
        rede_ensino: list[str] | None,
        tp_localizacao: list[str] | None,
    ) -> list[AcessibilidadeMapaPonto]:
        """
        Lista escolas georreferenciadas com score (0-11) e classificação
        (Boa/Média/Baixa/Inexistente) de acessibilidade.

        - `variaveis` é AND: a escola precisa ter TODAS as colunas indicadas = 1.
        - `municipios`/`rede_ensino`/`tp_localizacao` filtram pelos nomes
          legíveis das dimensões (no_municipio, no_tp_dependencia, no_tp_localizacao).
        - Quirk preservado da regra original: 'Baixa' soma 10 indicadores
          (omite in_acessibilidade_corrimao); 'Boa'/'Média' somam 11.
        """
        stmt = self._build_pontos_mapa_stmt(
            ano=ano,
            municipios=municipios,
            variaveis=variaveis,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
        )
        result = await self._session.execute(stmt)
        return [_row_to_mapa_ponto(row) for row in result]

    async def find_pontos_mapa_raw(
        self,
        ano: int | None,
        municipios: list[str] | None,
        variaveis: list[str] | None,
        rede_ensino: list[str] | None,
        tp_localizacao: list[str] | None,
    ) -> list[dict]:
        """Versão otimizada para o endpoint HTTP: retorna list[dict] direto,
        sem materializar dataclasses. Usada pela rota /mapa onde o overhead
        de asdict() × ~9.700 linhas é significativo. Coage Numeric → float
        para o JSON sair idêntico ao caminho do dataclass."""
        stmt = self._build_pontos_mapa_stmt(
            ano=ano,
            municipios=municipios,
            variaveis=variaveis,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
        )
        result = await self._session.execute(stmt)
        return [
            {
                "co_entidade": int(r["co_entidade"]),
                "no_entidade": r["no_entidade"],
                "no_municipio": r["no_municipio"],
                "no_bairro": r["no_bairro"],
                "latitude": float(r["latitude"]),
                "longitude": float(r["longitude"]),
                "no_tp_dependencia": r["no_tp_dependencia"],
                "no_tp_localizacao": r["no_tp_localizacao"],
                "score_acessibilidade": int(r["score_acessibilidade"]),
                "classificacao_acessibilidade": r["classificacao_acessibilidade"],
            }
            for r in result.mappings()
        ]

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
