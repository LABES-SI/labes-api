"""Renderiza o grafico_dependencia_conectividade indo até o banco.

Percorre o mesmo caminho usado pela rota `/conectividade/painel`:
abre uma sessão no warehouse, instancia o repositório e o serviço, chama
`build_painel`, reconstrói a figura a partir do JSON Plotly retornado e
salva como HTML.

Uso:
    uv run python -m tests.visual.render_dependencia_conectividade
    # Ou para testar filtros específicos
    # uv run python -m tests.visual.render_dependencia_conectividade --ano 2024 --variavel in_internet
"""

import argparse
import asyncio
import json
from pathlib import Path

import plotly.io as pio

from app.core.dependencies import SessionLocal, async_engine
from app.repositories.conectividade_repository import ConectividadeRepository
from app.services.conectividade_service import ConectividadeService

# Um template HTML mais limpo, sem barra de rolagem, ideal para gráficos pequenos
HTML_TEMPLATE = """<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<title>{titulo}</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
  body {{ margin: 0; font-family: sans-serif; background: #fff; }}
  .chart-wrapper {{
    border: 1px solid #e2e2e2;
    border-radius: 6px;
    margin: 16px;
    padding: 16px;
  }}
</style>
</head>
<body>
  <div class="chart-wrapper">{plot_div}</div>
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
        repository = ConectividadeRepository(SessionLocal, semaphore=None)
        service = ConectividadeService(repository)
        return await service.build_painel(
            ano=ano,
            municipios=municipios,
            variaveis=variaveis,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
        )


async def _run(
    ano: int | None,
    municipios: list[str] | None,
    variaveis: list[str] | None,
    rede_ensino: list[str] | None = None,
    tp_localizacao: list[str] | None = None,
) -> Path:
    try:
        painel = await _build_painel(
            ano=ano,
            municipios=municipios,
            variaveis=variaveis,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
        )
    finally:
        await async_engine.dispose()

    # O alvo aqui é o gráfico de Dependência Administrativa
    grafico = painel["data"]["graficos"]["grafico_dependencia_conectividade"]
    plotly_payload = grafico["plotly"]

    figure = pio.from_json(json.dumps(plotly_payload))

    out_dir = Path(__file__).parent / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "dependencia_conectividade.html"

    plot_div = pio.to_html(
        figure,
        include_plotlyjs=False,
        full_html=False,
        config={"responsive": True},
    )

    html = HTML_TEMPLATE.format(
        titulo=grafico["titulo"],
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
    DEFAULT_METRICA = "in_internet"
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
            rede_ensino=args.rede_ensino,
            tp_localizacao=args.tp_localizacao,
        )
    )


if __name__ == "__main__":
    main()
