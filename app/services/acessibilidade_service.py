import asyncio
import json

import pandas as pd
import plotly.graph_objects as go

from app.domain.acessibilidade import (
    AcessibilidadeEscola,
    AcessibilidadeLocalizacao,
    AcessibilidadeMunicipio,
    AcessibilidadeTemporal,
    TotalEscolas,
    AcessibilidadeDependencia,
    AcessibilidadeTemporalDependencia,
)
from app.repositories.acessibilidade_repository import AcessibilidadeRepository
from app.services.chart_factory import ChartFactory


# (chave, rótulo, cor, grupo) — fonte única das 15 métricas do notebook (cell-10):
# define ordem, cores e agrupamento da legenda (Infraestrutura × Profissionais) do
# gráfico de métricas por escola. METRIC_FIELDS é derivado daqui para alimentar o
# catálogo de filtros e a validação de variáveis.
METRIC_ESCOLA_FIELDS: list[tuple[str, str, str, str]] = [
    ("in_acessibilidade_rampas",        "Rampas",                       "#54A24B", "Infraestrutura"),
    ("in_acessibilidade_corrimao",      "Corrimão",                     "#E45756", "Infraestrutura"),
    ("in_acessibilidade_elevador",      "Elevador",                     "#72B7B2", "Infraestrutura"),
    ("in_acessibilidade_pisos_tateis",  "Pisos táteis",                 "#EECA3B", "Infraestrutura"),
    ("in_acessibilidade_vao_livre",     "Vão livre",                    "#B279A2", "Infraestrutura"),
    ("qt_salas_utilizadas_acessiveis",  "Salas acessíveis",             "#FF9DA6", "Infraestrutura"),
    ("in_acessibilidade_inexistente",   "Outros",                       "#444444", "Infraestrutura"),
    ("in_acessibilidade_sinal_tatil",   "Sinal tátil",                  "#1F77B4", "Infraestrutura"),
    ("in_acessibilidade_sinal_sonoro",  "Sinal sonoro",                 "#9D755D", "Infraestrutura"),
    ("in_acessibilidade_sinal_visual",  "Sinal visual",                 "#FF9DA6", "Infraestrutura"),
    ("tp_aee",                          "AEE",                          "#D67195", "Infraestrutura"),
    ("in_sala_atendimento_especial",    "Sala de atendimento especial", "#4C78A8", "Infraestrutura"),
    ("in_reserva_pcd",                  "Reserva PCD",                  "#F58518", "Infraestrutura"),
    ("qt_prof_psicologo",               "Psicólogo",                    "#5254A3", "Profissionais"),
    ("qt_prof_assist_social",           "Assistente social",            "#843C39", "Profissionais"),
]
COR_AUSENTE = "#E5E5E5"

# Catálogo (chave, label) derivado de METRIC_ESCOLA_FIELDS — fonte única para o
# catálogo de filtros (/filtros) e a validação de variáveis do painel.
METRIC_FIELDS: list[tuple[str, str]] = [
    (chave, label) for chave, label, _, _ in METRIC_ESCOLA_FIELDS
]

METRICS_BY_KEY: dict[str, str] = {key: label for key, label in METRIC_FIELDS}

PAINEL_DESCRICAO = "painel_acessibilidade"
MAPA_DESCRICAO = "mapa_acessibilidade"
ANALISE_TEMPORAL_DESCRICAO = "analise_temporal_acessibilidade"
TAB_PERCENT_ROW_HEIGHT_PX = 42
TAB_PERCENT_HEADER_PX = 130
TAB_PERCENT_VISIBLE_ROWS = 5
# Escolas por página no gráfico de métricas por escola (default do /painel e
# do endpoint dedicado /painel/escolas).
PAINEL_ESCOLAS_PAGE_SIZE = 5


class AcessibilidadeService:
    """Serviço de acessibilidade: monta painéis, mapas e gráficos de evolução temporal."""

    def __init__(self, repository: AcessibilidadeRepository):
        self._repository = repository

    @staticmethod
    def _figure_to_plotly_dict(figure: go.Figure) -> dict:
        """Converte figura Plotly para dict (data + layout) serializável em JSON."""
        return json.loads(figure.to_json())

    async def build_painel(
        self,
        ano: int | None,
        municipios: list[str] | None,
        rede_ensino: list[str] | None = None,
        tp_localizacao: list[str] | None = None,
        variaveis: list[str] | None = None,
        pibid: bool | None = None,
    ) -> dict:
        """Monta o painel de acessibilidade: gráfico + opções de filtro.

        - Sem `municipios`: o tab_percent cobre todos os municípios do recorte.
        - Sem `ano`: agrega em todos os censos.
        - `variaveis`: define quais indicadores entram no recorte.
          • Sem filtro (None/vazio): usa OR sobre TODAS as 15 variáveis —
            escola conta se tiver QUALQUER variável = 1.
          • Com filtro: usa AND — escola precisa ter TODAS as variáveis = 1.
        - `rede_ensino`/`tp_localizacao` restringem a população (aplicam
          aos numerador e denominador).
        """
        variaveis, combine_or = self._resolver_variaveis(variaveis)

        # Paralelizar queries independentes com asyncio.gather()
        (
            records,
            total_escolas_com_acessibilidade_record,
            total_escolas_geral_record,
            dep_records,
            loc_records,
        ) = await asyncio.gather(
            self._repository.find_media_por_municipio(
                variaveis=variaveis,
                combine_or=combine_or,
                ano=ano,
                municipios=municipios,
                rede_ensino=rede_ensino,
                tp_localizacao=tp_localizacao,
                pibid=pibid,
            ),
            self._repository.find_total_escolas(
                variaveis=variaveis,
                combine_or=combine_or,
                ano=ano,
                municipios=municipios,
                rede_ensino=rede_ensino,
                tp_localizacao=tp_localizacao,
                pibid=pibid,
            ),
            self._repository.find_total_escolas_geral(
                ano=ano,
                municipios=municipios,
                rede_ensino=rede_ensino,
                tp_localizacao=tp_localizacao,
                pibid=pibid,
            ),
            self._repository.find_media_por_dependencia(
                variaveis=variaveis,
                combine_or=combine_or,
                ano=ano,
                municipios=municipios,
                rede_ensino=rede_ensino,
                tp_localizacao=tp_localizacao,
                pibid=pibid,
            ),
            self._repository.find_media_por_localizacao(
                variaveis=variaveis,
                combine_or=combine_or,
                ano=ano,
                municipios=municipios,
                rede_ensino=rede_ensino,
                tp_localizacao=tp_localizacao,
                pibid=pibid,
            ),
        )

        tab_percent = self._build_tab_percent(records, ano, variaveis, combine_or)

        label_filtro = self._filtro_variaveis_label(variaveis, combine_or)
        recorte = self._recorte_temporal_label(ano)
        card_total_escolas = self._build_total_escolas_card(
            total_escolas_geral_record,
            titulo=f"Total de Escolas — {recorte}",
        )
        card_total_escolas_com_acessibilidade = self._build_total_escolas_card(
            total_escolas_com_acessibilidade_record,
            titulo=f"Total de Escolas com {label_filtro} — {recorte}",
        )

        grafico_dependencia = self._build_dependencia_chart(
            dep_records, variaveis, combine_or, ano,
        )
        grafico_tp_localizacao = self._build_localizacao_chart(
            loc_records, variaveis, combine_or, ano,
        )

        return {
            "descricao": PAINEL_DESCRICAO,
            "data": {
                "graficos": {
                    "card_total_escolas": card_total_escolas,
                    "card_total_escolas_com_acessibilidade": card_total_escolas_com_acessibilidade,
                    "tab_percent_acessibilidade": tab_percent,
                    "grafico_dependencia_acessibilidade": grafico_dependencia,
                    "grafico_tp_localizacao_acessibilidade": grafico_tp_localizacao,
                },
            },
        }

    async def build_painel_escolas(
        self,
        ano: int | None,
        municipios: list[str] | None,
        rede_ensino: list[str] | None = None,
        tp_localizacao: list[str] | None = None,
        variaveis: list[str] | None = None,
        pibid: bool | None = None,
        page: int = 0,
        page_size: int = PAINEL_ESCOLAS_PAGE_SIZE,
    ) -> dict:
        """Uma página do gráfico de métricas por escola (barras empilhadas),
        ordenado por score DESC e com os mesmos filtros do painel.

        Retorna `{"grafico": <envelope>, "paginacao": {...}}`. O front usa a
        paginação para navegar as demais escolas batendo só neste caminho leve,
        sem reprocessar o painel inteiro a cada virada de página.
        """
        variaveis_efetivas, combine_or = self._resolver_variaveis(variaveis)

        total_escolas = await self._repository.count_metricas_por_escola(
            variaveis=variaveis_efetivas,
            combine_or=combine_or,
            ano=ano,
            municipios=municipios,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
            pibid=pibid,
        )

        records = await self._repository.find_metricas_por_escola(
            variaveis=variaveis_efetivas,
            combine_or=combine_or,
            ano=ano,
            municipios=municipios,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
            pibid=pibid,
            limit=page_size,
            offset=page * page_size,
        )

        entidades = [r.co_entidade for r in records]
        ideb_map = await self._repository.find_ideb_por_entidades(entidades)
        pibid_map = await self._repository.find_pibid_por_entidades(entidades)

        total_paginas = (
            (total_escolas + page_size - 1) // page_size if page_size else 0
        )
        inicio = page * page_size

        label = self._filtro_variaveis_label(variaveis_efetivas, combine_or)
        recorte = self._recorte_escola_label(ano, records)
        sufixo_municipio = (
            f" {self._municipios_label(municipios)}" if municipios else ""
        )
        intervalo = (
            f"  |  escolas {inicio + 1}–{inicio + len(records)} de {total_escolas}"
            if records
            else "  |  0 escolas"
        )
        titulo = (
            f"Métricas de acessibilidade por escola com {label}"
            f"{sufixo_municipio} — {recorte}{intervalo}"
        )
        figure = self._build_metricas_por_escola_figure(
            records, titulo, ideb_map, pibid_map
        )
        return {
            "grafico": {
                "tipo": "bar",
                "titulo": titulo,
                "plotly": self._figure_to_plotly_dict(figure),
            },
            "paginacao": {
                "page": page,
                "page_size": page_size,
                "total_escolas": total_escolas,
                "total_paginas": total_paginas,
            },
        }

    async def build_mapa(
        self,
        ano: int | None,
        variaveis: list[str] | None,
        pibid: bool | None = None,
    ) -> dict:
        """Lista as linhas de gold.fato_score_acessibilidade (score e
        classificação pré-computados). Sem transformação extra — apenas
        envelopa a saída do repository."""
        pontos = await self._repository.find_pontos_mapa_raw(
            ano=ano,
            variaveis=variaveis,
            pibid=pibid,
        )
        return {
            "descricao": MAPA_DESCRICAO,
            "data": {"pontos": pontos},
        }

    async def build_analise_temporal(
        self,
        metrica: str,
        pibid: bool | None = None,
    ) -> dict:
        """Monta os gráficos de evolução temporal: por tipo de localização
        (urbana/rural) e por tipo de dependência administrativa
        (Federal/Estadual/Municipal/Privada, P1G6). Ambos parametrizados
        pela mesma `metrica`, com eixo X = ano censo e eixo Y = percentual
        de escolas com a métrica = 1.
        """
        if metrica not in METRICS_BY_KEY:
            raise ValueError(
                f"Métrica inválida: {metrica!r}. Esperado uma de: "
                f"{sorted(METRICS_BY_KEY)}"
            )
        records = await self._repository.find_evolucao_por_localizacao(
            metrica=metrica,
            pibid=pibid,
        )
        grafico = self._build_evolucao_temporal(records, metrica)


        dep_records = await self._repository.find_evolucao_por_dependencia(
            metrica=metrica,
            pibid=pibid,
        )
        grafico_dependencia = self._build_evolucao_temporal_dependencia(
            dep_records, metrica
        )

        return {
            "descricao": ANALISE_TEMPORAL_DESCRICAO,
            "data": {
                "graficos": {
                    "evolucao_temporal_por_localizacao": grafico,
                    "evolucao_temporal_por_dependencia": grafico_dependencia,
                },
            },
        }

    # ========================================================================
    # LABEL & TITLE HELPERS
    # ========================================================================

    @staticmethod
    def _resolver_variaveis(variaveis: list[str] | None) -> tuple[list[str], bool]:
        """Normaliza o filtro de variáveis do painel.

        - Vazio/None → OR sobre TODAS as 15 variáveis (escola conta com
          QUALQUER variável = 1).
        - Preenchido → AND, validando cada chave contra a whitelist.

        Retorna `(variaveis_efetivas, combine_or)`.
        """
        if not variaveis:
            return [chave for chave, _ in METRIC_FIELDS], True
        for v in variaveis:
            if v not in METRICS_BY_KEY:
                raise ValueError(
                    f"Variável inválida: {v!r}. Esperado uma de: "
                    f"{sorted(METRICS_BY_KEY)}"
                )
        return variaveis, False

    @staticmethod
    def _filtro_variaveis_label(variaveis: list[str], combine_or: bool) -> str:
        if combine_or:
            return "qualquer recurso de acessibilidade"
        if len(variaveis) == 1:
            return METRICS_BY_KEY.get(variaveis[0], variaveis[0])
        return "múltiplos recursos de acessibilidade selecionados"

    @staticmethod
    def _recorte_temporal_label(ano: int | None) -> str:
        return f"Censo {ano}" if ano is not None else "Todos os censos"

    @staticmethod
    def _municipios_label(municipios: list[str]) -> str:
        """Trecho de município (já com preposição) para o título. Nome do
        município quando houver só um; texto genérico quando houver vários."""
        if len(municipios) == 1:
            return f"em {municipios[0]}"
        return "nos municípios selecionados"

    @staticmethod
    def _recorte_escola_label(
        ano: int | None,
        records: list[AcessibilidadeEscola],
    ) -> str:
        """Rótulo temporal do gráfico por escola. Sem filtro de `ano`, cada
        escola usa o seu censo mais recente — então o rótulo mostra o(s)
        ano(s) realmente exibido(s) em vez de 'Todos os censos' (que
        confundiria)."""
        if ano is not None:
            return f"Censo {ano}"
        anos = sorted({r.nu_ano_censo for r in records})
        if not anos:
            return "Censo mais recente por escola"
        if len(anos) == 1:
            return f"Censo mais recente ({anos[0]})"
        return f"Censo mais recente por escola ({anos[0]}–{anos[-1]})"

    def _build_tab_percent(
        self,
        records: list[AcessibilidadeMunicipio],
        ano: int | None,
        variaveis: list[str],
        combine_or: bool = False,
    ) -> dict:
        df = self._records_to_dataframe(records)
        if not df.empty:
            df = df.sort_values(
                by=["percentual", "municipio"],
                ascending=[False, True],
                kind="mergesort",
            ).reset_index(drop=True)
        label = self._filtro_variaveis_label(variaveis, combine_or)
        recorte = self._recorte_temporal_label(ano)
        titulo = f"Percentual de escolas com {label} por município — {recorte}"
        figure = self._build_tab_percent_figure(df, "percentual", titulo)
        return {
            "tipo": "bar",
            "titulo": titulo,
            "plotly": self._figure_to_plotly_dict(figure),
        }

    def _build_evolucao_temporal(
        self,
        records: list[AcessibilidadeTemporal],
        metrica: str,
    ) -> dict:
        label = METRICS_BY_KEY[metrica]
        titulo = f"Percentual de escolas com {label} por tipo de localização (evolução temporal)"
        df = self._temporal_to_dataframe(records)
        if not df.empty:
            df = df.sort_values(by=["localizacao", "ano"]).reset_index(drop=True)
        figure = self._build_evolucao_temporal_figure(df, titulo)
        return {
            "tipo": "line",
            "titulo": titulo,
            "plotly": self._figure_to_plotly_dict(figure),
        }

    # ========================================================================
    # DATAFRAME BUILDERS - Conversão de registros para DataFrames (Pandas)
    # ========================================================================

    @staticmethod
    def _records_to_dataframe(records: list[AcessibilidadeMunicipio]) -> pd.DataFrame:
        rows = [
            {
                "municipio": r.municipio,
                "percentual": r.percentual,
                "total_escolas": r.total_escolas,
            }
            for r in records
        ]
        return pd.DataFrame(rows)

    @staticmethod
    def _temporal_to_dataframe(records: list[AcessibilidadeTemporal]) -> pd.DataFrame:
        rows = [
            {
                "ano": r.ano,
                "localizacao": r.localizacao,
                "percentual": r.percentual,
            }
            for r in records
        ]
        return pd.DataFrame(rows)

    # ========================================================================
    # FIGURE BUILDERS - Renderização Plotly para gráficos
    # ========================================================================

    @staticmethod
    def _build_tab_percent_figure(
       df: pd.DataFrame,
       metrica: str,
       titulo: str,
    ) -> go.Figure:
       if df.empty:
           return ChartFactory.bar_chart_horizontal([], [], titulo)
        
       values = df[metrica].tolist()
       municipios = df["municipio"].tolist()
       totais = df["total_escolas"].tolist()
        
       fig = ChartFactory.bar_chart_horizontal(
           y_data=municipios,
           x_data=values,
           titulo=titulo,
           customdata=totais,
           x_axis_range=(0, 100),
       )
        
       n_rows = len(df)
       figure_height = TAB_PERCENT_HEADER_PX + TAB_PERCENT_ROW_HEIGHT_PX * max(
           n_rows, 1
       )
       # Customizações específicas para este gráfico
       fig.update_layout(
           yaxis=dict(title="Lista de municípios"),
           margin=dict(l=160, r=40, t=60, b=40),
           height=figure_height,
       )
       return fig

    @staticmethod
    @staticmethod
    def _build_evolucao_temporal_figure(
        df: pd.DataFrame,
        titulo: str,
    ) -> go.Figure:
        if df.empty:
            return ChartFactory.line_chart([], {}, titulo)
        
        # Agrupa dados por localização para criar série temporal
        y_data_series = {}
        for localizacao in df["localizacao"].unique():
            df_loc = df[df["localizacao"] == localizacao]
            y_data_series[localizacao] = df_loc["percentual"].tolist()
        
        x_data = df["ano"].unique().tolist()
        x_data.sort()
        
        return ChartFactory.line_chart(
            x_data=x_data,
            y_data_series=y_data_series,
            titulo=titulo,
            y_axis_title="Percentual de acessibilidade",
        )
    
    def _build_total_escolas_card(
        self,
        total_record: TotalEscolas,
        titulo: str = "Total de Escolas",
    ) -> dict:
        """Envelopa a figura do indicador no formato esperado pelo contrato da API"""
        figure = self._build_total_escolas_figure(total_record.total, titulo)

        return{
            "tipo": "indicator",
            "titulo": titulo,
            "plotly": self._figure_to_plotly_dict(figure),
        }

    @staticmethod
    def _build_total_escolas_figure(total: int, titulo: str = "Total de Escolas") -> go.Figure:
        """Constrói o componente de KPI (Indicator) idêntico ao protótipo do notebook"""
        return ChartFactory.indicator_card(
            value=total,
            titulo=titulo,
            font_size=60,
        )
    
    def _build_dependencia_chart(
        self,
        records: list[AcessibilidadeDependencia],
        variaveis: list[str],
        combine_or: bool,
        ano: int | None,
    ) -> dict:
        """Estrutura o envelope JSON do gráfico de dependência administrativa (P1G5)."""
        sorted_records = sorted(records, key=lambda x: x.percentual, reverse=True)

        x_data = [r.dependencia for r in sorted_records]
        y_data = [r.percentual for r in sorted_records]

        totais_escolas = [r.total_escolas for r in sorted_records]

        label = self._filtro_variaveis_label(variaveis, combine_or)
        recorte = self._recorte_temporal_label(ano)
        titulo = (
            f"Percentual de escolas com {label} por tipo de dependência "
            f"administrativa — {recorte}"
        )
        figure = self._build_dependencia_figure(x_data, y_data, totais_escolas, titulo)
        
        return {
            "tipo": "bar",
            "titulo": titulo,
            "plotly": self._figure_to_plotly_dict(figure),
        }

    @staticmethod
    def _build_dependencia_figure(
        x_data: list[str],
        y_data: list[float],
        totais_escolas: list[int],
        titulo: str,
    ) -> go.Figure:
        """Gera o objeto gráfico do Plotly para barras verticais."""
        return ChartFactory.bar_chart_vertical(
            x_data=x_data,
            y_data=y_data,
            titulo=titulo,
            customdata=totais_escolas,
            color_palette="Blues_r",
        )

    def _build_localizacao_chart(
        self,
        records: list[AcessibilidadeLocalizacao],
        variaveis: list[str],
        combine_or: bool,
        ano: int | None,
    ) -> dict:
        """Estrutura o envelope JSON do gráfico por tipo de localização."""
        sorted_records = sorted(records, key=lambda x: x.percentual, reverse=True)

        x_data = [r.localizacao for r in sorted_records]
        y_data = [r.percentual for r in sorted_records]

        totais_escolas = [r.total_escolas for r in sorted_records]

        label = self._filtro_variaveis_label(variaveis, combine_or)
        recorte = self._recorte_temporal_label(ano)
        titulo = (
            f"Percentual de escolas com {label} por tipo de localização "
            f"— {recorte}"
        )
        figure = self._build_localizacao_figure(x_data, y_data, totais_escolas, titulo)

        return {
            "tipo": "bar",
            "titulo": titulo,
            "plotly": self._figure_to_plotly_dict(figure),
        }

    @staticmethod
    def _build_localizacao_figure(
        x_data: list[str],
        y_data: list[float],
        totais_escolas: list[int],
        titulo: str,
    ) -> go.Figure:
        """Gera o objeto gráfico do Plotly para barras verticais."""
        return ChartFactory.bar_chart_vertical(
            x_data=x_data,
            y_data=y_data,
            titulo=titulo,
            customdata=totais_escolas,
            color_palette="Blues_r",
        )

    @staticmethod
    def _build_metricas_por_escola_figure(
        records: list[AcessibilidadeEscola],
        titulo: str,
        ideb_map: dict[int, dict[str, float | None]],
        pibid_map: dict[int, dict[str, object]],
    ) -> go.Figure:
        """Uma barra horizontal empilhada por escola: cada métrica é um slot de
        largura 1, colorido se a escola possui (=1) ou cinza se não. Hover traz
        PIBID (subprojeto + bolsistas ativos) e IDEB (anos iniciais/finais/
        ensino médio). Legenda manual agrupada (Infraestrutura × Profissionais)
        e anotação n/15 ao final de cada barra. Os registros chegam ordenados
        por score DESC; o eixo Y é invertido para o maior score ficar no topo."""
        fig = go.Figure()
        escolas = [r.no_entidade for r in records]
        n = len(records)
        n_metricas = len(METRIC_ESCOLA_FIELDS)

        # Pré-processar dados de IDEB, PIBID para evitar lookups repetidos
        cached_data = []
        for r in records:
            # IDEB
            notas = ideb_map.get(r.co_entidade, {})
            ideb_partes = [
                f"{rotulo}: {notas[chave]:.1f}"
                for chave, rotulo in (
                    ("iniciais", "Anos Iniciais"),
                    ("finais", "Anos Finais"),
                    ("medio", "Ensino Médio"),
                )
                if notas.get(chave) is not None
            ]
            ideb_texto = "<br>".join(ideb_partes) if ideb_partes else "sem registro"
            
            # PIBID
            pibid_data = pibid_map.get(r.co_entidade, {})
            subprojeto = pibid_data.get("subprojetos", "Sem registro")
            bolsistas = pibid_data.get("bolsistas", "—")
            
            cached_data.append({
                "nu_ano_censo": r.nu_ano_censo,
                "subprojeto": subprojeto,
                "bolsistas": bolsistas,
                "ideb_texto": ideb_texto,
            })

        # Uma barra empilhada por métrica (slot fixo de largura 1).
        for chave, rotulo, cor, _grupo in METRIC_ESCOLA_FIELDS:
            colors = []
            customdata_list = []
            for i, r in enumerate(records):
                possui = r.metricas.get(chave, 0) == 1
                colors.append(cor if possui else COR_AUSENTE)
                cached = cached_data[i]
                customdata_list.append([
                    rotulo,
                    "Possui" if possui else "Não possui",
                    cached["nu_ano_censo"],
                    cached["subprojeto"],
                    cached["bolsistas"],
                    cached["ideb_texto"],
                ])
            
            fig.add_trace(
                go.Bar(
                    y=escolas,
                    x=[1] * n,
                    orientation="h",
                    marker=dict(
                        color=colors,
                        line=dict(color="white", width=2),
                    ),
                    customdata=customdata_list,
                    hovertemplate=(
                        "<b>%{y}</b> (censo %{customdata[2]})<br>"
                        "%{customdata[0]}: %{customdata[1]}<br>"
                        "<br><b>PIBID</b><br>"
                        "Subprojeto: %{customdata[3]}<br>"
                        "Bolsistas ativos: %{customdata[4]}<br>"
                        "<br><b>IDEB</b><br>"
                        "%{customdata[5]}"
                        "<extra></extra>"
                    ),
                    showlegend=False,
                )
            )

        # Legenda manual agrupada, com swatch na cor de cada métrica.
        grupos_vistos: set[str] = set()
        for _chave, rotulo, cor, grupo in METRIC_ESCOLA_FIELDS:
            fig.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode="markers",
                    marker=dict(symbol="square", size=12, color=cor),
                    name=rotulo,
                    legendgroup=grupo,
                    legendgrouptitle_text=(
                        grupo if grupo not in grupos_vistos else None
                    ),
                    showlegend=True,
                )
            )
            grupos_vistos.add(grupo)

        # Batch annotations (em vez de uma por uma)
        annotations = [
            dict(
                x=n_metricas + 0.2,
                y=r.no_entidade,
                text=f"{int(r.score)}/{n_metricas}",
                showarrow=False,
                xanchor="left",
                font=dict(size=11, color="#444"),
            )
            for r in records
        ]
        fig.update_layout(annotations=annotations)

        fig.update_layout(
            barmode="stack",
            title=titulo,
            xaxis=dict(showticklabels=False, range=[0, n_metricas + 1.5]),
            yaxis=dict(title="", autorange="reversed"),
            height=max(400, 26 * max(n, 1)),
            bargap=0.35,
            legend_title_text="Métricas",
            template="plotly_white",
        )
        return fig

    @staticmethod
    def _temporal_dependencia_to_dataframe(
        records: list[AcessibilidadeTemporalDependencia],
    ) -> pd.DataFrame:
        rows = [
            {
                "ano": r.ano,
                "dependencia": r.dependencia,
                "percentual": r.percentual,
            }
            for r in records
        ]
        return pd.DataFrame(rows)

    def _build_evolucao_temporal_dependencia(
        self,
        records: list[AcessibilidadeTemporalDependencia],
        metrica: str,
    ) -> dict:
        label = METRICS_BY_KEY[metrica]
        titulo = f"Percentual de escolas com {label} por tipo de dependência administrativa (evolução temporal)"
        df = self._temporal_dependencia_to_dataframe(records)
        if not df.empty:
            df = df.sort_values(
                by=["dependencia", "ano"]
            ).reset_index(drop=True)
        figure = self._build_evolucao_temporal_dependencia_figure(df, titulo)
        return {
            "tipo": "line",
            "titulo": titulo,
            "plotly": self._figure_to_plotly_dict(figure),
        }

    @staticmethod
    def _build_evolucao_temporal_dependencia_figure(
        df: pd.DataFrame,
        titulo: str,
    ) -> go.Figure:
        if df.empty:
            return ChartFactory.line_chart([], {}, titulo)
        
        # Agrupa dados por dependência para criar série temporal
        y_data_series = {}
        for dependencia in df["dependencia"].unique():
            df_dep = df[df["dependencia"] == dependencia]
            y_data_series[dependencia] = df_dep["percentual"].tolist()
        
        x_data = df["ano"].unique().tolist()
        x_data.sort()
        
        return ChartFactory.line_chart(
            x_data=x_data,
            y_data_series=y_data_series,
            titulo=titulo,
            y_axis_title="Percentual de Acessibilidade",
        )
