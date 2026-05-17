"""Renderiza um HTML por valor de cada filtro do painel de acessibilidade.

Percorre o mesmo caminho da rota `/acessibilidade/painel` e gera três
conjuntos de arquivos em `tests/visual/out/`:

  - por_municipio/<slug>.html — painel filtrado por aquele município
  - por_ano/<ano>.html         — painel filtrado por aquele ano do censo
  - por_metrica/<chave>.html   — painel renderizando aquela métrica

Uso:
    uv run python -m tests.visual.render_filtros
"""

import asyncio
import json
import re
import unicodedata
from pathlib import Path

import plotly.io as pio

from app.core.dependencies import SessionLocal, async_engine
from app.repositories.acessibilidade_repository import AcessibilidadeRepository
from app.services.acessibilidade_service import METRIC_FIELDS, AcessibilidadeService


OUT_DIR = Path(__file__).parent / "out"
DEFAULT_METRICA = "in_banheiro_pne"


def _slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", ascii_only).strip("_").lower()
    return slug or "vazio"


def _write_html(painel: dict, out_file: Path) -> int:
    grafico = painel["data"]["graficos"]["tab_percent_acessibilidade"]
    plotly_payload = grafico["plotly"]
    figure = pio.from_json(json.dumps(plotly_payload))
    out_file.parent.mkdir(parents=True, exist_ok=True)
    figure.write_html(out_file, include_plotlyjs="cdn", full_html=True)
    return len(plotly_payload["data"][0]["x"]) if plotly_payload["data"] else 0


async def _run() -> None:
    try:
        async with SessionLocal() as session:
            repository = AcessibilidadeRepository(session)
            service = AcessibilidadeService(repository)

            municipios = await repository.find_municipios_disponiveis()
            anos = await repository.find_anos_disponiveis()

            print(f"Por município ({len(municipios)}):")
            for _, nome in municipios:
                painel = await service.build_painel(
                    ano=None, municipios=[nome], metrica=DEFAULT_METRICA
                )
                out = OUT_DIR / "por_municipio" / f"{_slugify(nome)}.html"
                n = _write_html(painel, out)
                print(f"  {nome}: {n} barra(s) -> {out.relative_to(OUT_DIR.parent)}")

            print(f"\nPor ano ({len(anos)}):")
            for ano in anos:
                painel = await service.build_painel(
                    ano=ano, municipios=None, metrica=DEFAULT_METRICA
                )
                out = OUT_DIR / "por_ano" / f"{ano}.html"
                n = _write_html(painel, out)
                print(f"  {ano}: {n} barra(s) -> {out.relative_to(OUT_DIR.parent)}")

            print(f"\nPor métrica ({len(METRIC_FIELDS)}):")
            for chave, label in METRIC_FIELDS:
                painel = await service.build_painel(
                    ano=None, municipios=None, metrica=chave
                )
                out = OUT_DIR / "por_metrica" / f"{chave}.html"
                n = _write_html(painel, out)
                print(f"  {label}: {n} barra(s) -> {out.relative_to(OUT_DIR.parent)}")
    finally:
        await async_engine.dispose()


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
