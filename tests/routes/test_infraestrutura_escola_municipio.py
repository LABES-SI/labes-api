from fractions import Fraction

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.dependencies import get_infraestrutura_repository
from app.routes.infraestrutura import router
from app.services.infraestrutura_escola_municipio import InfraestruturaEscolaMunicipioService

SYNTHETIC_KEYS = ("a", "b", "c")


class FakeRepository:
    def __init__(self, rows):
        self.rows = rows

    async def find_escola_municipio_raw(self, school_id, years):
        return [row for row in self.rows if row["year"] in years]


def row(school_id, municipality_code, values, year=2024, municipality_name="M"):
    return {
        "school_id": school_id,
        "year": year,
        "municipality_code": municipality_code,
        "municipality_name": municipality_name,
        **dict(zip(SYNTHETIC_KEYS, values)),
    }


def response(rows, *, school_id=1, years=(2024,)):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_infraestrutura_repository] = lambda: FakeRepository(rows)
    from app.routes import infraestrutura as route_module
    original_service = route_module.InfraestruturaEscolaMunicipioService

    class SyntheticService(InfraestruturaEscolaMunicipioService):
        def __init__(self, repository):
            super().__init__(
                repository,
                indicators=SYNTHETIC_KEYS,
                indicator_set_version="DAD-03A-S*-3-synthetic",
            )

    route_module.InfraestruturaEscolaMunicipioService = SyntheticService
    try:
        params = [("school_id", str(school_id))]
        params.extend(("years", str(year)) for year in years)
        with TestClient(app) as client:
            result = client.get(
                "/infraestrutura/analise-temporal/escola-municipio", params=params
            )
        assert result.status_code == 200, result.text
        payload = result.json()
        assert payload["data"]["indicator_set_homologated"] is False
        assert payload["data"]["indicator_set_version"] == "DAD-03A-S*-3-synthetic"
        return payload["data"]["records"]
    finally:
        route_module.InfraestruturaEscolaMunicipioService = original_service


@pytest.mark.parametrize(
    "case_id,rows,years,expected",
    [
        ("T01", [row(1, 10, [1, 1, 0]), row(2, 10, [1, 0, 1]), row(3, 10, [0, 0, 0])], (2024,),
         [("complete", "available", 2, "200/3", "100/3", "100/3")]),
        ("T02", [row(1, 20, [0, 0, 0]), row(2, 20, [1, 0, 0]), row(3, 20, [0, 0, 0])], (2024,),
         [("complete", "available", 2, "0/1", "50/3", "-50/3")]),
        ("T03", [row(1, 30, [1, 1, 1]), row(2, 30, [1, 1, 0]), row(3, 30, [1, 1, 1])], (2024,),
         [("complete", "available", 2, "100/1", "250/3", "50/3")]),
        ("T04", [row(1, 40, [1, None, 0]), row(2, 40, [1, 0, 1]), row(3, 40, [0, 0, 0])], (2024,),
         [("partial", "nao_avaliada", None, "50/1", None, None)]),
        ("T05", [row(1, 50, [None, None, None]), row(2, 50, [1, 0, 1])], (2024,),
         [("observada_sem_indicadores_validos", "nao_avaliada", None, None, None, None)]),
        ("T06", [row(2, 60, [1, 0, 1])], (2025,),
         [("nao_observada", "nao_avaliada", None, None, None, None)]),
        ("T07", [row(1, 70, [1, 1, 1]), row(2, 70, [1, None, None]), row(3, 70, [None, None, None])], (2024,),
         [("complete", "sem_comparadoras", 0, "100/1", None, None)]),
        ("T08", [row(1, 80, [1, 1, 0]), row(2, 80, [1, 0, 0])], (2024,),
         [("complete", "comparadora_unica", 1, "200/3", "100/3", "100/3")]),
        ("T09", [row(1, 90, [1, 2, 0]), row(2, 90, [1, 0, 0]), row(3, 90, [0, 0, 0])], (2024,),
         [("entrada_invalida", "nao_avaliada", None, None, None, None)]),
        ("T10", [row(1, 100, [1, 1, 1]), row(2, 100, [1, 0, 0]), row(3, 100, [1, 2, 0])], (2024,),
         [("complete", "integridade_referencia", None, "100/1", None, None)]),
        ("T11", [row(1, 110, [1, 1, 1]), row(1, 110, [0, 0, 0]), row(2, 110, [1, 0, 0])], (2024,),
         [("duplicidade_escola_ano", "nao_avaliada", None, None, None, None)]),
        ("T12", [row(1, 120, [1, 1, 1]), row(2, 120, [1, 0, 0]), row(3, 120, [1, 1, 0]), row(3, 120, [0, 0, 0])], (2024,),
         [("complete", "integridade_referencia", None, "100/1", None, None)]),
        ("T13A", [row(1, 130, [1, 1, 1]), row(2, 130, [1, None, None]), row(3, 130, [0, 0, 0])], (2024,),
         [("complete", "comparadora_unica", 1, "100/1", "0/1", "100/1")]),
        ("T13B", [row(1, 131, [1, 1, 1]), row(2, 131, [1, 2, 0]), row(3, 131, [0, 0, 0])], (2024,),
         [("complete", "integridade_referencia", None, "100/1", None, None)]),
        ("T14", [row(1, 140, [1, 1, 1], 2022), row(2, 140, [0, 0, 0], 2022),
                  row(1, 141, [1, 1, 1], 2023), row(3, 141, [1, 0, 0], 2023)], (2022, 2023),
         [("complete", "territorio_pendente", 1, "100/1", "0/1", "100/1"),
          ("complete", "territorio_pendente", 1, "100/1", "100/3", "200/3")]),
        ("T15", [row(1, 150, [1, 1, 1]), row(2, 150, [1, None, None]), row(3, 150, [0, 0, 0])], (2024,),
         [("complete", "comparadora_unica", 1, "100/1", "0/1", "100/1")]),
    ],
    ids=lambda case: case if isinstance(case, str) else None,
)
def test_dad03a_cases_via_http(case_id, rows, years, expected):
    records = response(rows, years=years)
    assert len(records) == len(expected), case_id
    for actual, wanted in zip(records, expected):
        index_status, ref_status, n, index, reference, difference = wanted
        assert actual["index_status"] == index_status, case_id
        assert actual["reference_status"] == ref_status, case_id
        assert actual["n_comparable_schools"] == n, case_id
        assert actual["school_index_pct_exact"] == index, case_id
        assert actual["municipal_mean_excluding_school_pct_exact"] == reference, case_id
        assert actual["difference_pp_exact"] == difference, case_id
        assert actual["n_selected_indicators"] == 3


def test_t15_exposes_mean_versus_grouped_response_trap_via_http():
    result = response([
        row(1, 150, [1, 1, 1]),
        row(2, 150, [1, None, None]),
        row(3, 150, [0, 0, 0]),
    ])[0]
    assert result["municipal_mean_excluding_school_pct_exact"] == "0/1"
    # If the partial school were included, mean of school indices would be 50%;
    # pooling its raw valid responses with Q would be 25%. The provisional
    # complete-coverage result uses only Q (0%).
    assert (Fraction(100, 1) + Fraction(0, 1)) / 2 == Fraction(50, 1)
    assert Fraction(1, 4) * 100 == Fraction(25, 1)


def test_invalid_or_duplicate_year_parameters_return_422():
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_infraestrutura_repository] = lambda: FakeRepository([])
    with TestClient(app) as client:
        invalid = client.get("/infraestrutura/analise-temporal/escola-municipio?school_id=1&years=2021")
        duplicate = client.get("/infraestrutura/analise-temporal/escola-municipio?school_id=1&years=2024&years=2024")
    assert invalid.status_code == 422
    assert duplicate.status_code == 422
