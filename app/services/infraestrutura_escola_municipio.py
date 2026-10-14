"""Experimental School x Municipality calculation for DAD-04.

The 17 candidate indicators are a test profile only; no result or indicator
is homologated by this module.
"""
from collections import Counter
from fractions import Fraction

from app.repositories.infraestrutura_repository import METRIC_KEYS

METHODOLOGY_VERSION = "DAD-05-v0.1-condicional"
INDICATOR_SET_VERSION = "S-candidate-17-v1-nonhomologated"


def _exact(value: Fraction | None) -> str | None:
    if value is None:
        return None
    return f"{value.numerator}/{value.denominator}"


def _value_counts(row: dict, indicators: tuple[str, ...]) -> dict:
    yes = no = nulls = invalid = 0
    invalid_fields: list[str] = []
    for indicator in indicators:
        value = row.get(indicator)
        if value is None:
            nulls += 1
        elif type(value) is int and value == 1:
            yes += 1
        elif type(value) is int and value == 0:
            no += 1
        else:
            invalid += 1
            invalid_fields.append(indicator)
    valid = yes + no
    index = Fraction(100 * yes, valid) if valid and not invalid else None
    return {
        "n_yes": yes,
        "n_no": no,
        "n_null": nulls,
        "n_invalid_indicators": invalid,
        "n_valid_indicators": valid,
        "coverage_exact": _exact(Fraction(valid, len(indicators))),
        "index": index,
        "invalid_fields": invalid_fields,
    }


class InfraestruturaEscolaMunicipioService:
    """Orchestrate the scoped query and exact calculation for the experimental route."""

    def __init__(
        self,
        repository,
        indicators: tuple[str, ...] = tuple(METRIC_KEYS),
        indicator_set_version: str = INDICATOR_SET_VERSION,
    ):
        if not indicators:
            raise ValueError("Indicator set cannot be empty")
        self._repository = repository
        self._indicators = tuple(indicators)
        self._indicator_set_version = indicator_set_version

    async def build(self, *, school_id: int, years: list[int]) -> dict:
        rows = await self._repository.find_escola_municipio_raw(school_id, years)
        rows = [dict(row) for row in rows]
        results = [self._year_result(school_id, year, rows) for year in years]

        observed_codes = {
            item["municipality_code"]
            for item in results
            if item["index_status"] != "nao_observada"
            and item["municipality_code"] is not None
        }
        if len(observed_codes) > 1:
            for item in results:
                if item["municipality_code"] is not None:
                    item["warnings"].append("codigo_municipal_variou_entre_anos_solicitados")
                    if item["reference_status"] in {"available", "comparadora_unica"}:
                        item["reference_status"] = "territorio_pendente"

        return {
            "descricao": "analise_temporal_escola_municipio_experimental",
            "data": {
                "status": "experimental_nao_homologado",
                "methodology_version": METHODOLOGY_VERSION,
                "indicator_set_version": self._indicator_set_version,
                "indicator_set_homologated": False,
                "records": results,
            },
        }

    def _year_result(self, school_id: int, year: int, rows: list[dict]) -> dict:
        selected_rows = [
            row for row in rows
            if row.get("year") == year and row.get("school_id") == school_id
        ]
        base = {
            "year": year,
            "school_id": school_id,
            "municipality_code": None,
            "municipality_name": None,
            "n_selected_indicators": len(self._indicators),
            "n_valid_indicators": None,
            "n_yes": None,
            "n_no": None,
            "n_null": None,
            "n_invalid_indicators": None,
            "coverage_exact": None,
            "eligible_for_comparison": False,
            "school_index_pct_exact": None,
            "index_status": "nao_observada",
            "n_comparable_schools": None,
            "municipal_mean_excluding_school_pct_exact": None,
            "difference_pp_exact": None,
            "reference_status": "nao_avaliada",
            "unavailability_reasons": ["escola_nao_observada_no_ano"],
            "warnings": [],
            "integrity_issues": [],
        }
        if not selected_rows:
            return base
        base["municipality_code"] = selected_rows[0].get("municipality_code")
        base["municipality_name"] = selected_rows[0].get("municipality_name")
        if len(selected_rows) != 1:
            base["index_status"] = "duplicidade_escola_ano"
            base["reference_status"] = "nao_avaliada"
            base["unavailability_reasons"] = ["duplicidade_escola_ano_na_escola_selecionada"]
            base["integrity_issues"] = [
                {"school_id": school_id, "year": year, "issue": "duplicate_school_year"}
            ]
            return base

        selected = selected_rows[0]
        counts = _value_counts(selected, self._indicators)
        for key in (
            "n_valid_indicators", "n_yes", "n_no", "n_null",
            "n_invalid_indicators", "coverage_exact",
        ):
            base[key] = counts[key]
        if counts["n_invalid_indicators"]:
            base["index_status"] = "entrada_invalida"
            base["reference_status"] = "nao_avaliada"
            base["unavailability_reasons"] = ["valor_invalido_na_escola_selecionada"]
            base["integrity_issues"] = [
                {"school_id": school_id, "year": year, "issue": "invalid_indicator", "indicator": field}
                for field in counts["invalid_fields"]
            ]
            return base
        if counts["n_valid_indicators"] == 0:
            base["index_status"] = "observada_sem_indicadores_validos"
            base["reference_status"] = "nao_avaliada"
            base["unavailability_reasons"] = ["observada_sem_indicadores_validos"]
            return base

        base["school_index_pct_exact"] = _exact(counts["index"])
        if counts["n_valid_indicators"] < len(self._indicators):
            base["index_status"] = "partial"
            base["reference_status"] = "nao_avaliada"
            base["unavailability_reasons"] = ["cobertura_completa_exigida_no_perfil_experimental"]
            return base

        base["index_status"] = "complete"
        base["eligible_for_comparison"] = True
        municipality_code = selected.get("municipality_code")
        if municipality_code is None:
            base["reference_status"] = "territorio_pendente"
            base["unavailability_reasons"] = ["codigo_municipal_ausente_na_observacao"]
            return base

        group = [
            row for row in rows
            if row.get("year") == year and row.get("municipality_code") == municipality_code
        ]
        other_rows = [row for row in group if row.get("school_id") != school_id]
        issues: list[dict] = []
        key_counts = Counter(row.get("school_id") for row in other_rows)
        for other_id, count in key_counts.items():
            if other_id is None:
                issues.append({"school_id": None, "year": year, "issue": "missing_school_id"})
            elif count > 1:
                issues.append({"school_id": other_id, "year": year, "issue": "duplicate_school_year"})

        eligible_indices: list[Fraction] = []
        for row in other_rows:
            other_id = row.get("school_id")
            if other_id is None:
                continue
            candidate = _value_counts(row, self._indicators)
            for field in candidate["invalid_fields"]:
                issues.append({
                    "school_id": other_id,
                    "year": year,
                    "issue": "invalid_indicator",
                    "indicator": field,
                })
            if candidate["n_invalid_indicators"]:
                continue
            if candidate["n_valid_indicators"] == len(self._indicators):
                eligible_indices.append(candidate["index"])
            # Partial coverage and all-NULL observations are methodological
            # exclusions in this provisional profile, not integrity blockers.

        if issues:
            base["reference_status"] = "integridade_referencia"
            base["unavailability_reasons"] = ["integridade_na_composicao_das_comparadoras"]
            base["integrity_issues"] = issues
            return base
        n = len(eligible_indices)
        base["n_comparable_schools"] = n
        if n == 0:
            base["reference_status"] = "sem_comparadoras"
            base["unavailability_reasons"] = ["sem_comparadoras_elegiveis"]
            return base

        reference = sum(eligible_indices, Fraction(0, 1)) / n
        base["municipal_mean_excluding_school_pct_exact"] = _exact(reference)
        base["difference_pp_exact"] = _exact(counts["index"] - reference)
        base["reference_status"] = "comparadora_unica" if n == 1 else "available"
        if n == 1:
            base["warnings"].append("referencia_depende_de_uma_comparadora")
        return base
