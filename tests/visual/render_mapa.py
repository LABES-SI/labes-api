"""Confere o pipeline do /acessibilidade/mapa contra a query bruta do notebook.

O /mapa agora lê direto de gold.fato_score_acessibilidade (score e classificação
pré-computados). Este script executa dois caminhos contra o warehouse e bate os
DataFrames:

1. Pipeline: AcessibilidadeRepository.find_pontos_mapa_raw -> DataFrame.
2. Query bruta do notebook: SELECT * FROM gold.fato_score_acessibilidade.

Imprime diferenças de shape, contagem por classificação e se batem linha-a-linha.
Salva ambos em tests/visual/out/ como CSV para inspeção.

Uso:
    uv run python -m tests.visual.render_mapa
    uv run python -m tests.visual.render_mapa --ano 2024
"""

import argparse
import asyncio
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from app.core.dependencies import SessionLocal, async_engine
from app.repositories.acessibilidade_repository import AcessibilidadeRepository


QUERY_MAPA = "SELECT * FROM gold.fato_score_acessibilidade"


async def _df_pipeline(ano: int | None) -> pd.DataFrame:
    repo = AcessibilidadeRepository(SessionLocal, semaphore=None)
    pontos = await repo.find_pontos_mapa_raw(ano=ano, variaveis=None)
    return pd.DataFrame(pontos)


async def _df_query_bruta(ano: int | None) -> pd.DataFrame:
    sql = QUERY_MAPA
    if ano is not None:
        sql += f" WHERE nu_ano_censo = {int(ano)}"
    async with SessionLocal() as session:
        result = await session.execute(text(sql))
        rows = result.mappings().all()
    return pd.DataFrame(rows)


async def _run(ano: int | None) -> None:
    try:
        pipeline_df = await _df_pipeline(ano)
        bruta_df = await _df_query_bruta(ano)
    finally:
        await async_engine.dispose()

    out_dir = Path(__file__).parent / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    pipeline_df.to_csv(out_dir / "mapa_pipeline.csv", index=False)
    bruta_df.to_csv(out_dir / "mapa_query_bruta.csv", index=False)

    print(f"Linhas pipeline:    {len(pipeline_df)}")
    print(f"Linhas query bruta: {len(bruta_df)}")
    print()
    print("Classificação (pipeline):")
    print(pipeline_df["classificacao_acessibilidade"].value_counts().to_string())
    print()
    print("Classificação (query bruta):")
    print(bruta_df["classificacao_acessibilidade"].value_counts().to_string())
    print()

    if pipeline_df.shape != bruta_df.shape:
        print(f"DIVERGÊNCIA de shape: {pipeline_df.shape} vs {bruta_df.shape}")
    else:
        a = pipeline_df.sort_values("co_entidade", kind="mergesort").reset_index(drop=True)
        b = bruta_df.sort_values("co_entidade", kind="mergesort").reset_index(drop=True)
        cols = [c for c in ("co_entidade", "nu_ano_censo", "score_acessibilidade",
                            "classificacao_acessibilidade") if c in a.columns and c in b.columns]
        iguais = a[cols].equals(b[cols])
        print(f"score/classificação idênticos por (co_entidade, nu_ano_censo)? {iguais}")

    print()
    print(f"CSVs salvos em: {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ano",
        type=int,
        default=None,
        help="Filtra pelo ano do censo (nu_ano_censo). Omitir = todos os anos.",
    )
    args = parser.parse_args()
    asyncio.run(_run(ano=args.ano))


if __name__ == "__main__":
    main()
