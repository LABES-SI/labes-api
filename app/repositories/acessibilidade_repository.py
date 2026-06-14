import asyncio
from contextlib import asynccontextmanager

from sqlalchemy import Numeric, and_, case, func, literal, or_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.acessibilidade import (
    AcessibilidadeEscola,
    AcessibilidadeLocalizacao,
    AcessibilidadeMapaPonto,
    AcessibilidadeMunicipio,
    AcessibilidadeTemporal,
    #P1G4
    TotalEscolas,
    #P1G5
    AcessibilidadeDependencia,
    #P1G6
    AcessibilidadeTemporalDependencia,
)
from app.models.acessibilidade import (
    base_pibid,
    dim_entidade,
    dim_municipio,
    dim_tp_dependencia,
    dim_tp_localizacao,
    ideb_anos_finais_escolas,
    ideb_anos_iniciais_escolas,
    ideb_ensino_medio_escolas,
    fato_acessibilidade,
)


# Whitelist única de variáveis indicadoras que podem vir como filtro no
# endpoint /mapa. É a fonte de verdade consumida pelo Literal da rota e pelo
# filtro AND no repository — protege contra string crua do usuário virar
# coluna SQL.
VARIAVEIS_ACESSIBILIDADE: dict[str, "object"] = {
    col.name: col for col in fato_acessibilidade.c if col.name.startswith("in_")
}


METRIC_TO_FATO_COLUMN = {
    "in_banheiro_pne": fato_acessibilidade.c.in_banheiro_pne,
    "in_sala_atendimento_especial": fato_acessibilidade.c.in_sala_atendimento_especial,
    "in_acessibilidade_rampas": fato_acessibilidade.c.in_acessibilidade_rampas,
    "in_acessibilidade_corrimao": fato_acessibilidade.c.in_acessibilidade_corrimao,
    "in_acessibilidade_elevador": fato_acessibilidade.c.in_acessibilidade_elevador,
    "in_acessibilidade_pisos_tateis": fato_acessibilidade.c.in_acessibilidade_pisos_tateis,
    "in_acessibilidade_vao_livre": fato_acessibilidade.c.in_acessibilidade_vao_livre,
    "in_acessibilidade_inexistente": fato_acessibilidade.c.in_acessibilidade_inexistente,
    "in_acessibilidade_sinal_tatil": fato_acessibilidade.c.in_acessibilidade_sinal_tatil,
    "in_acessibilidade_sinal_sonoro": fato_acessibilidade.c.in_acessibilidade_sinal_sonoro,
    "in_acessibilidade_sinal_visual": fato_acessibilidade.c.in_acessibilidade_sinal_visual,
    "in_acessibilidade_sinalizacao": fato_acessibilidade.c.in_acessibilidade_sinalizacao,
    "in_prof_psicologo": fato_acessibilidade.c.in_prof_psicologo,
    "in_prof_trad_libras": fato_acessibilidade.c.in_prof_trad_libras,
    "in_prof_revisor_braille": fato_acessibilidade.c.in_prof_revisor_braille,
    "in_prof_assist_social": fato_acessibilidade.c.in_prof_assist_social,
    "in_prof_fonaudiologo": fato_acessibilidade.c.in_prof_fonaudiologo,
}


IDEB_YEAR_COLUMNS = {
    2005: "ideb_2005",
    2007: "ideb_2007",
    2009: "ideb_2009",
    2011: "ideb_2011",
    2013: "ideb_2013",
    2015: "ideb_2015",
    2017: "ideb_2017",
    2019: "ideb_2019",
    2021: "ideb_2021",
    2023: "ideb_2023",
}


def _row_to_municipio(row) -> AcessibilidadeMunicipio:
    return AcessibilidadeMunicipio(
        codigo_municipio=int(row.codigo_municipio),
        municipio=row.municipio,
        percentual=float(row.percentual) if row.percentual is not None else 0.0,
        total_escolas=int(row.total_escolas) if row.total_escolas is not None else 0,
    )


def _row_to_temporal(row) -> AcessibilidadeTemporal:
    return AcessibilidadeTemporal(
        ano=int(row.ano),
        codigo_localizacao=int(row.codigo_localizacao),
        localizacao=row.localizacao,
        percentual=float(row.percentual),
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
        ideb=float(row.ideb) if row.ideb is not None else None,
    )

#P1G4
def _row_to_total_escolas(row) -> TotalEscolas:
    return TotalEscolas(
        total=int(row.total_escolas) if row.total_escolas is not None else 0,
    )

#P1G5
def _row_to_dependencia(row) -> AcessibilidadeDependencia:
    return AcessibilidadeDependencia(
        codigo_dependencia=int(row.codigo_dependencia),
        dependencia=row.dependencia,
        percentual=float(row.percentual) if row.percentual is not None else 0.0,
        total_escolas=int(row.total_escolas) if row.total_escolas is not None else 0,
    )


def _row_to_localizacao(row) -> AcessibilidadeLocalizacao:
    return AcessibilidadeLocalizacao(
        codigo_localizacao=int(row.codigo_localizacao),
        localizacao=row.localizacao,
        percentual=float(row.percentual) if row.percentual is not None else 0.0,
        total_escolas=int(row.total_escolas) if row.total_escolas is not None else 0,
    )


def _row_to_escola(row) -> AcessibilidadeEscola:
    metricas = {chave: int(row[chave] or 0) for chave in METRIC_TO_FATO_COLUMN}
    return AcessibilidadeEscola(
        co_entidade=int(row["co_entidade"]),
        no_entidade=row["no_entidade"],
        nu_ano_censo=int(row["nu_ano_censo"]),
        metricas=metricas,
        score=int(row["score"] or 0),
    )

#P1G6
def _row_to_temporal_dependencia(row) -> AcessibilidadeTemporalDependencia:
    return AcessibilidadeTemporalDependencia(
        ano=int(row.ano),
        codigo_dependencia=int(row.codigo_dependencia),
        dependencia=row.dependencia,
        percentual=float(row.percentual) if row.percentual is not None else 0.0,
    )


def _build_metric_predicate(variaveis: list[str], combine_or: bool):
    """Resolve nomes de variáveis para colunas SQL e combina com AND/OR.

    `combine_or=True` é usado pelo painel quando o filtro de variáveis chega
    vazio (escola conta se tiver QUALQUER variável = 1). `combine_or=False`
    mantém a semântica AND (escola precisa ter TODAS = 1). Levanta
    ValueError em nome inválido.
    """
    cols = []
    for nome in variaveis:
        col = VARIAVEIS_ACESSIBILIDADE.get(nome)
        if col is None:
            raise ValueError(
                f"Variável inválida: {nome!r}. "
                f"Esperado uma de: {sorted(VARIAVEIS_ACESSIBILIDADE)}"
            )
        cols.append(col)
    combinator = or_ if combine_or else and_
    return combinator(*[c == 1 for c in cols])


def _build_ideb_expr(ano_expr):
    ideb_iniciais = ideb_anos_iniciais_escolas.c
    ideb_finais = ideb_anos_finais_escolas.c

    return case(
        *[
            (
                ano_expr == ano,
                func.coalesce(
                    getattr(ideb_iniciais, column_name),
                    getattr(ideb_finais, column_name),
                ),
            )
            for ano, column_name in IDEB_YEAR_COLUMNS.items()
        ],
        else_=literal(None),
    )


class AcessibilidadeRepository:
    """
    Acessa o domínio de acessibilidade no warehouse silver.

    Tabela fato: silver.fato_acessibilidade (uma linha por escola por
    ano censo) + dimensões (entidade, município, tp_dependência,
    tp_localização). Owner do mart: squad de dados.
    """

    def __init__(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
        semaphore: asyncio.Semaphore | None = None,
    ):
        # Recebe o sessionmaker (não uma sessão única): cada query abre a sua
        # própria sessão via _execute/_scalar, então o asyncio.gather do service
        # paraleliza sem corromper a sessão. `semaphore=None` = sem limite
        # (render scripts isolados em tests/visual).
        self._sessionmaker = sessionmaker
        self._semaphore = semaphore

    @asynccontextmanager
    async def _limit(self):
        """Adquire o semáforo global de warehouse ANTES de abrir a sessão, para
        que o teto valha sobre conexões fisicamente em uso. `None` = sem limite."""
        if self._semaphore is None:
            yield
        else:
            async with self._semaphore:
                yield

    async def _execute(self, stmt):
        """Abre uma sessão dedicada para esta query e devolve o Result.

        As queries usam SQLAlchemy Core (Row/mappings, já bufferizados pelo
        driver async no execute), então o Result continua consumível depois que
        a sessão fecha — não há I/O lazy nem expire_on_commit em jogo.
        """
        async with self._limit():
            async with self._sessionmaker() as session:
                return await session.execute(stmt)

    async def _scalar(self, stmt):
        """Como `_execute`, mas para queries escalares (ex.: COUNT)."""
        async with self._limit():
            async with self._sessionmaker() as session:
                return await session.scalar(stmt)

    async def find_media_por_municipio(
        self,
        *,
        variaveis: list[str] | None,
        combine_or: bool = False,
        ano: int | None,
        municipios: list[str] | None,
        rede_ensino: list[str] | None = None,
        tp_localizacao: list[str] | None = None,
    ) -> list[AcessibilidadeMunicipio]:
        """
        Percentual de escolas por município que possuem o(s) indicador(es)
        de `variaveis` = 1, sobre o total de escolas do município no recorte.

        - `combine_or=False` (default): semântica AND — escola precisa ter
          TODAS as variáveis = 1.
        - `combine_or=True`: semântica OR — escola conta se tiver QUALQUER
          variável = 1 (usado pelo painel quando o filtro chega vazio).
        - Denominador (subconsulta correlacionada): COUNT(co_entidade) do
          mesmo município/ano (+ rede_ensino/tp_localização se passados),
          sem o filtro de métrica.
        - `municipios` filtra apenas a saída (cada município é independente
          via correlação `e_sub.co_municipio = e.co_municipio`).
        """
        if not variaveis:
            raise ValueError("É necessário passar ao menos uma variável para o painel")
        metric_predicate = _build_metric_predicate(variaveis, combine_or)

        f = fato_acessibilidade.c
        e = dim_entidade.c
        m = dim_municipio.c
        d = dim_tp_dependencia.c
        l = dim_tp_localizacao.c

        f_sub = fato_acessibilidade.alias("f_sub")
        e_sub = dim_entidade.alias("e_sub")
        d_sub = dim_tp_dependencia.alias("d_sub")
        l_sub = dim_tp_localizacao.alias("l_sub")

        denom_join = (
            f_sub
            .outerjoin(e_sub, f_sub.c.co_entidade == e_sub.c.co_entidade)
            .outerjoin(d_sub, e_sub.c.tp_dependencia == d_sub.c.co_tp_dependencia)
            .outerjoin(l_sub, e_sub.c.tp_localizacao == l_sub.c.co_tp_localizacao)
        )
        denom_filters = [e_sub.c.co_municipio == e.co_municipio]
        if ano is not None:
            denom_filters.append(f_sub.c.nu_ano_censo == ano)
        if rede_ensino:
            denom_filters.append(d_sub.c.no_tp_dependencia.in_(rede_ensino))
        if tp_localizacao:
            denom_filters.append(l_sub.c.no_tp_localizacao.in_(tp_localizacao))

        denominador = (
            select(func.count(f_sub.c.co_entidade))
            .select_from(denom_join)
            .where(*denom_filters)
            .correlate(fato_acessibilidade, dim_entidade)
            .scalar_subquery()
        )

        percentual = func.round(
            (
                func.count(f.co_entidade) * literal(100.0)
                / func.nullif(denominador, 0)
            ).cast(Numeric),
            2,
        )

        join_tree = (
            fato_acessibilidade
            .outerjoin(dim_entidade, f.co_entidade == e.co_entidade)
            .outerjoin(dim_municipio, e.co_municipio == m.co_municipio)
            .outerjoin(dim_tp_dependencia, e.tp_dependencia == d.co_tp_dependencia)
            .outerjoin(dim_tp_localizacao, e.tp_localizacao == l.co_tp_localizacao)
        )

        stmt = (
            select(
                e.co_municipio.label("codigo_municipio"),
                m.no_municipio.label("municipio"),
                percentual.label("percentual"),
                denominador.label("total_escolas"),
            )
            .select_from(join_tree)
            .where(metric_predicate, m.no_municipio.is_not(None))
            .group_by(e.co_municipio, m.no_municipio)
            .order_by(m.no_municipio)
        )

        if ano is not None:
            stmt = stmt.where(f.nu_ano_censo == ano)
        if municipios:
            stmt = stmt.where(m.no_municipio.in_(municipios))
        if rede_ensino:
            stmt = stmt.where(d.no_tp_dependencia.in_(rede_ensino))
        if tp_localizacao:
            stmt = stmt.where(l.no_tp_localizacao.in_(tp_localizacao))

        result = await self._execute(stmt)
        return [_row_to_municipio(row) for row in result]

    async def find_municipios_disponiveis(self) -> list[tuple[int, str]]:
        """Lista (codigo, nome) de todos os municípios com escolas."""
        e = dim_entidade.c
        m = dim_municipio.c
        stmt = (
            select(
                m.co_municipio.label("codigo"),
                m.no_municipio.label("nome"),
            )
            .select_from(
                dim_municipio.join(dim_entidade, e.co_municipio == m.co_municipio)
            )
            .where(m.co_municipio.is_not(None), m.no_municipio.is_not(None))
            .distinct()
            .order_by(m.no_municipio)
        )
        result = await self._execute(stmt)
        return [(int(row.codigo), row.nome) for row in result]

    async def find_anos_disponiveis(self) -> list[int]:
        """Lista de anos do censo presentes em fato_acessibilidade."""
        return [int(v) for v in await self._find_distinct(fato_acessibilidade.c.nu_ano_censo)]

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
        result = await self._execute(stmt)
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
        result = await self._execute(stmt)
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
        f = fato_acessibilidade.c
        e = dim_entidade.c
        l = dim_tp_localizacao.c

        percentual = func.round(
            (
                func.count(case((col == 1, 1)))
                * 100.0
                / func.nullif(func.count(f.co_entidade), 0)
            ).cast(Numeric),
            2,
        )

        join_tree = (
            fato_acessibilidade
            .outerjoin(dim_entidade, f.co_entidade == e.co_entidade)
            .outerjoin(dim_tp_localizacao, e.tp_localizacao == l.co_tp_localizacao)
        )

        stmt = (
            select(
                f.nu_ano_censo.label("ano"),
                l.co_tp_localizacao.label("codigo_localizacao"),
                l.no_tp_localizacao.label("localizacao"),
                percentual.label("percentual"),
            )
            .select_from(join_tree)
            .where(
                l.no_tp_localizacao.is_not(None),
                f.nu_ano_censo.is_not(None),
            )
            .group_by(
                f.nu_ano_censo,
                l.co_tp_localizacao,
                l.no_tp_localizacao,
            )
            .order_by(f.nu_ano_censo, l.no_tp_localizacao)
        )

        result = await self._execute(stmt)
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
        result = await self._execute(stmt)
        return [row[0] for row in result]

    #P1G4
    async def find_total_escolas(
        self,
        *,
        variaveis: list[str],
        combine_or: bool = False,
        ano: int | None = None,
        municipios: list[str] | None = None,
        rede_ensino: list[str] | None = None,
        tp_localizacao: list[str] | None = None,
    ) -> TotalEscolas:
        """
        Calcula a quantidade absoluta de escolas (COUNT) que satisfazem o
        predicado de `variaveis`, aplicando os filtros dinâmicos do painel.

        - `combine_or=False`: escola precisa ter TODAS as variáveis = 1 (AND).
        - `combine_or=True`: escola conta se tiver QUALQUER variável = 1 (OR).

        Alimenta o card de KPI do painel geral (P1G4).
        """
        if not variaveis:
            raise ValueError("É necessário passar ao menos uma variável para o painel")
        metric_predicate = _build_metric_predicate(variaveis, combine_or)

        f = fato_acessibilidade.c
        e = dim_entidade.c
        m = dim_municipio.c
        d = dim_tp_dependencia.c
        l = dim_tp_localizacao.c

        # Árvore de JOINS idêntica ao padrão do restante do arquivo
        join_tree = (
            fato_acessibilidade
            .join(dim_entidade, f.co_entidade == e.co_entidade)
            .outerjoin(dim_municipio, e.co_municipio == m.co_municipio)
            .outerjoin(dim_tp_dependencia, e.tp_dependencia == d.co_tp_dependencia)
            .outerjoin(dim_tp_localizacao, e.tp_localizacao == l.co_tp_localizacao)
        )

        stmt = (
            select(func.count(f.co_entidade).label("total_escolas"))
            .select_from(join_tree)
            .where(metric_predicate)
        )

        # Aplicação dos filtros opcionais e dinâmicos do painel
        if ano is not None:
            stmt = stmt.where(f.nu_ano_censo == ano)
        if municipios:
            stmt = stmt.where(m.no_municipio.in_(municipios))
        if rede_ensino:
            stmt = stmt.where(d.no_tp_dependencia.in_(rede_ensino))
        if tp_localizacao:
            stmt = stmt.where(l.no_tp_localizacao.in_(tp_localizacao))
        
        result = await self._execute(stmt)
        row = result.first()

        return _row_to_total_escolas(row) if row else TotalEscolas(total=0)

    async def find_total_escolas_geral(
        self,
        *,
        ano: int | None = None,
        municipios: list[str] | None = None,
        rede_ensino: list[str] | None = None,
        tp_localizacao: list[str] | None = None,
    ) -> TotalEscolas:
        """
        Total absoluto de escolas no recorte (ano/município/rede/localização),
        SEM aplicar predicado de variáveis de acessibilidade. Funciona como
        denominador comparável ao card_total_escolas_com_acessibilidade.
        """
        f = fato_acessibilidade.c
        e = dim_entidade.c
        m = dim_municipio.c
        d = dim_tp_dependencia.c
        l = dim_tp_localizacao.c

        join_tree = (
            fato_acessibilidade
            .join(dim_entidade, f.co_entidade == e.co_entidade)
            .outerjoin(dim_municipio, e.co_municipio == m.co_municipio)
            .outerjoin(dim_tp_dependencia, e.tp_dependencia == d.co_tp_dependencia)
            .outerjoin(dim_tp_localizacao, e.tp_localizacao == l.co_tp_localizacao)
        )

        stmt = (
            select(func.count(f.co_entidade).label("total_escolas"))
            .select_from(join_tree)
        )

        if ano is not None:
            stmt = stmt.where(f.nu_ano_censo == ano)
        if municipios:
            stmt = stmt.where(m.no_municipio.in_(municipios))
        if rede_ensino:
            stmt = stmt.where(d.no_tp_dependencia.in_(rede_ensino))
        if tp_localizacao:
            stmt = stmt.where(l.no_tp_localizacao.in_(tp_localizacao))

        result = await self._execute(stmt)
        row = result.first()
        return _row_to_total_escolas(row) if row else TotalEscolas(total=0)

    #P1G5
    async def find_media_por_dependencia(
        self,
        *,
        variaveis: list[str],
        combine_or: bool = False,
        ano: int | None = None,
        municipios: list[str] | None = None,
        rede_ensino: list[str] | None = None,
        tp_localizacao: list[str] | None = None,
    ) -> list[AcessibilidadeDependencia]:
        """
        Calcula o percentual de escolas que satisfazem o predicado de
        `variaveis`, agrupado por tipo de dependência administrativa (P1G5).

        - `combine_or=False`: numerador conta escolas com TODAS as
          variáveis = 1 (AND).
        - `combine_or=True`: numerador conta escolas com QUALQUER
          variável = 1 (OR).
        """
        if not variaveis:
            raise ValueError("É necessário passar ao menos uma variável para o painel")
        metric_predicate = _build_metric_predicate(variaveis, combine_or)

        f = fato_acessibilidade.c
        e = dim_entidade.c
        m = dim_municipio.c
        d = dim_tp_dependencia.c
        l = dim_tp_localizacao.c

        # Agregação condicional
        percentual = func.round(
            (
                func.count(case((metric_predicate, 1)))
                * 100.0
                / func.nullif(func.count(f.co_entidade), 0)
            ).cast(Numeric),
            2,
        )

        # Joins necessários para cruzar os dados com a dimensão de dependência
        join_tree = (
            fato_acessibilidade
            .join(dim_entidade, f.co_entidade == e.co_entidade)
            .join(dim_tp_dependencia, e.tp_dependencia == d.co_tp_dependencia)
            .outerjoin(dim_municipio, e.co_municipio == m.co_municipio)
            .outerjoin(dim_tp_localizacao, e.tp_localizacao == l.co_tp_localizacao)
        )

        stmt = (
            select(
                d.co_tp_dependencia.label("codigo_dependencia"),
                d.no_tp_dependencia.label("dependencia"),
                percentual.label("percentual"),
                func.count(f.co_entidade).label("total_escolas"),
            )
            .select_from(join_tree)
            .group_by(d.co_tp_dependencia, d.no_tp_dependencia)
        )

        # Filtros dinâmicos herdados globalmente do painel
        if ano is not None:
            stmt = stmt.where(f.nu_ano_censo == ano)
        if municipios:
            stmt = stmt.where(m.no_municipio.in_(municipios))
        if rede_ensino:
            stmt = stmt.where(d.no_tp_dependencia.in_(rede_ensino))
        if tp_localizacao:
            stmt = stmt.where(l.no_tp_localizacao.in_(tp_localizacao))

        result = await self._execute(stmt)
        return [_row_to_dependencia(row) for row in result]

    async def find_media_por_localizacao(
        self,
        *,
        variaveis: list[str],
        combine_or: bool = False,
        ano: int | None = None,
        municipios: list[str] | None = None,
        rede_ensino: list[str] | None = None,
        tp_localizacao: list[str] | None = None,
    ) -> list[AcessibilidadeLocalizacao]:
        """
        Calcula o percentual de escolas que satisfazem o predicado de
        `variaveis`, agrupado por tipo de localização (Urbana/Rural).

        - `combine_or=False`: numerador conta escolas com TODAS as
          variáveis = 1 (AND).
        - `combine_or=True`: numerador conta escolas com QUALQUER
          variável = 1 (OR).
        """
        if not variaveis:
            raise ValueError("É necessário passar ao menos uma variável para o painel")
        metric_predicate = _build_metric_predicate(variaveis, combine_or)

        f = fato_acessibilidade.c
        e = dim_entidade.c
        m = dim_municipio.c
        d = dim_tp_dependencia.c
        l = dim_tp_localizacao.c

        percentual = func.round(
            (
                func.count(case((metric_predicate, 1)))
                * 100.0
                / func.nullif(func.count(f.co_entidade), 0)
            ).cast(Numeric),
            2,
        )

        join_tree = (
            fato_acessibilidade
            .join(dim_entidade, f.co_entidade == e.co_entidade)
            .join(dim_tp_localizacao, e.tp_localizacao == l.co_tp_localizacao)
            .outerjoin(dim_municipio, e.co_municipio == m.co_municipio)
            .outerjoin(dim_tp_dependencia, e.tp_dependencia == d.co_tp_dependencia)
        )

        stmt = (
            select(
                l.co_tp_localizacao.label("codigo_localizacao"),
                l.no_tp_localizacao.label("localizacao"),
                percentual.label("percentual"),
                func.count(f.co_entidade).label("total_escolas"),
            )
            .select_from(join_tree)
            .where(l.no_tp_localizacao.is_not(None))
            .group_by(l.co_tp_localizacao, l.no_tp_localizacao)
        )

        if ano is not None:
            stmt = stmt.where(f.nu_ano_censo == ano)
        if municipios:
            stmt = stmt.where(m.no_municipio.in_(municipios))
        if rede_ensino:
            stmt = stmt.where(d.no_tp_dependencia.in_(rede_ensino))
        if tp_localizacao:
            stmt = stmt.where(l.no_tp_localizacao.in_(tp_localizacao))

        result = await self._execute(stmt)
        return [_row_to_localizacao(row) for row in result]

    def _build_metricas_escola_subquery(
        self,
        *,
        variaveis: list[str],
        combine_or: bool,
        ano: int | None,
        municipios: list[str] | None,
        rede_ensino: list[str] | None,
        tp_localizacao: list[str] | None,
    ):
        """Subquery base do gráfico de métricas por escola: uma linha por
        (escola, censo) com as 17 métricas, o score e o `rn` (row_number por
        escola, censo DESC) para dedup do censo mais recente. Compartilhada por
        `find_metricas_por_escola` (lista paginada) e `count_metricas_por_escola`
        (total para a paginação)."""
        if not variaveis:
            raise ValueError("É necessário passar ao menos uma variável para o painel")
        metric_predicate = _build_metric_predicate(variaveis, combine_or)

        f = fato_acessibilidade.c
        e = dim_entidade.c
        m = dim_municipio.c
        d = dim_tp_dependencia.c
        l = dim_tp_localizacao.c

        metric_cols = [
            func.coalesce(col, 0).label(chave)
            for chave, col in METRIC_TO_FATO_COLUMN.items()
        ]
        score_expr = sum(
            (func.coalesce(col, 0) for col in METRIC_TO_FATO_COLUMN.values()),
            literal(0),
        )
        # Dedup para o censo mais recente de cada escola: sem filtro de ano,
        # uma escola aparece em vários censos — fica apenas a linha rn == 1.
        rn = (
            func.row_number()
            .over(partition_by=e.co_entidade, order_by=f.nu_ano_censo.desc())
            .label("rn")
        )

        join_tree = (
            fato_acessibilidade
            .join(dim_entidade, f.co_entidade == e.co_entidade)
            .outerjoin(dim_municipio, e.co_municipio == m.co_municipio)
            .outerjoin(dim_tp_dependencia, e.tp_dependencia == d.co_tp_dependencia)
            .outerjoin(dim_tp_localizacao, e.tp_localizacao == l.co_tp_localizacao)
        )

        base = (
            select(
                e.co_entidade.label("co_entidade"),
                e.no_entidade.label("no_entidade"),
                f.nu_ano_censo.label("nu_ano_censo"),
                *metric_cols,
                score_expr.label("score"),
                rn,
            )
            .select_from(join_tree)
            .where(metric_predicate, e.no_entidade.is_not(None))
        )

        if ano is not None:
            base = base.where(f.nu_ano_censo == ano)
        if municipios:
            base = base.where(m.no_municipio.in_(municipios))
        if rede_ensino:
            base = base.where(d.no_tp_dependencia.in_(rede_ensino))
        if tp_localizacao:
            base = base.where(l.no_tp_localizacao.in_(tp_localizacao))

        return base.subquery()

    async def find_metricas_por_escola(
        self,
        *,
        variaveis: list[str],
        combine_or: bool = False,
        ano: int | None = None,
        municipios: list[str] | None = None,
        rede_ensino: list[str] | None = None,
        tp_localizacao: list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[AcessibilidadeEscola]:
        """
        Lista escolas com o valor (0/1) de cada uma das 17 métricas de
        acessibilidade e o score (soma das 17), aplicando a mesma regra de
        filtro dos demais gráficos do painel.

        - `combine_or=False`: escola entra se tiver TODAS as variáveis = 1 (AND).
        - `combine_or=True`: escola entra se tiver QUALQUER variável = 1 (OR;
          usado quando o filtro de variáveis chega vazio).
        - Sem `ano`: dedup para o censo mais recente de cada escola
          (row_number por co_entidade, nu_ano_censo DESC).
        - `limit`/`offset`: usados pelo painel para paginar o gráfico por escola
          (ordenado por score DESC). Use `count_metricas_por_escola` para o total.
        """
        sub = self._build_metricas_escola_subquery(
            variaveis=variaveis,
            combine_or=combine_or,
            ano=ano,
            municipios=municipios,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
        )
        stmt = (
            select(sub)
            .where(sub.c.rn == 1)
            .order_by(sub.c.score.desc(), sub.c.no_entidade)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        result = await self._execute(stmt)
        return [_row_to_escola(row) for row in result.mappings()]

    async def count_metricas_por_escola(
        self,
        *,
        variaveis: list[str],
        combine_or: bool = False,
        ano: int | None = None,
        municipios: list[str] | None = None,
        rede_ensino: list[str] | None = None,
        tp_localizacao: list[str] | None = None,
    ) -> int:
        """Total de escolas (após dedup do censo mais recente) que casam com os
        filtros — denominador da paginação do gráfico por escola."""
        sub = self._build_metricas_escola_subquery(
            variaveis=variaveis,
            combine_or=combine_or,
            ano=ano,
            municipios=municipios,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
        )
        stmt = select(func.count()).select_from(sub).where(sub.c.rn == 1)
        total = await self._scalar(stmt)
        return int(total or 0)

    #P1G6
    async def find_evolucao_por_dependencia(
        self,
        metrica: str,
    ) -> list[AcessibilidadeTemporalDependencia]:
        """Percentual da métrica por (ano censo, tipo de dependência
        administrativa).

        Equivale à query original com subquery correlacionada, reescrita
        aqui via agregação condicional (COUNT(CASE WHEN...)) seguindo o
        mesmo padrão de find_evolucao_por_localizacao — generalizada
        para qualquer métrica do whitelist.
        """
        if metrica not in METRIC_TO_FATO_COLUMN:
            raise ValueError(
                f"Métrica inválida: {metrica!r}. Esperado uma de: "
                f"{sorted(METRIC_TO_FATO_COLUMN)}"
            )
        col = METRIC_TO_FATO_COLUMN[metrica]
        f = fato_acessibilidade.c
        e = dim_entidade.c
        d = dim_tp_dependencia.c

        percentual = func.round(
            (
                func.count(case((col == 1, 1)))
                * 100.0
                / func.nullif(func.count(f.co_entidade), 0)
            ).cast(Numeric),
            2,
        )

        join_tree = (
            fato_acessibilidade
            .outerjoin(dim_entidade, f.co_entidade == e.co_entidade)
            .outerjoin(dim_tp_dependencia, e.tp_dependencia == d.co_tp_dependencia)
        )

        stmt = (
            select(
                f.nu_ano_censo.label("ano"),
                d.co_tp_dependencia.label("codigo_dependencia"),
                d.no_tp_dependencia.label("dependencia"),
                percentual.label("percentual"),
            )
            .select_from(join_tree)
            .where(
                d.no_tp_dependencia.is_not(None),
                f.nu_ano_censo.is_not(None),
            )
            .group_by(
                f.nu_ano_censo,
                d.co_tp_dependencia,
                d.no_tp_dependencia,
            )
            .order_by(f.nu_ano_censo, d.no_tp_dependencia)
        )

        result = await self._execute(stmt)
        return [_row_to_temporal_dependencia(row) for row in result]


    async def find_ideb_por_entidades(
        self,
        entidades: list[tuple[int, int]],
    ) -> dict[int, dict[str, float | None]]:
        """
        Retorna {co_entidade: {"iniciais": ..., "finais": ..., "medio": ...}}
        para cada escola, buscando a nota IDEB do ano mais próximo disponível
        em cada uma das três etapas (anos iniciais, anos finais e ensino médio).
        """
        if not entidades:
            return {}

        ANOS_IDEB = [2005, 2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021, 2023]

        def ano_ideb_mais_proximo(ano_censo: int) -> int | None:
            candidatos = [a for a in ANOS_IDEB if a <= ano_censo]
            return max(candidatos) if candidatos else None

        from collections import defaultdict
        por_ano: dict[int, list[int]] = defaultdict(list)

        for co_entidade, nu_ano_censo in entidades:
            ano_ideb = ano_ideb_mais_proximo(nu_ano_censo)
            if ano_ideb is not None:
                por_ano[ano_ideb].append(co_entidade)

        # Estrutura separada por tabela
        resultado: dict[int, dict[str, float | None]] = {
            co: {"iniciais": None, "finais": None, "medio": None}
            for co, _ in entidades
        }

        tabelas = [
            (ideb_anos_iniciais_escolas, "iniciais"),
            (ideb_anos_finais_escolas,   "finais"),
            (ideb_ensino_medio_escolas,  "medio"),
        ]

        for ano_ideb, co_list in por_ano.items():
            col_name = f"IDEB({ano_ideb})"

            for table, chave in tabelas:
                if col_name not in table.c:
                    continue
                col = table.c[col_name]
                stmt = (
                    select(table.c["CO_ENTIDADE"], col)
                    .where(
                        table.c["CO_ENTIDADE"].in_(co_list),
                        col.is_not(None),
                    )
                )
                rows = (await self._execute(stmt)).fetchall()
                for co_entidade, nota in rows:
                    resultado[co_entidade][chave] = float(nota)

        return resultado

    async def find_pibid_por_entidades(
        self,
        entidades: list[tuple[int, int]],
    ) -> dict[int, dict[str, object]]:
        """
        Retorna {co_entidade: {"subprojetos": str|None, "bolsistas": int|None}}
        para cada escola, lendo silver.base_pibid no mesmo ano do censo da escola.

        Mesmo padrão de bucketing por ano de `find_ideb_por_entidades`: agrupa as
        entidades por `nu_ano_censo` e, por ano, agrega os subprojetos
        (STRING_AGG distinto) e o total de bolsistas ativos.
        """
        if not entidades:
            return {}

        from collections import defaultdict
        por_ano: dict[int, list[int]] = defaultdict(list)
        for co_entidade, nu_ano_censo in entidades:
            por_ano[nu_ano_censo].append(co_entidade)

        resultado: dict[int, dict[str, object]] = {
            co: {"subprojetos": None, "bolsistas": None} for co, _ in entidades
        }

        p = base_pibid.c
        for ano, co_list in por_ano.items():
            stmt = (
                select(
                    p.CO_ENTIDADE,
                    func.string_agg(p.SUBPROJETO.distinct(), literal(" / ")).label(
                        "subprojetos"
                    ),
                    func.max(p.QTD_BOLSISTAS_ATIVOS).label("bolsistas"),
                )
                .where(p.ANO == ano, p.CO_ENTIDADE.in_(co_list))
                .group_by(p.CO_ENTIDADE)
            )
            rows = (await self._execute(stmt)).fetchall()
            for co_entidade, subprojetos, bolsistas in rows:
                resultado[co_entidade] = {
                    "subprojetos": subprojetos,
                    "bolsistas": int(bolsistas) if bolsistas is not None else None,
                }

        return resultado