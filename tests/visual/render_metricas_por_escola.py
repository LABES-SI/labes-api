"""Renderiza o gráfico "Métricas de acessibilidade por escola" indo até o banco.

Percorre o mesmo caminho usado pela rota `/acessibilidade/painel/escolas`: abre
uma sessão no warehouse, instancia o repositório e o serviço, chama
`build_painel_escolas`, reconstrói a figura a partir do JSON Plotly retornado e
salva como HTML.

O gráfico é paginado (ordenado por score DESC): cada chamada traz uma página de
`--page_size` escolas a partir de `--page` (base 0), mais os metadados de
paginação (total de escolas / páginas).

Uso:
    uv run python -m tests.visual.render_metricas_por_escola --ano 2023 --municipio Abaetetuba
    uv run python -m tests.visual.render_metricas_por_escola --ano 2023 --municipio Abaetetuba --page 1 --page_size 5
    # abre tests/visual/out/metricas_por_escola.html
"""

import argparse
import asyncio
import json
from pathlib import Path

import plotly.io as pio

from app.core.dependencies import SessionLocal, async_engine
from app.repositories.acessibilidade_repository import AcessibilidadeRepository
from app.services.acessibilidade_service import AcessibilidadeService


SCROLL_TEMPLATE = """<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<title>{titulo}</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
  body {{ margin: 0; font-family: sans-serif; background: #fff; }}
  .scroll-wrapper {{
    max-height: 680px;
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


async def _build_pagina(
    ano: int | None,
    municipios: list[str] | None,
    variaveis: list[str] | None = None,
    rede_ensino: list[str] | None = None,
    tp_localizacao: list[str] | None = None,
    page: int = 0,
    page_size: int = 5,
) -> dict:
    async with SessionLocal() as session:
        repository = AcessibilidadeRepository(SessionLocal, semaphore=None)
        service = AcessibilidadeService(repository)
        return await service.build_painel_escolas(
            ano=ano,
            municipios=municipios,
            variaveis=variaveis,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
            page=page,
            page_size=page_size,
        )


async def _run(
    ano: int | None,
    municipios: list[str] | None,
    variaveis: list[str] | None,
    rede_ensino: list[str] | None,
    tp_localizacao: list[str] | None,
    page: int = 0,
    page_size: int = 5,
) -> Path:
    try:
        resultado = await _build_pagina(
            ano=ano,
            municipios=municipios,
            variaveis=variaveis,
            rede_ensino=rede_ensino,
            tp_localizacao=tp_localizacao,
            page=page,
            page_size=page_size,
        )
    finally:
        await async_engine.dispose()

    grafico = resultado["grafico"]
    paginacao = resultado["paginacao"]
    plotly_payload = grafico["plotly"]

    figure = pio.from_json(json.dumps(plotly_payload))

    out_dir = Path(__file__).parent / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "metricas_por_escola.html"

    plot_div = pio.to_html(
        figure,
        include_plotlyjs=False,
        full_html=False,
        config={"responsive": True},
    )
    html = SCROLL_TEMPLATE.format(
        titulo=grafico["titulo"],
        plot_div=plot_div,
    )
    out_file.write_text(html, encoding="utf-8")

    n_escolas = len(plotly_payload["data"][0]["y"]) if plotly_payload["data"] else 0
    print(f"Gráfico renderizado em: {out_file}")
    print(f"Título: {grafico['titulo']}")
    print(f"Escolas nesta página: {n_escolas}")
    print(
        f"Paginação: page {paginacao['page']} / "
        f"{max(paginacao['total_paginas'] - 1, 0)} "
        f"(page_size={paginacao['page_size']}, total={paginacao['total_escolas']})"
    )
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
    parser.add_argument("--page", type=int, default=0, help="Página (base 0).")
    parser.add_argument(
        "--page_size", type=int, default=5, help="Escolas por página."
    )
    args = parser.parse_args()

    return asyncio.run(
        _run(
            ano=args.ano,
            municipios=args.municipios,
            variaveis=args.variaveis,
            rede_ensino=args.rede_ensino,
            tp_localizacao=args.tp_localizacao,
            page=args.page,
            page_size=args.page_size,
        )
    )


if __name__ == "__main__":
    main()
