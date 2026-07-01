import asyncio
from contextlib import asynccontextmanager

from sqlalchemy import Numeric, and_, case, func, literal, or_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.conectividade import (
    ConectividadeDependencia,
    ConectividadeEscola,
    ConectividadeLocalizacao,
    ConectividadeMunicipio,
    ConectividadeTemporal,
    ConectividadeTemporalDependencia,
    TotalEscolas,
)
from app.models.conectividade import (
    # gold — painéis
    dim_entidade,
    dim_municipio,
    dim_tp_dependencia,
    dim_tp_localizacao,
    fato_conectividade,
    fato_ideb_anos_finais_esc,
    fato_ideb_anos_iniciais_esc,
    fato_ideb_ensino_medio_esc,
    fato_pibid,
    # gold — mapa (score/classificação pré-computados)
    fato_score_conectividade,
)


# Conjunto único das 17 métricas do notebook (cell-12), na mesma ordem. Fonte de
# verdade dos painéis: predicado de filtro, subquery por escola/score, validação
# da análise temporal e `_row_to_escola`. Colunas qt_*/tp_rede_local são tratadas
# como binário (> 0 = possui) onde entram em contagem/score.
METRIC_TO_FATO_COLUMN = {
    "in_internet": fato_conectividade.c.in_internet,
    "in_internet_alunos": fato_conectividade.c.in_internet_alunos,
    "in_internet_administrativo": fato_conectividade.c.in_internet_administrativo,
    "in_internet_aprendizagem": fato_conectividade.c.in_internet_aprendizagem,
    "in_internet_comunidade": fato_conectividade.c.in_internet_comunidade,
    "in_banda_larga": fato_conectividade.c.in_banda_larga,
    "in_acesso_internet_computador": fato_conectividade.c.in_acesso_internet_computador,
    "in_aces_internet_disp_pessoais": fato_conectividade.c.in_aces_internet_disp_pessoais,
    "tp_rede_local": fato_conectividade.c.tp_rede_local,
    "in_computador": fato_conectividade.c.in_computador,
    "in_desktop_aluno": fato_conectividade.c.in_desktop_aluno,
    "qt_desktop_aluno": fato_conectividade.c.qt_desktop_aluno,
    "in_comp_portatil_aluno": fato_conectividade.c.in_comp_portatil_aluno,
    "qt_comp_portatil_aluno": fato_conectividade.c.qt_comp_portatil_aluno,
    "in_tablet_aluno": fato_conectividade.c.in_tablet_aluno,
    "qt_tablet_aluno": fato_conectividade.c.qt_tablet_aluno,
    "in_redes_sociais": fato_conectividade.c.in_redes_sociais,
}


# Whitelist de variáveis dos painéis (gold). Consumida pelo Literal da rota e pelo
# filtro do repository — protege contra string crua do usuário virar coluna SQL.
VARIAVEIS_CONECTIVIDADE: dict[str, "object"] = dict(METRIC_TO_FATO_COLUMN)


# Whitelist do mapa: as 17 colunas de métrica de fato_score_conectividade (mesmo
# conjunto gold dos painéis). Usada só para validar/filtrar o parâmetro `variaveis`
# do /mapa contra a tabela pré-computada.
VARIAVEIS_CONECTIVIDADE_MAPA: dict[str, "object"] = {
    nome: fato_score_conectividade.c[nome] for nome in METRIC_TO_FATO_COLUMN
}


# Ano fixo da nota do IDEB exposta no hover do gráfico por escola — espelha
# ANO_IDEB=2023 do notebook (cell-12). Lido diretamente de uma coluna por etapa.
IDEB_YEAR_COLUMN = "ideb_2023"


def _row_to_municipio(row) -> ConectividadeMunicipio:
    return ConectividadeMunicipio(
        codigo_municipio=int(row.codigo_municipio),
        municipio=row.municipio,
        percentual=float(row.percentual) if row.percentual is not None else 0.0,
        total_escolas=int(row.total_escolas) if row.total_escolas is not None else 0,
    )


def _row_to_temporal(row) -> ConectividadeTemporal:
    return ConectividadeTemporal(
        ano=int(row.ano),
        codigo_localizacao=int(row.codigo_localizacao),
        localizacao=row.localizacao,
        percentual=float(row.percentual),
    )


def _row_to_total_escolas(row) -> TotalEscolas:
    return TotalEscolas(
        total=int(row.total_escolas) if row.total_escolas is not None else 0,
    )


def _row_to_dependencia(row) -> ConectividadeDependencia:
    return ConectividadeDependencia(
        codigo_dependencia=int(row.codigo_dependencia),
        dependencia=row.dependencia,
        percentual=float(row.percentual) if row.percentual is not None else 0.0,
        total_escolas=int(row.total_escolas) if row.total_escolas is not None else 0,
    )


def _row_to_localizacao(row) -> ConectividadeLocalizacao:
    return ConectividadeLocalizacao(
        codigo_localizacao=int(row.codigo_localizacao),
        localizacao=row.localizacao,
        percentual=float(row.percentual) if row.percentual is not None else 0.0,
        total_escolas=int(row.total_escolas) if row.total_escolas is not None else 0,
    )


def _row_to_escola(row) -> ConectividadeEscola:
    # Binário uniforme: qt_*/tp_rede_local podem vir > 1, normaliza para 0/1.
    metricas = {chave: int((row[chave] or 0) > 0) for chave in METRIC_TO_FATO_COLUMN}
    return ConectividadeEscola(
        co_entidade=int(row["co_entidade"]),
        no_entidade=row["no_entidade"],
        nu_ano_censo=int(row["nu_ano_censo"]),
        metricas=metricas,
        score=int(row["score"] or 0),
    )


def _row_to_temporal_dependencia(row) -> ConectividadeTemporalDependencia:
    return ConectividadeTemporalDependencia(
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
        col = VARIAVEIS_CONECTIVIDADE.get(nome)
        if col is None:
            raise ValueError(
                f"Variável inválida: {nome!r}. "
                f"Esperado uma de: {sorted(VARIAVEIS_CONECTIVIDADE)}"
            )
        cols.append(col)
    combinator = or_ if combine_or else and_
    # Binário uniforme (> 0): colunas in_ 0/1 seguem equivalentes; qt_*/tp_rede_local
    # contam como "possui" quando > 0.
    return combinator(*[c > 0 for c in cols])


class ConectividadeRepository:
    """
    Acessa o domínio de conectividade no warehouse.

    Painéis: gold.fato_conectividade (uma linha por escola por ano censo) +
    dimensões gold. Mapa: gold.fato_score_conectividade (score/classificação
    pré-computados, sem joins). Owner do mart: squad de dados.
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
        """Abre uma sessão dedicada para esta query e devolve o Result."""
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
        pibid: bool | None = None,
    ) -> list[ConectividadeMunicipio]:
        """
        Percentual de escolas por município que possuem o(s) indicador(es)
        de `variaveis` = 1, sobre o total de escolas do município no recorte.
        """
        if not variaveis:
            raise ValueError("É necessário passar ao menos uma variável para o painel")
        metric_predicate = _build_metric_predicate(variaveis, combine_or)

        f = fato_conectividade.c
        e = dim_entidade.c
        m = dim_municipio.c
        d = dim_tp_dependencia.c
        l = dim_tp_localizacao.c

        f_sub = fato_conectividade.alias("f_sub")
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
        if pibid is not None:
            denom_filters.append(f_sub.c.pibid == (1 if pibid else 0))

        denominador = (
            select(func.count(f_sub.c.co_entidade))
            .select_from(denom_join)
            .where(*denom_filters)
            .correlate(fato_conectividade, dim_entidade)
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
            fato_conectividade
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
        if pibid is not None:
            stmt = stmt.where(f.pibid == (1 if pibid else 0))

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
        """Lista de anos do censo presentes em fato_conectividade."""
        return [int(v) for v in await self._find_distinct(fato_conectividade.c.nu_ano_censo)]

    # As 17 colunas de métrica de fato_score_conectividade vêm como Numeric com
    # NULL possível no banco — selecionadas via COALESCE(col, 0) para sair como 0,
    # coerente com o cálculo do score (NULL conta como 0).
    _MAPA_METRIC_COLS = tuple(METRIC_TO_FATO_COLUMN)

    # IDEB 2023 pré-computado em gold.fato_score_conectividade (escola e município).
    # Diferente das métricas: sai como float|None (sem COALESCE), pois nota 0 seria
    # enganosa — NULL significa "sem nota", igual a find_ideb_por_entidades.
    _MAPA_IDEB_COLS = (
        "ideb_2023_anos_iniciais",
        "ideb_2023_anos_finais",
        "ideb_2023_ensino_medio",
        "ideb_2023_anos_iniciais_mun",
        "ideb_2023_anos_finais_mun",
        "ideb_2023_ensino_medio_mun",
    )

    async def find_pontos_mapa_raw(
        self,
        ano: int | None,
        variaveis: list[str] | None,
        pibid: bool | None = None,
    ) -> list[dict]:
        """Lê a tabela pré-computada gold.fato_score_conectividade (sem joins) e
        devolve list[dict] direto para a rota /mapa — score e classificação já
        vêm prontos do pipeline de dados.

        - As 17 métricas saem com COALESCE(col, 0): NULL vira 0.
        - `ano`: filtra `nu_ano_censo`.
        - `variaveis`: AND sobre as 17 métricas gold (a escola precisa ter TODAS
          as colunas indicadas > 0). Validado contra `VARIAVEIS_CONECTIVIDADE_MAPA`.
        """
        c = fato_score_conectividade.c
        stmt = select(
            c.co_entidade,
            c.nu_ano_censo,
            c.pibid,
            *(func.coalesce(c[nome], 0).label(nome) for nome in self._MAPA_METRIC_COLS),
            c.score_conectividade,
            c.classificacao_conectividade,
            *(c[nome] for nome in self._MAPA_IDEB_COLS),
            c.dt_carga,
        )

        if ano is not None:
            stmt = stmt.where(c.nu_ano_censo == ano)
        if pibid is not None:
            stmt = stmt.where(c.pibid == (1 if pibid else 0))
        if variaveis:
            for nome in variaveis:
                col = VARIAVEIS_CONECTIVIDADE_MAPA.get(nome)
                if col is None:
                    raise ValueError(f"Variável inválida: {nome!r}")
                stmt = stmt.where(col > 0)

        result = await self._execute(stmt)
        return [
            {
                "co_entidade": int(r["co_entidade"]),
                "nu_ano_censo": int(r["nu_ano_censo"]),
                "pibid": int(r["pibid"]) if r["pibid"] is not None else None,
                **{nome: float(r[nome]) for nome in self._MAPA_METRIC_COLS},
                "score_conectividade": int(r["score_conectividade"]),
                "classificacao_conectividade": r["classificacao_conectividade"],
                **{
                    nome: (float(r[nome]) if r[nome] is not None else None)
                    for nome in self._MAPA_IDEB_COLS
                },
                "dt_carga": (
                    r["dt_carga"].isoformat() if r["dt_carga"] is not None else None
                ),
            }
            for r in result.mappings()
        ]

    async def find_evolucao_por_localizacao(
        self,
        metrica: str,
        pibid: bool | None = None,
    ) -> list[ConectividadeTemporal]:
        """Percentual da métrica por (ano, tipo de localização).

        Denominador é o total de entidades naquele ano + tipo de localização;
        numerador é o total com a métrica = 1. Escrita via agregação condicional
        (COUNT(CASE WHEN...)) para evitar a subquery correlacionada.
        """
        if metrica not in METRIC_TO_FATO_COLUMN:
            raise ValueError(
                f"Métrica inválida: {metrica!r}. Esperado uma de: "
                f"{sorted(METRIC_TO_FATO_COLUMN)}"
            )
        col = METRIC_TO_FATO_COLUMN[metrica]
        f = fato_conectividade.c
        e = dim_entidade.c
        l = dim_tp_localizacao.c

        percentual = func.round(
            (
                func.count(case((col > 0, 1)))
                * 100.0
                / func.nullif(func.count(f.co_entidade), 0)
            ).cast(Numeric),
            2,
        )

        join_tree = (
            fato_conectividade
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

        if pibid is not None:
            stmt = stmt.where(f.pibid == (1 if pibid else 0))

        result = await self._execute(stmt)
        return [_row_to_temporal(row) for row in result]

    async def _find_distinct(self, column) -> list:
        """SELECT DISTINCT column WHERE column IS NOT NULL ORDER BY column."""
        stmt = (
            select(column)
            .where(column.is_not(None))
            .distinct()
            .order_by(column)
        )
        result = await self._execute(stmt)
        return [row[0] for row in result]

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
        """
        Calcula a quantidade absoluta de escolas (COUNT) que satisfazem o
        predicado de `variaveis`, aplicando os filtros dinâmicos do painel.
        """
        if not variaveis:
            raise ValueError("É necessário passar ao menos uma variável para o painel")
        metric_predicate = _build_metric_predicate(variaveis, combine_or)

        f = fato_conectividade.c
        e = dim_entidade.c
        m = dim_municipio.c
        d = dim_tp_dependencia.c
        l = dim_tp_localizacao.c

        join_tree = (
            fato_conectividade
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

        if ano is not None:
            stmt = stmt.where(f.nu_ano_censo == ano)
        if municipios:
            stmt = stmt.where(m.no_municipio.in_(municipios))
        if rede_ensino:
            stmt = stmt.where(d.no_tp_dependencia.in_(rede_ensino))
        if tp_localizacao:
            stmt = stmt.where(l.no_tp_localizacao.in_(tp_localizacao))
        if pibid is not None:
            stmt = stmt.where(f.pibid == (1 if pibid else 0))

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
        """
        Total absoluto de escolas no recorte (ano/município/rede/localização),
        SEM aplicar predicado de variáveis de conectividade. Funciona como
        denominador comparável ao card_total_escolas_com_conectividade.
        """
        f = fato_conectividade.c
        e = dim_entidade.c
        m = dim_municipio.c
        d = dim_tp_dependencia.c
        l = dim_tp_localizacao.c

        join_tree = (
            fato_conectividade
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
        if pibid is not None:
            stmt = stmt.where(f.pibid == (1 if pibid else 0))

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
    ) -> list[ConectividadeDependencia]:
        """
        Calcula o percentual de escolas que satisfazem o predicado de
        `variaveis`, agrupado por tipo de dependência administrativa.
        """
        if not variaveis:
            raise ValueError("É necessário passar ao menos uma variável para o painel")
        metric_predicate = _build_metric_predicate(variaveis, combine_or)

        f = fato_conectividade.c
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
            fato_conectividade
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

        if ano is not None:
            stmt = stmt.where(f.nu_ano_censo == ano)
        if municipios:
            stmt = stmt.where(m.no_municipio.in_(municipios))
        if rede_ensino:
            stmt = stmt.where(d.no_tp_dependencia.in_(rede_ensino))
        if tp_localizacao:
            stmt = stmt.where(l.no_tp_localizacao.in_(tp_localizacao))
        if pibid is not None:
            stmt = stmt.where(f.pibid == (1 if pibid else 0))

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
    ) -> list[ConectividadeLocalizacao]:
        """
        Calcula o percentual de escolas que satisfazem o predicado de
        `variaveis`, agrupado por tipo de localização (Urbana/Rural).
        """
        if not variaveis:
            raise ValueError("É necessário passar ao menos uma variável para o painel")
        metric_predicate = _build_metric_predicate(variaveis, combine_or)

        f = fato_conectividade.c
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
            fato_conectividade
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
        if pibid is not None:
            stmt = stmt.where(f.pibid == (1 if pibid else 0))

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

        f = fato_conectividade.c
        e = dim_entidade.c
        m = dim_municipio.c
        d = dim_tp_dependencia.c
        l = dim_tp_localizacao.c

        # Binário uniforme (qt_*/tp_rede_local viram 0/1 via > 0). Cada métrica
        # conta 1 no score, mantendo o intervalo 0–17.
        def binario(col):
            return case((col > 0, 1), else_=0)

        metric_cols = [
            binario(col).label(chave) for chave, col in METRIC_TO_FATO_COLUMN.items()
        ]
        score_expr = sum(
            (binario(col) for col in METRIC_TO_FATO_COLUMN.values()),
            literal(0),
        )
        rn = (
            func.row_number()
            .over(partition_by=e.co_entidade, order_by=f.nu_ano_censo.desc())
            .label("rn")
        )

        join_tree = (
            fato_conectividade
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
            .where(e.no_entidade.is_not(None))
        )

        # Aplica-se o filtro de métricas apenas se o utilizador enviou variáveis
        if variaveis:
            metric_predicate = _build_metric_predicate(variaveis, combine_or)
            base = base.where(metric_predicate)

        if ano is not None:
            base = base.where(f.nu_ano_censo == ano)
        if municipios:
            base = base.where(m.no_municipio.in_(municipios))
        if rede_ensino:
            base = base.where(d.no_tp_dependencia.in_(rede_ensino))
        if tp_localizacao:
            base = base.where(l.no_tp_localizacao.in_(tp_localizacao))
        if pibid is not None:
            base = base.where(f.pibid == (1 if pibid else 0))

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
    ) -> list[ConectividadeEscola]:
        """
        Lista escolas com o valor (0/1) de cada uma das 17 métricas de
        conectividade e o score (soma das 17), aplicando a mesma regra de
        filtro dos demais gráficos do painel.

        - Sem `ano`: dedup para o censo mais recente de cada escola.
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

    async def find_evolucao_por_dependencia(
        self,
        metrica: str,
        pibid: bool | None = None,
    ) -> list[ConectividadeTemporalDependencia]:
        """Percentual da métrica por (ano censo, tipo de dependência
        administrativa). Via agregação condicional (COUNT(CASE WHEN...))."""
        if metrica not in METRIC_TO_FATO_COLUMN:
            raise ValueError(
                f"Métrica inválida: {metrica!r}. Esperado uma de: "
                f"{sorted(METRIC_TO_FATO_COLUMN)}"
            )
        col = METRIC_TO_FATO_COLUMN[metrica]
        f = fato_conectividade.c
        e = dim_entidade.c
        d = dim_tp_dependencia.c

        percentual = func.round(
            (
                func.count(case((col > 0, 1)))
                * 100.0
                / func.nullif(func.count(f.co_entidade), 0)
            ).cast(Numeric),
            2,
        )

        join_tree = (
            fato_conectividade
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

        if pibid is not None:
            stmt = stmt.where(f.pibid == (1 if pibid else 0))

        result = await self._execute(stmt)
        return [_row_to_temporal_dependencia(row) for row in result]

    async def find_ideb_por_entidades(
        self,
        entidades: list[int],
    ) -> dict[int, dict[str, float | None]]:
        """
        Retorna {co_entidade: {"iniciais": ..., "finais": ..., "medio": ...}}
        para cada escola, lendo a coluna de ano fixo (`IDEB_YEAR_COLUMN`) em cada
        uma das três etapas do gold, igual ao notebook (cell-12, ANO_IDEB=2023).
        """
        if not entidades:
            return {}

        resultado: dict[int, dict[str, float | None]] = {
            co: {"iniciais": None, "finais": None, "medio": None} for co in entidades
        }

        tabelas = [
            (fato_ideb_anos_iniciais_esc, "iniciais"),
            (fato_ideb_anos_finais_esc,   "finais"),
            (fato_ideb_ensino_medio_esc,  "medio"),
        ]

        for table, chave in tabelas:
            col = table.c[IDEB_YEAR_COLUMN]
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
        """
        Retorna {co_entidade: {"subprojetos": str|None, "bolsistas": int|None}}
        para cada escola, lendo gold.fato_pibid. A tabela gold não tem coluna de
        ano: agrega por escola numa única query (STRING_AGG distinto dos
        subprojetos + MAX de bolsistas ativos), igual ao notebook (cell-12).
        """
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
