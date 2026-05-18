"""Renderiza o tab_percent de acessibilidade indo até o banco.

Percorre o mesmo caminho usado pela rota `/acessibilidade/painel`:
abre uma sessão no warehouse, instancia o repositório e o serviço, chama
`build_painel`, reconstrói a figura a partir do JSON Plotly retornado e
salva como HTML.

Uso:
    uv run python -m tests.visual.render_tab_percent
    # abre tests/visual/out/tab_percent.html
"""

import argparse
import asyncio
import json
from pathlib import Path

import plotly.io as pio

from app.core.dependencies import SessionLocal, async_engine
from app.repositories.acessibilidade_repository import AcessibilidadeRepository
from app.services.acessibilidade_service import (
    AcessibilidadeService,
    TAB_PERCENT_HEADER_PX,
    TAB_PERCENT_ROW_HEIGHT_PX,
    TAB_PERCENT_VISIBLE_ROWS,
)


SCROLL_TEMPLATE = """<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<title>{titulo}</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
  body {{ margin: 0; font-family: sans-serif; background: #fff; }}
  .scroll-wrapper {{
    max-height: {max_height}px;
    overflow-y: auto;
    border: 1px solid #e2e2e2;
    border-radius: 6px;
    margin: 16px;
  }}
</style>
</head>
<body>
  <div class="scroll-wrapper">{plot_div}</div>
</body>
</html>
"""


async def _build_painel(
    ano: int | None,
    municipios: list[str] | None,
    variaveis: list[str] | None = None,
    rede_ensino: list[str] | None = None,
    tp_localizacao: list[str] | None = None,
) -> dict:
    async with SessionLocal() as session:
        repository = AcessibilidadeRepository(session)
        service = AcessibilidadeService(repository)
        return await service.build_painel(
            ano=ano,
            municipios=municipios,
            variaveis=variaveis,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
        )


async def _run(
    ano: int | None, municipios: list[str] | None, variaveis: list[str] | None
) -> Path:
    try:
        painel = await _build_painel(ano=ano, municipios=municipios, variaveis=variaveis)
    finally:
        await async_engine.dispose()

    grafico = painel["data"]["graficos"]["tab_percent_acessibilidade"]
    plotly_payload = grafico["plotly"]

    figure = pio.from_json(json.dumps(plotly_payload))

    out_dir = Path(__file__).parent / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "tab_percent.html"

    plot_div = pio.to_html(
        figure,
        include_plotlyjs=False,
        full_html=False,
        config={"responsive": True},
    )
    max_height = TAB_PERCENT_HEADER_PX + TAB_PERCENT_ROW_HEIGHT_PX * TAB_PERCENT_VISIBLE_ROWS
    html = SCROLL_TEMPLATE.format(
        titulo=grafico["titulo"],
        max_height=max_height,
        plot_div=plot_div,
    )
    out_file.write_text(html, encoding="utf-8")

    n_bars = len(plotly_payload["data"][0]["x"]) if plotly_payload["data"] else 0
    print(f"Gráfico renderizado em: {out_file}")
    print(f"Título: {grafico['titulo']}")
    print(f"Barras: {n_bars}")
    return out_file


def main() -> Path:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ano", type=int, default=None)
    parser.add_argument(
        "--municipio",
        action="append",
        dest="municipios",
        default=None,
        help="Repita para passar múltiplos municípios.",
    )
    DEFAULT_METRICA = "in_banheiro_pne"
    parser.add_argument(
        "--variavel",
        action="append",
        dest="variaveis",
        default=None,
        help="Repita para passar múltiplas variáveis (filtro AND).",
    )
    parser.add_argument(
        "--rede_ensino",
        action="append",
        dest="rede_ensino",
        default=None,
        help="Repita para passar múltiplas redes de ensino.",
    )
    parser.add_argument(
        "--tp_localizacao",
        action="append",
        dest="tp_localizacao",
        default=None,
        help="Repita para passar múltiplas localizações (Urbana/Rural).",
    )
    args = parser.parse_args()

    variaveis = args.variaveis or [DEFAULT_METRICA]
    return asyncio.run(
        _run(
            ano=args.ano,
            municipios=args.municipios,
            variaveis=variaveis,
        )
    )


if __name__ == "__main__":
    main()
