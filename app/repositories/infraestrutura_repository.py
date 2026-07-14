import asyncio
from contextlib import asynccontextmanager

from sqlalchemy import Numeric, and_, case, func, literal, or_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.infraestrutura import (
    InfraestruturaDependencia,
    InfraestruturaEscola,
    InfraestruturaLocalizacao,
    InfraestruturaMunicipio,
    InfraestruturaTemporal,
    InfraestruturaTemporalDependencia,
    TotalEscolas,
)
from app.models.infraestrutura import (
    dim_tp_dependencia,
    dim_tp_localizacao,
    fato_ideb_anos_finais_esc,
    fato_ideb_anos_iniciais_esc,
    fato_ideb_ensino_medio_esc,
    fato_pibid,
    infraestrutura_comum,
)


# Chaves das 17 métricas do notebook (cell-1), na mesma ordem do
# METRIC_ESCOLA_FIELDS do service. A coluna real na silver é o mesmo nome em
# MAIÚSCULO (case-sensitive), resolvida via `.c[chave.upper()]`.
METRIC_KEYS: list[str] = [
    "in_agua_potavel",
    "in_energia_rede_publica",
    "in_esgoto_rede_publica",
    "in_lixo_servico_coleta",
    "in_banheiro",
    "in_banheiro_pne",
    "in_biblioteca",
    "in_sala_leitura",
    "in_laboratorio_ciencias",
    "in_laboratorio_informatica",
    "in_sala_multiuso",
    "in_sala_atendimento_especial",
    "in_cozinha",
    "in_refeitorio",
    "in_quadra_esportes",
    "in_patio_coberto",
    "in_auditorio",
]

# chave (minúscula) -> coluna SQL (MAIÚSCULO) em silver.infraestrutura_comum.
METRIC_TO_COLUMN = {
    chave: infraestrutura_comum.c[chave.upper()] for chave in METRIC_KEYS
}

# Whitelist consumida pelo Literal da rota e pelo filtro do repository — protege
# contra string crua do usuário virar coluna SQL.
VARIAVEIS_INFRAESTRUTURA: dict[str, "object"] = dict(METRIC_TO_COLUMN)

# Coluna da nota do IDEB (valor observado mais recente) exposta no hover do
# gráfico por escola. O notebook (cell-13, `carregar_ideb`) lê a coluna `ideb`
# das tabelas gold.fato_ideb_*_esc — não uma coluna por ano.
IDEB_COLUMN = "ideb"


def _classificar_infraestrutura(score: int) -> str:
    """Classificação por faixa de score (notebook cell-1, `classificar_infraestrutura`).
    Note que infraestrutura NÃO tem faixa "Excelente" (diferente dos outros painéis)."""
    if score >= 12:
        return "Boa"
    if score >= 7:
        return "Média"
    if score >= 1:
        return "Baixa"
    return "Inexistente"


def _row_to_municipio(row) -> InfraestruturaMunicipio:
    return InfraestruturaMunicipio(
        codigo_municipio=int(row.codigo_municipio),
        municipio=row.municipio,
        percentual=float(row.percentual) if row.percentual is not None else 0.0,
        total_escolas=int(row.total_escolas) if row.total_escolas is not None else 0,
    )


def _row_to_temporal(row) -> InfraestruturaTemporal:
    return InfraestruturaTemporal(
        ano=int(row.ano),
        codigo_localizacao=int(row.codigo_localizacao),
        localizacao=row.localizacao,
        percentual=float(row.percentual),
    )


def _row_to_total_escolas(row) -> TotalEscolas:
    return TotalEscolas(
        total=int(row.total_escolas) if row.total_escolas is not None else 0,
    )


def _row_to_dependencia(row) -> InfraestruturaDependencia:
    return InfraestruturaDependencia(
        codigo_dependencia=int(row.codigo_dependencia),
        dependencia=row.dependencia,
        percentual=float(row.percentual) if row.percentual is not None else 0.0,
        total_escolas=int(row.total_escolas) if row.total_escolas is not None else 0,
    )


def _row_to_localizacao(row) -> InfraestruturaLocalizacao:
    return InfraestruturaLocalizacao(
        codigo_localizacao=int(row.codigo_localizacao),
        localizacao=row.localizacao,
        percentual=float(row.percentual) if row.percentual is not None else 0.0,
        total_escolas=int(row.total_escolas) if row.total_escolas is not None else 0,
    )


def _row_to_escola(row) -> InfraestruturaEscola:
    # As 17 colunas IN_ são 0/1; normaliza para binário uniforme por segurança.
    metricas = {chave: int((row[chave] or 0) > 0) for chave in METRIC_KEYS}
    return InfraestruturaEscola(
        co_entidade=int(row["co_entidade"]),
        no_entidade=row["no_entidade"],
        nu_ano_censo=int(row["nu_ano_censo"]),
        metricas=metricas,
        score=int(row["score"] or 0),
    )


def _row_to_temporal_dependencia(row) -> InfraestruturaTemporalDependencia:
    return InfraestruturaTemporalDependencia(
        ano=int(row.ano),
        codigo_dependencia=int(row.codigo_dependencia),
        dependencia=row.dependencia,
        percentual=float(row.percentual) if row.percentual is not None else 0.0,
    )


def _build_metric_predicate(variaveis: list[str], combine_or: bool):
    """Resolve nomes de variáveis para colunas SQL e combina com AND/OR.

    `combine_or=True` é usado pelo painel quando o filtro de variáveis chega
    vazio (escola conta se tiver QUALQUER variável = 1). `combine_or=False`
    mantém a semântica AND (escola precisa ter TODAS = 1). Levanta ValueError
    em nome inválido (guard de SQL injection)."""
    cols = []
    for nome in variaveis:
        col = VARIAVEIS_INFRAESTRUTURA.get(nome)
        if col is None:
            raise ValueError(
                f"Variável inválida: {nome!r}. "
                f"Esperado uma de: {sorted(VARIAVEIS_INFRAESTRUTURA)}"
            )
        cols.append(col)
    combinator = or_ if combine_or else and_
    return combinator(*[c > 0 for c in cols])


class InfraestruturaRepository:
    """
    Acessa o domínio de infraestrutura no warehouse.

    Diferente de acessibilidade/conectividade, TUDO vem de
    silver.infraestrutura_comum (não há fato/score na camada gold). A silver já
    traz NO_MUNICIPIO/TP_DEPENDENCIA/TP_LOCALIZACAO/pibid, então basta join com
    gold.dim_tp_dependencia e gold.dim_tp_localizacao para os nomes legíveis.
    """

    def __init__(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
        semaphore: asyncio.Semaphore | None = None,
    ):
        # Recebe o sessionmaker (não uma sessão única): cada query abre a sua
        # própria sessão via _execute/_scalar, então o asyncio.gather do service
        # paraleliza sem corromper a sessão. `semaphore=None` = sem limite.
        self._sessionmaker = sessionmaker
        self._semaphore = semaphore

    @asynccontextmanager
    async def _limit(self):
        """Adquire o semáforo global de warehouse ANTES de abrir a sessão."""
        if self._semaphore is None:
            yield
        else:
            async with self._semaphore:
                yield

    async def _execute(self, stmt):
        """Abre uma sessão dedicada para esta query e devolve o Result."""
        async with self._limit():
            async with self._sessionmaker() as session:
                return await session.execute(stmt)

    async def _scalar(self, stmt):
        """Como `_execute`, mas para queries escalares (ex.: COUNT)."""
        async with self._limit():
            async with self._sessionmaker() as session:
                return await session.scalar(stmt)

    @staticmethod
    def _join_tree():
        """silver.infraestrutura_comum LEFT JOIN as duas dimensões legíveis."""
        i = infraestrutura_comum.c
        d = dim_tp_dependencia.c
        l = dim_tp_localizacao.c
        return (
            infraestrutura_comum
            .outerjoin(dim_tp_dependencia, i.TP_DEPENDENCIA == d.co_tp_dependencia)
            .outerjoin(dim_tp_localizacao, i.TP_LOCALIZACAO == l.co_tp_localizacao)
        )

    @staticmethod
    def _apply_filtros(stmt, *, ano, municipios, rede_ensino, tp_localizacao, pibid):
        """Aplica os filtros dinâmicos comuns a todos os gráficos do painel."""
        i = infraestrutura_comum.c
        d = dim_tp_dependencia.c
        l = dim_tp_localizacao.c
        if ano is not None:
            stmt = stmt.where(i.NU_ANO_CENSO == ano)
        if municipios:
            stmt = stmt.where(i.NO_MUNICIPIO.in_(municipios))
        if rede_ensino:
            stmt = stmt.where(d.no_tp_dependencia.in_(rede_ensino))
        if tp_localizacao:
            stmt = stmt.where(l.no_tp_localizacao.in_(tp_localizacao))
        if pibid is not None:
            stmt = stmt.where(i.pibid == (1 if pibid else 0))
        return stmt

    async def find_media_por_municipio(
        self,
        *,
        variaveis: list[str] | None,
        combine_or: bool = False,
        ano: int | None,
        municipios: list[str] | None,
        rede_ensino: list[str] | None = None,
        tp_localizacao: list[str] | None = None,
        pibid: bool | None = None,
    ) -> list[InfraestruturaMunicipio]:
        """Percentual de escolas por município que possuem o(s) indicador(es)
        de `variaveis` = 1, sobre o total de escolas do município no recorte."""
        if not variaveis:
            raise ValueError("É necessário passar ao menos uma variável para o painel")
        metric_predicate = _build_metric_predicate(variaveis, combine_or)

        i = infraestrutura_comum.c
        percentual = func.round(
            (
                func.count(case((metric_predicate, 1)))
                * 100.0
                / func.nullif(func.count(i.CO_ENTIDADE), 0)
            ).cast(Numeric),
            2,
        )

        stmt = (
            select(
                i.CO_MUNICIPIO.label("codigo_municipio"),
                i.NO_MUNICIPIO.label("municipio"),
                percentual.label("percentual"),
                func.count(i.CO_ENTIDADE).label("total_escolas"),
            )
            .select_from(self._join_tree())
            .where(i.NO_MUNICIPIO.is_not(None))
            .group_by(i.CO_MUNICIPIO, i.NO_MUNICIPIO)
            .order_by(i.NO_MUNICIPIO)
        )
        stmt = self._apply_filtros(
            stmt,
            ano=ano,
            municipios=municipios,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
            pibid=pibid,
        )

        result = await self._execute(stmt)
        return [_row_to_municipio(row) for row in result]

    async def find_total_escolas(
        self,
        *,
        variaveis: list[str],
        combine_or: bool = False,
        ano: int | None = None,
        municipios: list[str] | None = None,
        rede_ensino: list[str] | None = None,
        tp_localizacao: list[str] | None = None,
        pibid: bool | None = None,
    ) -> TotalEscolas:
        """Quantidade absoluta de escolas (COUNT) que satisfazem o predicado de
        `variaveis`, aplicando os filtros dinâmicos do painel."""
        if not variaveis:
            raise ValueError("É necessário passar ao menos uma variável para o painel")
        metric_predicate = _build_metric_predicate(variaveis, combine_or)

        i = infraestrutura_comum.c
        stmt = (
            select(func.count(i.CO_ENTIDADE).label("total_escolas"))
            .select_from(self._join_tree())
            .where(metric_predicate)
        )
        stmt = self._apply_filtros(
            stmt,
            ano=ano,
            municipios=municipios,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
            pibid=pibid,
        )

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
        pibid: bool | None = None,
    ) -> TotalEscolas:
        """Total absoluto de escolas no recorte, SEM predicado de variáveis —
        denominador comparável ao card com infraestrutura."""
        i = infraestrutura_comum.c
        stmt = (
            select(func.count(i.CO_ENTIDADE).label("total_escolas"))
            .select_from(self._join_tree())
        )
        stmt = self._apply_filtros(
            stmt,
            ano=ano,
            municipios=municipios,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
            pibid=pibid,
        )

        result = await self._execute(stmt)
        row = result.first()
        return _row_to_total_escolas(row) if row else TotalEscolas(total=0)

    async def find_media_por_dependencia(
        self,
        *,
        variaveis: list[str],
        combine_or: bool = False,
        ano: int | None = None,
        municipios: list[str] | None = None,
        rede_ensino: list[str] | None = None,
        tp_localizacao: list[str] | None = None,
        pibid: bool | None = None,
    ) -> list[InfraestruturaDependencia]:
        """Percentual de escolas que satisfazem o predicado de `variaveis`,
        agrupado por tipo de dependência administrativa."""
        if not variaveis:
            raise ValueError("É necessário passar ao menos uma variável para o painel")
        metric_predicate = _build_metric_predicate(variaveis, combine_or)

        i = infraestrutura_comum.c
        d = dim_tp_dependencia.c
        l = dim_tp_localizacao.c

        percentual = func.round(
            (
                func.count(case((metric_predicate, 1)))
                * 100.0
                / func.nullif(func.count(i.CO_ENTIDADE), 0)
            ).cast(Numeric),
            2,
        )

        join_tree = (
            infraestrutura_comum
            .join(dim_tp_dependencia, i.TP_DEPENDENCIA == d.co_tp_dependencia)
            .outerjoin(dim_tp_localizacao, i.TP_LOCALIZACAO == l.co_tp_localizacao)
        )

        stmt = (
            select(
                d.co_tp_dependencia.label("codigo_dependencia"),
                d.no_tp_dependencia.label("dependencia"),
                percentual.label("percentual"),
                func.count(i.CO_ENTIDADE).label("total_escolas"),
            )
            .select_from(join_tree)
            .group_by(d.co_tp_dependencia, d.no_tp_dependencia)
        )
        stmt = self._apply_filtros(
            stmt,
            ano=ano,
            municipios=municipios,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
            pibid=pibid,
        )

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
        pibid: bool | None = None,
    ) -> list[InfraestruturaLocalizacao]:
        """Percentual de escolas que satisfazem o predicado de `variaveis`,
        agrupado por tipo de localização (Urbana/Rural)."""
        if not variaveis:
            raise ValueError("É necessário passar ao menos uma variável para o painel")
        metric_predicate = _build_metric_predicate(variaveis, combine_or)

        i = infraestrutura_comum.c
        d = dim_tp_dependencia.c
        l = dim_tp_localizacao.c

        percentual = func.round(
            (
                func.count(case((metric_predicate, 1)))
                * 100.0
                / func.nullif(func.count(i.CO_ENTIDADE), 0)
            ).cast(Numeric),
            2,
        )

        join_tree = (
            infraestrutura_comum
            .join(dim_tp_localizacao, i.TP_LOCALIZACAO == l.co_tp_localizacao)
            .outerjoin(dim_tp_dependencia, i.TP_DEPENDENCIA == d.co_tp_dependencia)
        )

        stmt = (
            select(
                l.co_tp_localizacao.label("codigo_localizacao"),
                l.no_tp_localizacao.label("localizacao"),
                percentual.label("percentual"),
                func.count(i.CO_ENTIDADE).label("total_escolas"),
            )
            .select_from(join_tree)
            .where(l.no_tp_localizacao.is_not(None))
            .group_by(l.co_tp_localizacao, l.no_tp_localizacao)
        )
        stmt = self._apply_filtros(
            stmt,
            ano=ano,
            municipios=municipios,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
            pibid=pibid,
        )

        result = await self._execute(stmt)
        return [_row_to_localizacao(row) for row in result]

    def _build_metricas_escola_subquery(
        self,
        *,
        variaveis: list[str] | None,
        combine_or: bool,
        ano: int | None,
        municipios: list[str] | None,
        rede_ensino: list[str] | None,
        tp_localizacao: list[str] | None,
        pibid: bool | None = None,
    ):
        """Subquery base do gráfico de métricas por escola: uma linha por
        (escola, censo) com as 17 métricas (binarizadas em 0/1), o score (0–17) e
        o `rn` (row_number por escola, censo DESC) para dedup do censo mais
        recente. Compartilhada por `find_metricas_por_escola` (lista paginada) e
        `count_metricas_por_escola` (total para a paginação)."""
        i = infraestrutura_comum.c
        d = dim_tp_dependencia.c
        l = dim_tp_localizacao.c

        def binario(col):
            return case((col > 0, 1), else_=0)

        metric_cols = [
            binario(col).label(chave) for chave, col in METRIC_TO_COLUMN.items()
        ]
        score_expr = sum(
            (binario(col) for col in METRIC_TO_COLUMN.values()),
            literal(0),
        )
        rn = (
            func.row_number()
            .over(partition_by=i.CO_ENTIDADE, order_by=i.NU_ANO_CENSO.desc())
            .label("rn")
        )

        base = (
            select(
                i.CO_ENTIDADE.label("co_entidade"),
                i.NO_ENTIDADE.label("no_entidade"),
                i.NU_ANO_CENSO.label("nu_ano_censo"),
                *metric_cols,
                score_expr.label("score"),
                rn,
            )
            .select_from(self._join_tree())
            .where(i.NO_ENTIDADE.is_not(None))
        )

        # Aplica o filtro de métricas apenas se o usuário enviou variáveis.
        if variaveis:
            metric_predicate = _build_metric_predicate(variaveis, combine_or)
            base = base.where(metric_predicate)

        base = self._apply_filtros(
            base,
            ano=ano,
            municipios=municipios,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
            pibid=pibid,
        )

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
        pibid: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[InfraestruturaEscola]:
        """Lista escolas com o valor (0/1) de cada uma das 17 métricas de
        infraestrutura e o score (soma das 17).

        - Sem `ano`: dedup para o censo mais recente de cada escola.
        - `limit`/`offset`: paginam o gráfico por escola (ordenado por score DESC)."""
        sub = self._build_metricas_escola_subquery(
            variaveis=variaveis,
            combine_or=combine_or,
            ano=ano,
            municipios=municipios,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
            pibid=pibid,
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
        pibid: bool | None = None,
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
            pibid=pibid,
        )
        stmt = select(func.count()).select_from(sub).where(sub.c.rn == 1)
        total = await self._scalar(stmt)
        return int(total or 0)

    async def find_evolucao_por_localizacao(
        self,
        metrica: str,
        pibid: bool | None = None,
    ) -> list[InfraestruturaTemporal]:
        """Percentual da métrica por (ano censo, tipo de localização), via
        agregação condicional (COUNT(CASE WHEN...))."""
        if metrica not in METRIC_TO_COLUMN:
            raise ValueError(
                f"Métrica inválida: {metrica!r}. Esperado uma de: "
                f"{sorted(METRIC_TO_COLUMN)}"
            )
        col = METRIC_TO_COLUMN[metrica]
        i = infraestrutura_comum.c
        l = dim_tp_localizacao.c

        percentual = func.round(
            (
                func.count(case((col > 0, 1)))
                * 100.0
                / func.nullif(func.count(i.CO_ENTIDADE), 0)
            ).cast(Numeric),
            2,
        )

        join_tree = infraestrutura_comum.outerjoin(
            dim_tp_localizacao, i.TP_LOCALIZACAO == l.co_tp_localizacao
        )

        stmt = (
            select(
                i.NU_ANO_CENSO.label("ano"),
                l.co_tp_localizacao.label("codigo_localizacao"),
                l.no_tp_localizacao.label("localizacao"),
                percentual.label("percentual"),
            )
            .select_from(join_tree)
            .where(
                l.no_tp_localizacao.is_not(None),
                i.NU_ANO_CENSO.is_not(None),
            )
            .group_by(
                i.NU_ANO_CENSO,
                l.co_tp_localizacao,
                l.no_tp_localizacao,
            )
            .order_by(i.NU_ANO_CENSO, l.no_tp_localizacao)
        )

        if pibid is not None:
            stmt = stmt.where(i.pibid == (1 if pibid else 0))

        result = await self._execute(stmt)
        return [_row_to_temporal(row) for row in result]

    async def find_evolucao_por_dependencia(
        self,
        metrica: str,
        pibid: bool | None = None,
    ) -> list[InfraestruturaTemporalDependencia]:
        """Percentual da métrica por (ano censo, tipo de dependência
        administrativa). Via agregação condicional (COUNT(CASE WHEN...))."""
        if metrica not in METRIC_TO_COLUMN:
            raise ValueError(
                f"Métrica inválida: {metrica!r}. Esperado uma de: "
                f"{sorted(METRIC_TO_COLUMN)}"
            )
        col = METRIC_TO_COLUMN[metrica]
        i = infraestrutura_comum.c
        d = dim_tp_dependencia.c

        percentual = func.round(
            (
                func.count(case((col > 0, 1)))
                * 100.0
                / func.nullif(func.count(i.CO_ENTIDADE), 0)
            ).cast(Numeric),
            2,
        )

        join_tree = infraestrutura_comum.outerjoin(
            dim_tp_dependencia, i.TP_DEPENDENCIA == d.co_tp_dependencia
        )

        stmt = (
            select(
                i.NU_ANO_CENSO.label("ano"),
                d.co_tp_dependencia.label("codigo_dependencia"),
                d.no_tp_dependencia.label("dependencia"),
                percentual.label("percentual"),
            )
            .select_from(join_tree)
            .where(
                d.no_tp_dependencia.is_not(None),
                i.NU_ANO_CENSO.is_not(None),
            )
            .group_by(
                i.NU_ANO_CENSO,
                d.co_tp_dependencia,
                d.no_tp_dependencia,
            )
            .order_by(i.NU_ANO_CENSO, d.no_tp_dependencia)
        )

        if pibid is not None:
            stmt = stmt.where(i.pibid == (1 if pibid else 0))

        result = await self._execute(stmt)
        return [_row_to_temporal_dependencia(row) for row in result]

    async def find_ideb_por_entidades(
        self,
        entidades: list[int],
    ) -> dict[int, dict[str, float | None]]:
        """Retorna {co_entidade: {"iniciais": ..., "finais": ..., "medio": ...}}
        lendo a coluna `ideb` (`IDEB_COLUMN`) nas três etapas do gold, igual ao
        notebook (cell-13, `carregar_ideb`)."""
        if not entidades:
            return {}

        resultado: dict[int, dict[str, float | None]] = {
            co: {"iniciais": None, "finais": None, "medio": None} for co in entidades
        }

        tabelas = [
            (fato_ideb_anos_iniciais_esc, "iniciais"),
            (fato_ideb_anos_finais_esc, "finais"),
            (fato_ideb_ensino_medio_esc, "medio"),
        ]

        for table, chave in tabelas:
            col = table.c[IDEB_COLUMN]
            stmt = (
                select(table.c.co_entidade, col)
                .where(table.c.co_entidade.in_(entidades), col.is_not(None))
            )
            rows = (await self._execute(stmt)).fetchall()
            for co_entidade, nota in rows:
                if co_entidade in resultado:
                    resultado[co_entidade][chave] = float(nota)

        return resultado

    async def find_pibid_por_entidades(
        self,
        entidades: list[int],
    ) -> dict[int, dict[str, object]]:
        """Retorna {co_entidade: {"subprojetos": str|None, "bolsistas": int|None}}
        lendo gold.fato_pibid (sem coluna de ano: agrega por escola numa única
        query — STRING_AGG distinto dos subprojetos + MAX de bolsistas ativos)."""
        if not entidades:
            return {}

        resultado: dict[int, dict[str, object]] = {
            co: {"subprojetos": None, "bolsistas": None} for co in entidades
        }

        p = fato_pibid.c
        stmt = (
            select(
                p.co_entidade,
                func.string_agg(p.subprojeto.distinct(), literal(" / ")).label(
                    "subprojetos"
                ),
                func.max(p.qtd_bolsistas_ativos).label("bolsistas"),
            )
            .where(p.co_entidade.in_(entidades))
            .group_by(p.co_entidade)
        )
        rows = (await self._execute(stmt)).fetchall()
        for co_entidade, subprojetos, bolsistas in rows:
            resultado[co_entidade] = {
                "subprojetos": subprojetos,
                "bolsistas": int(bolsistas) if bolsistas is not None else None,
            }

        return resultado

    async def find_pontos_mapa_raw(
        self,
        ano: int | None,
        variaveis: list[str] | None,
        pibid: bool | None = None,
    ) -> list[dict]:
        """Lê silver.infraestrutura_comum e calcula, on-the-fly, o score (0–17,
        soma binária das 17 métricas) e a classificação (Boa/Média/Baixa/
        Inexistente) — não existe tabela pré-computada gold para infraestrutura
        (notebook cell-9).

        - As 17 métricas saem com COALESCE(col, 0): NULL vira 0.
        - `ano`: filtra `NU_ANO_CENSO`.
        - `variaveis`: AND sobre as 17 métricas (a escola precisa ter TODAS as
          colunas indicadas > 0). Validado contra `VARIAVEIS_INFRAESTRUTURA`.
        """
        i = infraestrutura_comum.c
        stmt = select(
            i.CO_ENTIDADE.label("co_entidade"),
            i.NU_ANO_CENSO.label("nu_ano_censo"),
            i.pibid.label("pibid"),
            *(
                func.coalesce(col, 0).label(chave)
                for chave, col in METRIC_TO_COLUMN.items()
            ),
        )

        if ano is not None:
            stmt = stmt.where(i.NU_ANO_CENSO == ano)
        if pibid is not None:
            stmt = stmt.where(i.pibid == (1 if pibid else 0))
        if variaveis:
            for nome in variaveis:
                col = VARIAVEIS_INFRAESTRUTURA.get(nome)
                if col is None:
                    raise ValueError(f"Variável inválida: {nome!r}")
                stmt = stmt.where(col > 0)

        result = await self._execute(stmt)
        pontos: list[dict] = []
        for r in result.mappings():
            metricas = {chave: int((r[chave] or 0) > 0) for chave in METRIC_KEYS}
            score = sum(metricas.values())
            pontos.append(
                {
                    "co_entidade": int(r["co_entidade"]),
                    "nu_ano_censo": int(r["nu_ano_censo"]),
                    "pibid": int(r["pibid"]) if r["pibid"] is not None else None,
                    **{chave: float(metricas[chave]) for chave in METRIC_KEYS},
                    "score_infraestrutura": score,
                    "classificacao_infraestrutura": _classificar_infraestrutura(score),
                }
            )
        return pontos
