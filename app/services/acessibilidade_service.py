import json

import pandas as pd
import plotly.graph_objects as go

from app.domain.acessibilidade import (
    AcessibilidadeMunicipio,
    AcessibilidadeTemporal,
)
from app.repositories.acessibilidade_repository import AcessibilidadeRepository


METRIC_FIELDS: list[tuple[str, str]] = [
    ("rampas", "Rampas"),
    ("corrimao", "Corrimão"),
    ("elevador", "Elevador"),
    ("pisos_tateis", "Pisos Táteis"),
    ("vao_livre", "Vão Livre"),
    ("banheiro_pne", "Banheiro PNE"),
]

METRICS_BY_KEY: dict[str, str] = {key: label for key, label in METRIC_FIELDS}

PAINEL_DESCRICAO = "painel_acessibilidade"
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
        metrica: str,
    ) -> dict:
        """Monta o painel de acessibilidade: gráfico + opções de filtro.

        - Sem `municipios`: o tab_percent cobre todos os municípios do recorte.
        - Sem `ano`: agrega em todos os censos.
        - `metrica` define qual das 6 dimensões é plotada.
        """
        records = await self._repository.find_media_por_municipio(
            ano=ano,
            municipios=municipios,
        )
        municipios_disponiveis = await self._repository.find_municipios_disponiveis()
        anos_disponiveis = await self._repository.find_anos_disponiveis()

        tab_percent = self._build_tab_percent(records, ano, metrica)

        return {
            "descricao": PAINEL_DESCRICAO,
            "data": {
                "graficos": {
                    "tab_percent_acessibilidade": tab_percent,
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
                },
            },
        }

    async def build_analise_temporal(self, metrica: str) -> dict:
        """Monta o gráfico de evolução temporal por tipo de localização.

        Uma linha por tipo de localização (urbana/rural), eixo X = ano censo,
        eixo Y = percentual de escolas com a métrica selecionada.
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
        return {
            "descricao": ANALISE_TEMPORAL_DESCRICAO,
            "data": {
                "graficos": {
                    "evolucao_temporal_por_localizacao": grafico,
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
        metrica: str,
    ) -> dict:
        if metrica not in METRICS_BY_KEY:
            raise ValueError(
                f"Métrica inválida: {metrica!r}. Esperado uma de: "
                f"{sorted(METRICS_BY_KEY)}"
            )
        df = self._records_to_dataframe(records)
        if not df.empty:
            df = df.sort_values(
                by=[metrica, "municipio"],
                ascending=[False, True],
                kind="mergesort",
            ).reset_index(drop=True)
        recorte = f"Censo {ano}" if ano is not None else "Todos os censos"
        label = METRICS_BY_KEY[metrica]
        titulo = f"Percentual de escolas com {label} por município — {recorte}"
        figure = self._build_tab_percent_figure(df, metrica, titulo)
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
                **{key: getattr(r, key) for key, _ in METRIC_FIELDS},
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
