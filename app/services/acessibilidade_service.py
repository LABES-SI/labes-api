import json

import pandas as pd
import plotly.graph_objects as go

from app.domain.acessibilidade import (
    AcessibilidadeEscola,
    AcessibilidadeLocalizacao,
    AcessibilidadeMunicipio,
    AcessibilidadeTemporal,
    #P1G4
    TotalEscolas,
    #P1G5
    AcessibilidadeDependencia,
    #P1G6
    AcessibilidadeTemporalDependencia,
)
from app.repositories.acessibilidade_repository import AcessibilidadeRepository


METRIC_FIELDS: list[tuple[str, str]] = [
    ("in_banheiro_pne", "Banheiro PNE"),
    ("in_sala_atendimento_especial", "Sala de Atendimento Especial"),
    ("in_acessibilidade_rampas", "Rampas"),
    ("in_acessibilidade_corrimao", "Corrimão"),
    ("in_acessibilidade_elevador", "Elevador"),
    ("in_acessibilidade_pisos_tateis", "Pisos Táteis"),
    ("in_acessibilidade_vao_livre", "Vão Livre"),
    ("in_acessibilidade_inexistente", "Outros"),
    ("in_acessibilidade_sinal_tatil", "Sinalização Tátil"),
    ("in_acessibilidade_sinal_sonoro", "Sinalização Sonora"),
    ("in_acessibilidade_sinal_visual", "Sinalização Visual"),
    ("in_acessibilidade_sinalizacao", "Sinalização Geral"),
    ("in_prof_psicologo", "Psicólogo"),
    ("in_prof_trad_libras", "Tradutor/Intérprete de Libras"),
    ("in_prof_revisor_braille", "Revisor de Braille"),
    ("in_prof_assist_social", "Assistente Social"),
    ("in_prof_fonaudiologo", "Fonoaudiólogo"),
]

METRICS_BY_KEY: dict[str, str] = {key: label for key, label in METRIC_FIELDS}

# (chave, rótulo, cor, grupo) — define ordem, cores e agrupamento da legenda
# (Infraestrutura × Profissionais) do gráfico de métricas por escola.
# in_acessibilidade_inexistente entra como "Outros" (base, igual ao protótipo).
METRIC_ESCOLA_FIELDS: list[tuple[str, str, str, str]] = [
    ("in_sala_atendimento_especial", "Sala de atendimento especial", "#4C78A8", "Infraestrutura"),
    ("in_banheiro_pne",               "Banheiro PNE",                 "#F58518", "Infraestrutura"),
    ("in_acessibilidade_rampas",      "Rampas",                       "#54A24B", "Infraestrutura"),
    ("in_acessibilidade_corrimao",    "Corrimão",                     "#E45756", "Infraestrutura"),
    ("in_acessibilidade_elevador",    "Elevador",                     "#72B7B2", "Infraestrutura"),
    ("in_acessibilidade_pisos_tateis","Pisos táteis",                 "#EECA3B", "Infraestrutura"),
    ("in_acessibilidade_vao_livre",   "Vão livre",                    "#B279A2", "Infraestrutura"),
    ("in_acessibilidade_sinal_visual","Sinal visual",                 "#FF9DA6", "Infraestrutura"),
    ("in_acessibilidade_sinal_sonoro","Sinal sonoro",                 "#9D755D", "Infraestrutura"),
    ("in_acessibilidade_sinal_tatil", "Sinal tátil",                  "#1F77B4", "Infraestrutura"),
    ("in_acessibilidade_sinalizacao", "Sinalização",                  "#D67195", "Infraestrutura"),
    ("in_acessibilidade_inexistente", "Outros",                       "#444444", "Infraestrutura"),
    ("in_prof_psicologo",             "Psicólogo",                    "#5254A3", "Profissionais"),
    ("in_prof_trad_libras",           "Tradutor de Libras",           "#637939", "Profissionais"),
    ("in_prof_revisor_braille",       "Revisor de Braille",           "#8C6D31", "Profissionais"),
    ("in_prof_assist_social",         "Assistente social",            "#843C39", "Profissionais"),
    ("in_prof_fonaudiologo",          "Fonoaudiólogo",                "#7B4173", "Profissionais"),
]
COR_AUSENTE = "#E5E5E5"

REDES_ENSINO: list[str] = ["Federal", "Estadual", "Municipal", "Privada"]
TIPOS_LOCALIZACAO: list[str] = ["Urbana", "Rural"]

PAINEL_DESCRICAO = "painel_acessibilidade"
MAPA_DESCRICAO = "mapa_acessibilidade"
ANALISE_TEMPORAL_DESCRICAO = "analise_temporal_acessibilidade"
TAB_PERCENT_ROW_HEIGHT_PX = 42
TAB_PERCENT_HEADER_PX = 130
TAB_PERCENT_VISIBLE_ROWS = 5


class AcessibilidadeService:
    def __init__(self, repository: AcessibilidadeRepository):
        self._repository = repository

    async def build_painel(
        self,
        ano: int | None,
        municipios: list[str] | None,
        rede_ensino: list[str] | None = None,
        tp_localizacao: list[str] | None = None,
        variaveis: list[str] | None = None,
    ) -> dict:
        """Monta o painel de acessibilidade: gráfico + opções de filtro.

        - Sem `municipios`: o tab_percent cobre todos os municípios do recorte.
        - Sem `ano`: agrega em todos os censos.
        - `variaveis`: define quais indicadores entram no recorte.
          • Sem filtro (None/vazio): usa OR sobre TODAS as 17 variáveis —
            escola conta se tiver QUALQUER variável = 1.
          • Com filtro: usa AND — escola precisa ter TODAS as variáveis = 1.
        - `rede_ensino`/`tp_localizacao` restringem a população (aplicam
          aos numerador e denominador).
        """
        combine_or = not variaveis
        # "Sem filtro" = nenhum recorte aplicado. O gráfico por escola usa esse
        # estado para limitar ao top 10 (maior score); com qualquer filtro,
        # traz todas as escolas que casam.
        is_unfiltered = (
            combine_or
            and ano is None
            and not municipios
            and not rede_ensino
            and not tp_localizacao
        )
        if combine_or:
            variaveis = [chave for chave, _ in METRIC_FIELDS]
        else:
            for v in variaveis:
                if v not in METRICS_BY_KEY:
                    raise ValueError(f"Variável inválida: {v!r}. Esperado uma de: {sorted(METRICS_BY_KEY)}")

        records = await self._repository.find_media_por_municipio(
            variaveis=variaveis,
            combine_or=combine_or,
            ano=ano,
            municipios=municipios,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
        )

        total_escolas_com_acessibilidade_record = await self._repository.find_total_escolas(
            variaveis=variaveis,
            combine_or=combine_or,
            ano=ano,
            municipios=municipios,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
        )

        total_escolas_geral_record = await self._repository.find_total_escolas_geral(
            ano=ano,
            municipios=municipios,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
        )

        dep_records = await self._repository.find_media_por_dependencia(
            variaveis=variaveis,
            combine_or=combine_or,
            ano=ano,
            municipios=municipios,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
        )

        loc_records = await self._repository.find_media_por_localizacao(
            variaveis=variaveis,
            combine_or=combine_or,
            ano=ano,
            municipios=municipios,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
        )

        escola_records = await self._repository.find_metricas_por_escola(
            variaveis=variaveis,
            combine_or=combine_or,
            ano=ano,
            municipios=municipios,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
            limit=10 if is_unfiltered else None,
        )

        municipios_disponiveis = await self._repository.find_municipios_disponiveis()
        anos_disponiveis = await self._repository.find_anos_disponiveis()

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
        grafico_metricas_por_escola = await self._build_metricas_por_escola(
            escola_records, ano, variaveis, combine_or, municipios,
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
                    "grafico_metricas_por_escola_acessibilidade": grafico_metricas_por_escola,
                },
                "dados_filtros": {
                    "municipios": [
                        {"codigo": codigo, "nome": nome}
                        for codigo, nome in municipios_disponiveis
                    ],
                    "anos": anos_disponiveis,
                    "metricas": [
                        {"chave": chave, "label": label}
                        for chave, label in METRIC_FIELDS
                    ],
                    "rede_ensino": REDES_ENSINO,
                    "tp_localizacao": TIPOS_LOCALIZACAO,
                },
            },
        }

    async def build_mapa(
        self,
        ano: int | None,
        municipios: list[str] | None,
        variaveis: list[str] | None,
        rede_ensino: list[str] | None,
        tp_localizacao: list[str] | None,
    ) -> dict:
        """Lista escolas georreferenciadas com score e classificação de
        acessibilidade calculados em SQL. Sem transformação extra — apenas
        envelopa a saída do repository."""
        pontos = await self._repository.find_pontos_mapa_raw(
            ano=ano,
            municipios=municipios,
            variaveis=variaveis,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
        )
        return {
            "descricao": MAPA_DESCRICAO,
            "data": {"pontos": pontos},
        }

    async def build_analise_temporal(self, metrica: str) -> dict:
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
        )
        grafico = self._build_evolucao_temporal(records, metrica)


        dep_records = await self._repository.find_evolucao_por_dependencia(
            metrica=metrica,
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
                "dados_filtros": {
                    "metricas": [
                        {"chave": chave, "label": label}
                        for chave, label in METRIC_FIELDS
                    ],
                },
            },
        }

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
            "plotly": json.loads(figure.to_json()),
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
            "plotly": json.loads(figure.to_json()),
        }

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

    @staticmethod
    def _build_tab_percent_figure(
        df: pd.DataFrame,
        metrica: str,
        titulo: str,
    ) -> go.Figure:
        fig = go.Figure()
        if not df.empty:
            values = df[metrica].tolist()
            municipios = df["municipio"].tolist()
            text_labels = [f"{v:.1f}%".replace(".", ",") for v in values]
            totais = df["total_escolas"].tolist()
            fig.add_trace(
                go.Bar(
                    x=values,
                    y=municipios,
                    orientation="h",
                    text=text_labels,
                    customdata=totais,
                    texttemplate="%{text}<br>%{customdata} escolas",
                    textposition="inside",
                    insidetextanchor="end",
                )
            )

        n_rows = len(df)
        figure_height = TAB_PERCENT_HEADER_PX + TAB_PERCENT_ROW_HEIGHT_PX * max(
            n_rows, 1
        )
        fig.update_layout(
            title=titulo,
            xaxis=dict(range=[0, 100], ticksuffix="%"),
            # autorange="reversed" coloca o primeiro item (maior valor após o
            # sort DESC) no topo do eixo Y.
            yaxis=dict(autorange="reversed", title="Lista de municípios"),
            showlegend=False,
            margin=dict(l=160, r=40, t=60, b=40),
            height=figure_height,
        )
        return fig

    @staticmethod
    def _build_evolucao_temporal_figure(
        df: pd.DataFrame,
        titulo: str,
    ) -> go.Figure:
        fig = go.Figure()
        if not df.empty:
            for localizacao in df["localizacao"].unique():
                df_loc = df[df["localizacao"] == localizacao]
                fig.add_trace(
                    go.Scatter(
                        x=df_loc["ano"].tolist(),
                        y=df_loc["percentual"].tolist(),
                        mode="lines+markers",
                        name=localizacao,
                    )
                )
        fig.update_layout(
            title=titulo,
            xaxis=dict(title="Ano", dtick=1),
            yaxis=dict(title="Percentual de acessibilidade", ticksuffix="%"),
            template="plotly_white",
        )
        return fig
    
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
            "plotly": json.loads(figure.to_json()),
        }

    @staticmethod
    def _build_total_escolas_figure(total: int, titulo: str = "Total de Escolas") -> go.Figure:
        """Constrói o componente de KPI (Indicator) idêntico ao protótipo do notebook"""
        fig = go.Figure(
            go.Indicator(
                mode="number",
                value=total,
                title={"text": titulo},
                number={"font": {"size": 60}}
            )
        )
        return fig
    
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
            "plotly": json.loads(figure.to_json()),
        }

    @staticmethod
    def _build_dependencia_figure(
        x_data: list[str],
        y_data: list[float],
        totais_escolas: list[int],
        titulo: str,
    ) -> go.Figure:
        """Gera o objeto gráfico do Plotly para barras verticais."""
        import plotly.express as px
        
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=x_data,
                y=y_data,
                text=y_data,
                customdata=totais_escolas,
                texttemplate="%{text:.2f}%<br>%{customdata} escolas",
                textposition="auto",
                marker_color=px.colors.sequential.Blues_r  # Paleta Blues_r
            )
        )
        fig.update_layout(
            title=titulo,
            yaxis_title="Percentual de Escolas",
            xaxis_title="",
            showlegend=False,
            template="plotly_white"
        )
        return fig

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
            "plotly": json.loads(figure.to_json()),
        }

    @staticmethod
    def _build_localizacao_figure(
        x_data: list[str],
        y_data: list[float],
        totais_escolas: list[int],
        titulo: str,
    ) -> go.Figure:
        """Gera o objeto gráfico do Plotly para barras verticais."""
        import plotly.express as px

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=x_data,
                y=y_data,
                text=y_data,
                customdata=totais_escolas,
                texttemplate="%{text:.2f}%<br>%{customdata} escolas",
                textposition="auto",
                marker_color=px.colors.sequential.Blues_r,
            )
        )
        fig.update_layout(
            title=titulo,
            yaxis_title="Percentual de Escolas",
            xaxis_title="",
            showlegend=False,
            template="plotly_white",
        )
        return fig

    async def _build_metricas_por_escola(
        self,
        records: list[AcessibilidadeEscola],
        ano: int | None,
        variaveis: list[str],
        combine_or: bool,
        municipios: list[str] | None,
    ) -> dict:
        """Envelopa o gráfico de barras empilhadas de métricas por escola."""
        ideb_map = await self._repository.find_ideb_por_entidades(
            [(r.co_entidade, r.nu_ano_censo) for r in records]
        )

        label = self._filtro_variaveis_label(variaveis, combine_or)
        recorte = self._recorte_escola_label(ano, records)
        sufixo_municipio = (
            f" {self._municipios_label(municipios)}" if municipios else ""
        )
        titulo = (
            f"Métricas de acessibilidade por escola com {label}"
            f"{sufixo_municipio} — {recorte}"
        )
        figure = self._build_metricas_por_escola_figure(records, titulo, ideb_map)
        return {
            "tipo": "bar",
            "titulo": titulo,
            "plotly": json.loads(figure.to_json()),
        }

    @staticmethod
    def _build_metricas_por_escola_figure(
        records: list[AcessibilidadeEscola],
        titulo: str,
        ideb_map: dict[int, float | None],
    ) -> go.Figure:
        """Uma barra horizontal empilhada por escola: cada métrica é um slot de
        largura 1, colorido se a escola possui (=1) ou cinza se não. Legenda
        manual agrupada (Infraestrutura × Profissionais) e anotação n/17 ao
        final de cada barra. Os registros chegam ordenados por score DESC; o
        eixo Y é invertido para o maior score ficar no topo."""
        fig = go.Figure()
        escolas = [r.no_entidade for r in records]
        n = len(records)
        n_metricas = len(METRIC_ESCOLA_FIELDS)

        # Uma barra empilhada por métrica (slot fixo de largura 1).
        for chave, rotulo, cor, _grupo in METRIC_ESCOLA_FIELDS:
            possui = [r.metricas.get(chave, 0) == 1 for r in records]
            fig.add_trace(
                go.Bar(
                    y=escolas,
                    x=[1] * n,
                    orientation="h",
                    marker=dict(
                        color=[cor if p else COR_AUSENTE for p in possui],
                        line=dict(color="white", width=2),
                    ),
                    customdata=[
                        [
                            rotulo,
                            "Possui" if p else "Não possui",
                            r.nu_ano_censo,
                            # Nota real ou "N/D" quando ausente
                            ideb_map.get(r.co_entidade),
                        ]
                        for r, p in zip(records, possui)
                    ],
                    hovertemplate=(
                        "<b>%{y}</b> (censo %{customdata[2]})<br>"
                        # Plotly renderiza None como "null"; tratamos com
                        # um ternário via customdata.
                        "IDEB: %{customdata[3]}<br>"
                        "%{customdata[0]}: %{customdata[1]}<extra></extra>"
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

        # Contagem n/17 ao final de cada barra.
        for r in records:
            fig.add_annotation(
                x=n_metricas + 0.2,
                y=r.no_entidade,
                text=f"{int(r.score)}/{n_metricas}",
                showarrow=False,
                xanchor="left",
                font=dict(size=11, color="#444"),
            )

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

    #P1G6
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

    #P1G6
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
            "plotly": json.loads(figure.to_json()),
        }

    #P1G6
    @staticmethod
    def _build_evolucao_temporal_dependencia_figure(
        df: pd.DataFrame,
        titulo: str,
    ) -> go.Figure:
        fig = go.Figure()
        if not df.empty:
            for dependencia in df["dependencia"].unique():
                df_dep = df[df["dependencia"] == dependencia]
                fig.add_trace(
                    go.Scatter(
                        x=df_dep["ano"].tolist(),
                        y=df_dep["percentual"].tolist(),
                        mode="lines+markers",
                        name=dependencia,
                    )
                )
        fig.update_layout(
            title=titulo,
            xaxis=dict(title="Ano", dtick=1),
            yaxis=dict(title="Percentual de Acessibilidade", ticksuffix="%"),
            template="plotly_white",
        )
        return fig

    async def _build_metricas_por_escola(
        self,
        records: list[AcessibilidadeEscola],
        ano: int | None,
        variaveis: list[str],
        combine_or: bool,
        municipios: list[str] | None,
    ) -> dict:
        """Envelopa o gráfico de barras empilhadas de métricas por escola."""
        # Busca notas IDEB reais para as escolas do recorte.
        ideb_map = await self._repository.find_ideb_por_entidades(
            [(r.co_entidade, r.nu_ano_censo) for r in records]
        )

        label = self._filtro_variaveis_label(variaveis, combine_or)
        recorte = self._recorte_escola_label(ano, records)
        sufixo_municipio = (
            f" {self._municipios_label(municipios)}" if municipios else ""
        )
        titulo = (
            f"Métricas de acessibilidade por escola com {label}"
            f"{sufixo_municipio} — {recorte}"
        )
        figure = self._build_metricas_por_escola_figure(records, titulo, ideb_map)
        return {
            "tipo": "bar",
            "titulo": titulo,
            "plotly": json.loads(figure.to_json()),
        }


    @staticmethod
    def _mock_ideb_score(co_entidade: int, score_acessibilidade: int) -> float:
        """Gera um valor determinístico de mock do IDEB baseado no código da entidade e no score."""
        import random
        # Cria uma instância de Random para não alterar o state global
        rng = random.Random(co_entidade)
        if score_acessibilidade >= 10:
            base_ideb = rng.uniform(5.5, 7.5)
        elif score_acessibilidade >= 6:
            base_ideb = rng.uniform(4.5, 6.0)
        else:
            base_ideb = rng.uniform(3.0, 5.0)
        ideb_nota = base_ideb + rng.uniform(-0.5, 0.5)
        return round(max(0.0, min(10.0, ideb_nota)), 1)

    async def build_analise_ideb(
        self,
        ano: int | None,
        municipios: list[str] | None,
        rede_ensino: list[str] | None = None,
        tp_localizacao: list[str] | None = None,
        variaveis: list[str] | None = None,
    ) -> dict:
        """Monta o gráfico de cruzamento entre Acessibilidade e IDEB.
        Mock de dados do IDEB baseado no score de acessibilidade, 
        pois a fato_ideb original não foi incluída na base atual.
        """
        pontos = await self._repository.find_pontos_mapa(
            ano=ano,
            municipios=municipios,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
            variaveis=variaveis,
        )

        if not pontos:
            return {"plotly": json.loads(go.Figure().to_json()), "tipo": "scatter", "titulo": "Acessibilidade x IDEB"}

        dados = []
        
        for p in pontos:
            nota_ideb = self._mock_ideb_score(p.co_entidade, p.score_acessibilidade)
            
            dados.append({
                "Escola": str(p.no_entidade) if p.no_entidade else "Desconhecida",
                "Municipio": str(p.no_municipio) if p.no_municipio else "Desconhecido",
                "Score_Acessibilidade": p.score_acessibilidade,
                "IDEB": nota_ideb,
                "Classificacao": p.classificacao_acessibilidade,
                "Rede": str(p.no_tp_dependencia) if p.no_tp_dependencia else "Desconhecida"
            })

        df = pd.DataFrame(dados)
        fig = go.Figure()
        
        cores = {
            "Boa": "#54A24B",
            "Média": "#EECA3B",
            "Baixa": "#F58518",
            "Inexistente": "#E45756"
        }
        
        for classif in ["Boa", "Média", "Baixa", "Inexistente"]:
            df_classif = df[df["Classificacao"] == classif]
            if df_classif.empty:
                continue
                
            fig.add_trace(go.Scatter(
                x=df_classif["Score_Acessibilidade"],
                y=df_classif["IDEB"],
                mode='markers',
                name=classif,
                marker=dict(
                    color=cores.get(classif, "#444444"),
                    size=10,
                    line=dict(width=1, color='DarkSlateGrey')
                ),
                text=df_classif["Escola"] + "<br>Município: " + df_classif["Municipio"] + "<br>Rede: " + df_classif["Rede"],
                hovertemplate="<b>%{text}</b><br><br>Score Acessibilidade: %{x}<br>IDEB: %{y}<extra></extra>"
            ))
            
        fig.update_layout(
            title="Cruzamento: Score de Acessibilidade vs Nota do IDEB",
            xaxis_title="Score de Acessibilidade (0-11)",
            yaxis_title="Nota Estimada IDEB",
            legend_title="Classificação",
            template="plotly_white",
            hovermode="closest"
        )

        return {
            "tipo": "scatter",
            "titulo": "Cruzamento Acessibilidade vs IDEB",
            "plotly": json.loads(fig.to_json())
        }
