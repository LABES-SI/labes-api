"""
Factory centralizada para criação de gráficos Plotly reutilizáveis.

Este módulo consolida a lógica de construção de gráficos que antes era
duplicada em vários métodos _build_*_figure(). Permite fácil reutilização
para novos módulos (conectividade, infraestrutura, etc).

Padrões de gráficos:
- Bar vertical: para métricas percentuais por categoria
- Bar horizontal: para percentuais com ordenação customizável
- Line/Scatter: para séries temporais com múltiplas linhas
- Indicator: para KPIs e contadores numéricos
- Stacked bar horizontal: para múltiplas métricas por entidade
"""

import plotly.express as px
import plotly.graph_objects as go
from typing import Optional


class ChartFactory:
    """Factory centralizada para criar gráficos Plotly padronizados."""

    # Configurações globais de estilo
    DEFAULT_TEMPLATE = "plotly_white"
    DEFAULT_COLOR_PALETTE = "Blues_r"

    @staticmethod
    def bar_chart_vertical(
        x_data: list[str],
        y_data: list[float],
        titulo: str,
        customdata: Optional[list[int]] = None,
        color_palette: str = "Blues_r",
        template: str = "plotly_white",
        y_axis_title: str = "Percentual de Escolas",
    ) -> go.Figure:
        """
        Cria gráfico de barras verticais reutilizável.

        Padrão para métricas percentuais por categoria (e.g., dependência, localização).

        Args:
            x_data: Rótulos do eixo X (categorias)
            y_data: Valores do eixo Y (percentuais)
            titulo: Título do gráfico
            customdata: Dados adicionais para exibição no hover (e.g., totais de escolas)
            color_palette: Paleta de cores Plotly (e.g., "Blues_r", "Greens_r", "Reds_r")
            template: Tema do gráfico
            y_axis_title: Título do eixo Y

        Returns:
            go.Figure configurada
        """
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=x_data,
                y=y_data,
                text=y_data,
                customdata=customdata,
                texttemplate="%{text:.2f}%<br>%{customdata} escolas"
                if customdata
                else "%{text:.2f}%",
                textposition="auto",
                marker_color=getattr(px.colors.sequential, color_palette),
            )
        )
        fig.update_layout(
            title=titulo,
            yaxis_title=y_axis_title,
            xaxis_title="",
            showlegend=False,
            template=template,
        )
        return fig

    @staticmethod
    def bar_chart_horizontal(
        y_data: list[str],
        x_data: list[float],
        titulo: str,
        customdata: Optional[list[int]] = None,
        template: str = "plotly_white",
        x_axis_range: tuple[int, int] = (0, 100),
    ) -> go.Figure:
        """
        Cria gráfico de barras horizontais reutilizável.

        Padrão para percentuais com ordenação, tipicamente municipios ou regiões.

        Args:
            y_data: Rótulos do eixo Y (categoria, tipicamente nomes)
            x_data: Valores do eixo X (percentuais)
            titulo: Título do gráfico
            customdata: Dados adicionais para exibição no hover
            template: Tema do gráfico
            x_axis_range: Intervalo do eixo X (min, max)

        Returns:
            go.Figure configurada
        """
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=x_data,
                y=y_data,
                orientation="h",
                text=x_data,
                customdata=customdata,
                texttemplate="%{text:.1f}%".replace(".", ",")
                if customdata
                else "%{text:.1f}%",
                textposition="inside",
                insidetextanchor="end",
            )
        )
        fig.update_layout(
            title=titulo,
            xaxis=dict(range=x_axis_range, ticksuffix="%"),
            yaxis=dict(autorange="reversed"),
            template=template,
            showlegend=False,
        )
        return fig

    @staticmethod
    def line_chart(
        x_data: list[int],
        y_data_series: dict[str, list[float]],
        titulo: str,
        x_axis_title: str = "Ano",
        y_axis_title: str = "Percentual de Acessibilidade",
        template: str = "plotly_white",
    ) -> go.Figure:
        """
        Cria gráfico de linhas reutilizável para séries temporais.

        Padrão para evolução temporal com múltiplas séries (e.g., por localização, dependência).

        Args:
            x_data: Anos ou períodos (eixo X)
            y_data_series: Dicionário {nome_série: [valores]} para cada linha
            titulo: Título do gráfico
            x_axis_title: Título do eixo X
            y_axis_title: Título do eixo Y
            template: Tema do gráfico

        Returns:
            go.Figure configurada
        """
        fig = go.Figure()
        for serie_name, valores in y_data_series.items():
            fig.add_trace(
                go.Scatter(
                    x=x_data,
                    y=valores,
                    mode="lines+markers",
                    name=serie_name,
                )
            )
        fig.update_layout(
            title=titulo,
            xaxis=dict(title=x_axis_title, dtick=1),
            yaxis=dict(title=y_axis_title, ticksuffix="%"),
            template=template,
        )
        return fig

    @staticmethod
    def indicator_card(
        value: int,
        titulo: str,
        font_size: int = 60,
    ) -> go.Figure:
        """
        Cria card KPI (indicador numérico).

        Padrão para exibir contadores e totalizações.

        Args:
            value: Valor numérico a exibir
            titulo: Título do indicador
            font_size: Tamanho da fonte do número

        Returns:
            go.Figure configurada (Indicator)
        """
        fig = go.Figure(
            go.Indicator(
                mode="number",
                value=value,
                title={"text": titulo},
                number={"font": {"size": font_size}},
            )
        )
        return fig

    @staticmethod
    def stacked_bar_horizontal(
        y_labels: list[str],
        traces: list[dict],
        titulo: str,
        template: str = "plotly_white",
    ) -> go.Figure:
        """
        Cria gráfico de barras horizontais empilhadas (stacked).

        Padrão para múltiplas métricas por entidade (e.g., métricas por escola).

        Args:
            y_labels: Rótulos do eixo Y (escolas, regiões, etc)
            traces: Lista de dicts {
                'x': [valores],
                'y': [labels],
                'name': 'nome da série',
                'customdata': [...],
                'marker': {'color': [cores]},
                'hovertemplate': 'template',
            }
            titulo: Título do gráfico
            template: Tema do gráfico

        Returns:
            go.Figure configurada com barras empilhadas
        """
        fig = go.Figure()
        for trace_config in traces:
            fig.add_trace(
                go.Bar(
                    y=trace_config.get("y", y_labels),
                    x=trace_config["x"],
                    name=trace_config["name"],
                    customdata=trace_config.get("customdata"),
                    marker=trace_config.get("marker", {}),
                    hovertemplate=trace_config.get("hovertemplate"),
                    showlegend=trace_config.get("showlegend", True),
                )
            )

        fig.update_layout(
            title=titulo,
            barmode="stack",
            yaxis=dict(autorange="reversed"),
            template=template,
            showlegend=True,
        )
        return fig
