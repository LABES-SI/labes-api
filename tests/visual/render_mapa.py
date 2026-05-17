"""Compara o output do pipeline /acessibilidade/mapa com a query SQL original.

Executa dois caminhos contra o warehouse e bate os DataFrames:

1. Pipeline novo: AcessibilidadeRepository.find_pontos_mapa -> DataFrame.
2. Query bruta fornecida pelo usuário (query_mapa) executada via sessão.

Imprime diferenças de shape, contagem por classificação e diff de linhas.
Salva ambos em tests/visual/out/ como CSV para inspeção.

Uso:
    uv run python -m tests.visual.render_mapa
    uv run python -m tests.visual.render_mapa --ano 2023
"""

import argparse
import asyncio
from dataclasses import asdict
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from app.core.dependencies import SessionLocal, async_engine
from app.repositories.acessibilidade_repository import AcessibilidadeRepository


QUERY_MAPA_ORIGINAL = """
SELECT
    e.co_entidade,
    e.no_entidade,
    m.no_municipio,
    e.no_bairro,
    e.latitude,
    e.longitude,
    d.no_tp_dependencia,
    l.no_tp_localizacao,
    (
        COALESCE(f.in_sala_atendimento_especial, 0) +
        COALESCE(f.in_banheiro_pne, 0) +
        COALESCE(f.in_acessibilidade_rampas, 0) +
        COALESCE(f.in_acessibilidade_corrimao, 0) +
        COALESCE(f.in_acessibilidade_elevador, 0) +
        COALESCE(f.in_acessibilidade_pisos_tateis, 0) +
        COALESCE(f.in_acessibilidade_vao_livre, 0) +
        COALESCE(f.in_acessibilidade_sinal_visual, 0) +
        COALESCE(f.in_acessibilidade_sinal_sonoro, 0) +
        COALESCE(f.in_acessibilidade_sinal_tatil, 0) +
        COALESCE(f.in_acessibilidade_sinalizacao, 0)
    ) AS score_acessibilidade,

    CASE
        WHEN (
            COALESCE(f.in_sala_atendimento_especial, 0) +
            COALESCE(f.in_banheiro_pne, 0) +
            COALESCE(f.in_acessibilidade_rampas, 0) +
            COALESCE(f.in_acessibilidade_corrimao, 0) +
            COALESCE(f.in_acessibilidade_elevador, 0) +
            COALESCE(f.in_acessibilidade_pisos_tateis, 0) +
            COALESCE(f.in_acessibilidade_vao_livre, 0) +
            COALESCE(f.in_acessibilidade_sinal_visual, 0) +
            COALESCE(f.in_acessibilidade_sinal_sonoro, 0) +
            COALESCE(f.in_acessibilidade_sinal_tatil, 0) +
            COALESCE(f.in_acessibilidade_sinalizacao, 0)
        ) >= 8 THEN 'Boa'

        WHEN (
            COALESCE(f.in_sala_atendimento_especial, 0) +
            COALESCE(f.in_banheiro_pne, 0) +
            COALESCE(f.in_acessibilidade_rampas, 0) +
            COALESCE(f.in_acessibilidade_elevador, 0) +
            COALESCE(f.in_acessibilidade_pisos_tateis, 0) +
            COALESCE(f.in_acessibilidade_vao_livre, 0) +
            COALESCE(f.in_acessibilidade_sinal_visual, 0) +
            COALESCE(f.in_acessibilidade_sinal_sonoro, 0) +
            COALESCE(f.in_acessibilidade_sinal_tatil, 0) +
            COALESCE(f.in_acessibilidade_sinalizacao, 0)
        ) >= 5 THEN 'Média'

        WHEN (
            COALESCE(f.in_sala_atendimento_especial, 0) +
            COALESCE(f.in_banheiro_pne, 0) +
            COALESCE(f.in_acessibilidade_rampas, 0) +
            COALESCE(f.in_acessibilidade_elevador, 0) +
            COALESCE(f.in_acessibilidade_pisos_tateis, 0) +
            COALESCE(f.in_acessibilidade_vao_livre, 0) +
            COALESCE(f.in_acessibilidade_sinal_visual, 0) +
            COALESCE(f.in_acessibilidade_sinal_sonoro, 0) +
            COALESCE(f.in_acessibilidade_sinal_tatil, 0)
        ) >= 1 THEN 'Baixa'

        ELSE 'Inexistente'
    END AS classificacao_acessibilidade

FROM silver.fato_acessibilidade f
LEFT JOIN silver.dim_entidade e ON f.co_entidade = e.co_entidade
LEFT JOIN silver.dim_municipio m ON e.co_municipio = m.co_municipio
LEFT JOIN silver.dim_tp_dependencia d ON e.tp_dependencia = d.co_tp_dependencia
LEFT JOIN silver.dim_tp_localizacao l ON e.tp_localizacao = l.co_tp_localizacao
WHERE e.latitude IS NOT NULL AND e.longitude IS NOT NULL
"""


COLUNAS_ORDENADAS = [
    "co_entidade",
    "no_entidade",
    "no_municipio",
    "no_bairro",
    "latitude",
    "longitude",
    "no_tp_dependencia",
    "no_tp_localizacao",
    "score_acessibilidade",
    "classificacao_acessibilidade",
]


async def _df_pipeline(ano: int | None) -> pd.DataFrame:
    async with SessionLocal() as session:
        repo = AcessibilidadeRepository(session)
        pontos = await repo.find_pontos_mapa(
            ano=ano,
            municipios=None,
            variaveis=None,
            rede_ensino=None,
            tp_localizacao=None,
        )
    rows = [asdict(p) for p in pontos]
    return pd.DataFrame(rows, columns=COLUNAS_ORDENADAS)


async def _df_query_bruta(ano: int | None) -> pd.DataFrame:
    sql = QUERY_MAPA_ORIGINAL
    if ano is not None:
        sql += f"\n  AND f.nu_ano_censo = {int(ano)}\n"
    async with SessionLocal() as session:
        result = await session.execute(text(sql))
        rows = result.mappings().all()
    return pd.DataFrame(rows, columns=COLUNAS_ORDENADAS)


def _normaliza(df: pd.DataFrame) -> pd.DataFrame:
    df = df[COLUNAS_ORDENADAS].copy()
    df["latitude"] = df["latitude"].astype(float)
    df["longitude"] = df["longitude"].astype(float)
    df["score_acessibilidade"] = df["score_acessibilidade"].astype(int)
    return df.sort_values("co_entidade", kind="mergesort").reset_index(drop=True)


async def _run(ano: int | None) -> None:
    try:
        pipeline_df = _normaliza(await _df_pipeline(ano))
        bruta_df = _normaliza(await _df_query_bruta(ano))
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
        return

    iguais = pipeline_df.equals(bruta_df)
    print(f"DataFrames idênticos linha-a-linha? {iguais}")
    if not iguais:
        diff_score = (
            pipeline_df["score_acessibilidade"] != bruta_df["score_acessibilidade"]
        ).sum()
        diff_classif = (
            pipeline_df["classificacao_acessibilidade"]
            != bruta_df["classificacao_acessibilidade"]
        ).sum()
        print(f"  linhas com score diferente:          {diff_score}")
        print(f"  linhas com classificação diferente:  {diff_classif}")
        print()
        print("Primeiras 5 linhas com divergência de score:")
        mask = (
            pipeline_df["score_acessibilidade"] != bruta_df["score_acessibilidade"]
        )
        if mask.any():
            print(
                pd.concat(
                    [
                        pipeline_df.loc[mask, ["co_entidade", "score_acessibilidade"]]
                        .head(5)
                        .rename(columns={"score_acessibilidade": "score_pipeline"}),
                        bruta_df.loc[mask, ["score_acessibilidade"]]
                        .head(5)
                        .rename(columns={"score_acessibilidade": "score_bruta"})
                        .reset_index(drop=True),
                    ],
                    axis=1,
                ).to_string(index=False)
            )

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
