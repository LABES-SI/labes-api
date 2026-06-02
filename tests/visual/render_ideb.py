"""Compara o output do pipeline /acessibilidade/ideb com a query SQL original.

Imprime o resultado JSON do endpoint simulado.
Salva a figura Plotly gerada em HTML em tests/visual/out/cruzamento_ideb.html.

Uso:
    uv run python -m tests.visual.render_ideb
"""

import argparse
import asyncio
import json
from pathlib import Path

import plotly.graph_objects as go

from app.core.dependencies import SessionLocal, async_engine
from app.repositories.acessibilidade_repository import AcessibilidadeRepository
from app.services.acessibilidade_service import AcessibilidadeService


async def _run(ano: int | None) -> None:
    try:
        async with SessionLocal() as session:
            repo = AcessibilidadeRepository(session)
            service = AcessibilidadeService(repo)
            grafico = await service.build_analise_ideb(
                ano=ano,
                municipios=None,
                variaveis=None,
                rede_ensino=None,
                tp_localizacao=None,
            )
            
            # Print endpoint response body structure (similar to FastAPI returning it)
            envelope = {
                "descricao": "cruzamento_ideb",
                "data": {
                    "graficos": {
                        "scatter_ideb": grafico
                    }
                }
            }
            
            print("==================================================")
            print("RESPONSE BODY DO ENDPOINT (TRUNCADO PARA LEITURA):")
            print("==================================================")
            json_str = json.dumps(envelope, indent=2, ensure_ascii=False)
            print(json_str[:1500] + "\n... [Restante do JSON omitido] ...\n")
            print("==================================================")
            
            # Recreate figure from JSON to save it
            fig = go.Figure(grafico["plotly"])
            
    finally:
        await async_engine.dispose()

    out_dir = Path(__file__).parent / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / "cruzamento_ideb.html"
    fig.write_html(str(html_path))

    print(f"HTML do gráfico salvo com sucesso em: {html_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ano",
        type=int,
        default=2023,
        help="Filtra pelo ano do censo (nu_ano_censo). Padrão = 2023.",
    )
    args = parser.parse_args()
    asyncio.run(_run(ano=args.ano))


if __name__ == "__main__":
    main()
