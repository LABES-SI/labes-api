from sqlalchemy import Numeric, case, func, literal, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.acessibilidade import (
    AcessibilidadeMapaPonto,
    AcessibilidadeMunicipio,
    AcessibilidadeTemporal,
    #P1G4
    TotalEscolas,
    #P1G5
    AcessibilidadeDependencia
)
from app.models.acessibilidade import (
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


METRIC_TO_FATO_COLUMN = {
    "in_acessibilidade_rampas": fato_acessibilidade.c.in_acessibilidade_rampas,
    "in_acessibilidade_corrimao": fato_acessibilidade.c.in_acessibilidade_corrimao,
    "in_acessibilidade_elevador": fato_acessibilidade.c.in_acessibilidade_elevador,
    "in_acessibilidade_pisos_tateis": fato_acessibilidade.c.in_acessibilidade_pisos_tateis,
    "in_acessibilidade_vao_livre": fato_acessibilidade.c.in_acessibilidade_vao_livre,
    "in_banheiro_pne": fato_acessibilidade.c.in_banheiro_pne,
}


def _row_to_municipio(row) -> AcessibilidadeMunicipio:
    return AcessibilidadeMunicipio(
        codigo_municipio=int(row.codigo_municipio),
        municipio=row.municipio,
        percentual=float(row.percentual) if row.percentual is not None else 0.0,
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
    )

class AcessibilidadeRepository:
    """
    Acessa o domínio de acessibilidade no warehouse silver.

    Tabela fato: silver.fato_acessibilidade (uma linha por escola por
    ano censo) + dimensões (entidade, município, tp_dependência,
    tp_localização). Owner do mart: squad de dados.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_media_por_municipio(
        self,
        *,
        variaveis: list[str] | None,
        ano: int | None,
        municipios: list[str] | None,
        rede_ensino: list[str] | None = None,
        tp_localizacao: list[str] | None = None,
    ) -> list[AcessibilidadeMunicipio]:
        """
        Percentual de escolas por município que possuem o indicador
        `metrica` = 1, sobre o total de escolas do município no recorte.

        - Numerador: COUNT(co_entidade) com `metrica` = 1 + filtros de população.
        - Denominador (subconsulta correlacionada): COUNT(co_entidade) do
          mesmo município/ano (+ rede_ensino/tp_localização se passados),
          sem o filtro da métrica.
        - `municipios` filtra apenas a saída (cada município é independente
          via correlação `e_sub.co_municipio = e.co_municipio`).
        """
        # `variaveis` is a list of indicator column names (AND semantics).
        if not variaveis:
            raise ValueError("É necessário passar ao menos uma variável para o painel")
        metric_cols = []
        for nome in variaveis:
            col = VARIAVEIS_ACESSIBILIDADE.get(nome)
            if col is None:
                raise ValueError(f"Variável inválida: {nome!r}. Esperado uma de: {sorted(VARIAVEIS_ACESSIBILIDADE)}")
            metric_cols.append(col)

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
            )
            .select_from(join_tree)
            .where(*[c == 1 for c in metric_cols], m.no_municipio.is_not(None))
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

        result = await self._session.execute(stmt)
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
        result = await self._session.execute(stmt)
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

    #P1G4
    async def find_total_escolas(
        self,
        *,
        metrica: str,
        ano: int | None = None,
        municipios: list[str] | None = None,
        rede_ensino: list[str] | None = None,
        tp_localizacao: list[str] | None = None,
    ) -> TotalEscolas:
        """
        Calcula a quantidade absoluta de escolas (COUNT) que possuem o indicador
        de métrica selecionada igual a 1, aplicando os filtros dinâmicos do painel.

        Alimenta o card de KPI do painel geral (P1G4)
        """
        # Normaliza nomes curtos do front (ex: "rampas") para o padrão das colunas (ex: "in_acessibilidade_rampas")
        # CORREÇÃO (P1G5): Ajustado de 'rampas' estático para '{metrica}' dinâmico 
        # para evitar que os cards de KPI mostrassem apenas dados de rampas.
        nome_coluna = metrica if metrica.startswith("in_") else f"in_acessibilidade_{metrica}"
        if metrica == "banheiro_pne":
            nome_coluna = "in_banheiro_pne"

        if nome_coluna not in METRIC_TO_FATO_COLUMN:
            raise ValueError(
                f"Métrica inválida: {metrica!r}. Esperando um de: "
                f"{sorted(METRIC_TO_FATO_COLUMN.keys())}"
            )
        
        col = METRIC_TO_FATO_COLUMN[nome_coluna]
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

        # Montagem do SELECT COUNT(*) executando o filtro da métrica ativa (=1)
        stmt = (
            select(func.count(f.co_entidade).label("total_escolas"))
            .select_from(join_tree)
            .where(col == 1)
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
        
        result = await self._session.execute(stmt)
        row = result.first()

        return _row_to_total_escolas(row) if row else TotalEscolas(total=0)
    
    #P1G5
    async def find_media_por_dependencia(
        self,
        *,
        metrica: str,
        ano: int | None = None,
        municipios: list[str] | None = None,
        rede_ensino: list[str] | None = None,
        tp_localizacao: list[str] | None = None,
    ) -> list[AcessibilidadeDependencia]:
        """
        Calcula o percentual de escolas que possuem a métrica de acessibilidade
        igual a 1, agrupado por tipo de dependência administrativa (P1G5).
        """
        # Normaliza nomes curtos do front para o padrão das colunas
        nome_coluna = metrica if metrica.startswith("in_") else f"in_acessibilidade_{metrica}"
        if metrica == "banheiro_pne":
            nome_coluna = "in_banheiro_pne"

        if nome_coluna not in METRIC_TO_FATO_COLUMN:
            raise ValueError(f"Métrica inválida: {metrica!r}")
            
        col = METRIC_TO_FATO_COLUMN[nome_coluna]
        f = fato_acessibilidade.c
        e = dim_entidade.c
        m = dim_municipio.c
        d = dim_tp_dependencia.c
        l = dim_tp_localizacao.c

        # Agregação condicional
        percentual = func.round(
            (
                func.count(case((col == 1, 1)))
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

        result = await self._session.execute(stmt)
        return [_row_to_dependencia(row) for row in result]
