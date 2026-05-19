import json

import pandas as pd
import plotly.graph_objects as go

from app.domain.acessibilidade import (
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
    ("in_acessibilidade_inexistente", "Acessibilidade Inexistente"),
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

REDES_ENSINO: list[str] = ["Federal", "Estadual", "Municipal", "Privada"]

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
        - `variaveis` define o indicador cuja proporção será plotada (escolas
          do município com `variaveis = 1` sobre o total).
        - `rede_ensino`/`tp_localizacao` restringem a população (aplicam
          aos numerador e denominador).
        """
        if not variaveis:
            variaveis = [METRIC_FIELDS[0][0]]
        for v in variaveis:
            if v not in METRICS_BY_KEY:
                raise ValueError(f"Variável inválida: {v!r}. Esperado uma de: {sorted(METRICS_BY_KEY)}")

        records = await self._repository.find_media_por_municipio(
            variaveis=variaveis,
            ano=ano,
            municipios=municipios,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
        )

        # P1G4: Busca o total absoluto baseado na mesma métrica e filtros
        total_escolas_record = await self._repository.find_total_escolas(
            metrica=variaveis[0],
            ano=ano,
            municipios=municipios,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
        )

        #P1G5: Busca dados agrupados por dependência administrativa
        dep_records = await self._repository.find_media_por_dependencia(
            metrica=variaveis[0],
            ano=ano,
            municipios=municipios,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
        )

        loc_records = await self._repository.find_media_por_localizacao(
            metrica=variaveis[0],
            ano=ano,
            municipios=municipios,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
        )

        municipios_disponiveis = await self._repository.find_municipios_disponiveis()
        anos_disponiveis = await self._repository.find_anos_disponiveis()

        tab_percent = self._build_tab_percent(records, ano, variaveis)
        #P1G4
        card_total_escolas = self._build_total_escolas_card(total_escolas_record)
        #P1G5
        grafico_dependencia = self._build_dependencia_chart(dep_records, variaveis[0])
        grafico_tp_localizacao = self._build_localizacao_chart(loc_records, variaveis[0])

        return {
            "descricao": PAINEL_DESCRICAO,
            "data": {
                "graficos": {
                    "tab_percent_acessibilidade": tab_percent,
                    #P1G4
                    "card_total_escolas": card_total_escolas,
                    #P1G5
                    "grafico_dependencia_acessibilidade": grafico_dependencia,
                    "grafico_tp_localizacao_acessibilidade": grafico_tp_localizacao,
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

        #P1G6
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
                    #P1G6
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

    def _build_tab_percent(
        self,
        records: list[AcessibilidadeMunicipio],
        ano: int | None,
        variaveis: list[str],
    ) -> dict:
        df = self._records_to_dataframe(records)
        if not df.empty:
            df = df.sort_values(
                by=["percentual", "municipio"],
                ascending=[False, True],
                kind="mergesort",
            ).reset_index(drop=True)
        recorte = f"Censo {ano}" if ano is not None else "Todos os censos"
        labels = [METRICS_BY_KEY.get(v, v) for v in variaveis]
        label = ", ".join(labels)
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
        titulo = f"Evolução temporal de {label} por tipo de localização"
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
            fig.add_trace(
                go.Bar(
                    x=values,
                    y=municipios,
                    orientation="h",
                    text=text_labels,
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
    
    def _build_total_escolas_card(self, total_record: TotalEscolas) -> dict:
        """Envelopa a figura do indicador no formato esperado pelo contrato da API"""
        titulo = "Total de Escolas"
        figure = self._build_total_escolas_figure(total_record.total)

        return{
            "tipo": "indicator",
            "titulo": titulo,
            "plotly": json.loads(figure.to_json()),
        }
    
    @staticmethod
    def _build_total_escolas_figure(total: int) -> go.Figure:
        """Constrói o componente de KPI (Indicator) idêntico ao protótipo do notebook"""
        fig = go.Figure(
            go.Indicator(
                mode="number",
                value=total,
                title={"text": "Total de Escolas"},
                number={"font": {"size": 60}}
            )
        )
        return fig
    
    #P1G5
    def _build_dependencia_chart(
        self,
        records: list[AcessibilidadeDependencia],
        metrica: str,
    ) -> dict:
        """Estrutura o envelope JSON do gráfico de dependência administrativa (P1G5)."""
        # Ordenação decrescente pelo percentual
        sorted_records = sorted(records, key=lambda x: x.percentual, reverse=True)
        
        x_data = [r.dependencia for r in sorted_records]
        y_data = [r.percentual for r in sorted_records]
        
        # Mantém o título
        titulo = 'Percentual de Recursos de Acessibilidade nas Escolas do Pará por Tipo de Localização'
        figure = self._build_dependencia_figure(x_data, y_data, titulo)
        
        return {
            "tipo": "bar",
            "titulo": titulo,
            "plotly": json.loads(figure.to_json()),
        }

    @staticmethod
    def _build_dependencia_figure(
        x_data: list[str],
        y_data: list[float],
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
                texttemplate="%{text:.2f}%",
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
        metrica: str,
    ) -> dict:
        """Estrutura o envelope JSON do gráfico por tipo de localização."""
        sorted_records = sorted(records, key=lambda x: x.percentual, reverse=True)

        x_data = [r.localizacao for r in sorted_records]
        y_data = [r.percentual for r in sorted_records]

        titulo = (
            "Percentual de Recursos de Acessibilidade nas Escolas do Pará "
            "por Tipo de Localização"
        )
        figure = self._build_localizacao_figure(x_data, y_data, titulo)

        return {
            "tipo": "bar",
            "titulo": titulo,
            "plotly": json.loads(figure.to_json()),
        }

    @staticmethod
    def _build_localizacao_figure(
        x_data: list[str],
        y_data: list[float],
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
                texttemplate="%{text:.2f}%",
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
        titulo = f"Evolução temporal de {label} por tipo de dependência"
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
