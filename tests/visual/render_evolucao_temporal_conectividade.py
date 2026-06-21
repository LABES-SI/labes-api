"""Renderiza os gráficos de evolução temporal de conectividade indo até o banco.

Percorre o mesmo caminho usado pela rota `/conectividade/analise-temporal`:
abre uma sessão no warehouse, instancia o repositório e o serviço, chama
`build_analise_temporal`, reconstrói as figuras a partir do JSON Plotly
retornado e salva como HTML (uma seção por gráfico: localização e dependência).

Uso:
    uv run python -m tests.visual.render_evolucao_temporal_conectividade
    # abre tests/visual/out/evolucao_temporal_conectividade.html
"""

import argparse
import asyncio
import json
from pathlib import Path

import plotly.io as pio

from app.core.dependencies import SessionLocal, async_engine
from app.repositories.conectividade_repository import ConectividadeRepository
from app.services.conectividade_service import ConectividadeService


HTML_TEMPLATE = """<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<title>{titulo}</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
  body {{ margin: 0; font-family: sans-serif; background: #fff; }}
  .chart-wrapper {{
    margin: 16px;
    border: 1px solid #e2e2e2;
    border-radius: 6px;
    padding: 8px;
  }}
</style>
</head>
<body>
{plot_div}
</body>
</html>
"""


async def _build_analise_temporal(metrica: str) -> dict:
    async with SessionLocal() as session:
        repository = ConectividadeRepository(SessionLocal, semaphore=None)
        service = ConectividadeService(repository)
        return await service.build_analise_temporal(metrica=metrica)


async def _run(metrica: str) -> Path:
    try:
        envelope = await _build_analise_temporal(metrica=metrica)
    finally:
        await async_engine.dispose()

    graficos = envelope["data"]["graficos"]
    out_dir = Path(__file__).parent / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "evolucao_temporal_conectividade.html"

    plot_divs = []
    for chave, grafico in graficos.items():
        plotly_payload = grafico["plotly"]
        figure = pio.from_json(json.dumps(plotly_payload))
        plot_div = pio.to_html(
            figure,
            include_plotlyjs=False,
            full_html=False,
            config={"responsive": True},
        )
        plot_divs.append(
            f'<div class="chart-wrapper"><h3>{chave}</h3>{plot_div}</div>'
        )

        n_traces = len(plotly_payload["data"])
        n_pontos = sum(len(t.get("x", [])) for t in plotly_payload["data"])
        print(f"[{chave}] título: {grafico['titulo']} — séries: {n_traces} — pontos: {n_pontos}")

    html = HTML_TEMPLATE.format(
        titulo="Evolução Temporal — Conectividade",
        plot_div="\n".join(plot_divs),
    )
    out_file.write_text(html, encoding="utf-8")
    print(f"Gráficos renderizados em: {out_file}")
    return out_file


def main() -> Path:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrica", default="in_internet")
    args = parser.parse_args()

    return asyncio.run(_run(metrica=args.metrica))


if __name__ == "__main__":
    main()
