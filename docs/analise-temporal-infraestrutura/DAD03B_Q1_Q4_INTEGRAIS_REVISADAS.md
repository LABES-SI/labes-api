# SIE — DAD-03B | Q1–Q4 integrais para preparação de executor

# SIE — DAD-03B | SQL de leitura exploratória (Q1–Q4)

**Origem:** consultas integrais recuperadas do material compartilhado anteriormente na conversa (`Texto colado(5).txt`). São propostas elaboradas no Codex e **não foram executadas nem validadas pelo parser do PostgreSQL**.

**Escopo:** amostra exploratória sobre o conjunto candidato de 17 campos. DAD-01 NÃO HOMOLOGADA; DAD-02 preliminar; DAD-05 condicional; conjunto S não homologado. Nenhum resultado oficial está autorizado.



As consultas abaixo incluem os quatro ajustes registrados em `LEIA-ME.md`. **Não executadas.**

## Q1

```sql

WITH
years AS (
    SELECT unnest(ARRAY[2022, 2023, 2024, 2025]::integer[]) AS year
),
source_rows AS (
    SELECT
        s."NU_ANO_CENSO" AS year,
        s."CO_MUNICIPIO" AS municipality_code,
        s."CO_ENTIDADE" AS school_id,
        s."IN_AGUA_POTAVEL",
        s."IN_ENERGIA_REDE_PUBLICA",
        s."IN_ESGOTO_REDE_PUBLICA",
        s."IN_LIXO_SERVICO_COLETA",
        s."IN_BANHEIRO",
        s."IN_BANHEIRO_PNE",
        s."IN_BIBLIOTECA",
        s."IN_SALA_LEITURA",
        s."IN_LABORATORIO_CIENCIAS",
        s."IN_LABORATORIO_INFORMATICA",
        s."IN_SALA_MULTIUSO",
        s."IN_SALA_ATENDIMENTO_ESPECIAL",
        s."IN_COZINHA",
        s."IN_REFEITORIO",
        s."IN_QUADRA_ESPORTES",
        s."IN_PATIO_COBERTO",
        s."IN_AUDITORIO",
        (
            s."IN_AGUA_POTAVEL" IS NOT NULL
            AND s."IN_ENERGIA_REDE_PUBLICA" IS NOT NULL
            AND s."IN_ESGOTO_REDE_PUBLICA" IS NOT NULL
            AND s."IN_LIXO_SERVICO_COLETA" IS NOT NULL
            AND s."IN_BANHEIRO" IS NOT NULL
            AND s."IN_BANHEIRO_PNE" IS NOT NULL
            AND s."IN_BIBLIOTECA" IS NOT NULL
            AND s."IN_SALA_LEITURA" IS NOT NULL
            AND s."IN_LABORATORIO_CIENCIAS" IS NOT NULL
            AND s."IN_LABORATORIO_INFORMATICA" IS NOT NULL
            AND s."IN_SALA_MULTIUSO" IS NOT NULL
            AND s."IN_SALA_ATENDIMENTO_ESPECIAL" IS NOT NULL
            AND s."IN_COZINHA" IS NOT NULL
            AND s."IN_REFEITORIO" IS NOT NULL
            AND s."IN_QUADRA_ESPORTES" IS NOT NULL
            AND s."IN_PATIO_COBERTO" IS NOT NULL
            AND s."IN_AUDITORIO" IS NOT NULL
            AND s."IN_AGUA_POTAVEL" IN (0, 1)
            AND s."IN_ENERGIA_REDE_PUBLICA" IN (0, 1)
            AND s."IN_ESGOTO_REDE_PUBLICA" IN (0, 1)
            AND s."IN_LIXO_SERVICO_COLETA" IN (0, 1)
            AND s."IN_BANHEIRO" IN (0, 1)
            AND s."IN_BANHEIRO_PNE" IN (0, 1)
            AND s."IN_BIBLIOTECA" IN (0, 1)
            AND s."IN_SALA_LEITURA" IN (0, 1)
            AND s."IN_LABORATORIO_CIENCIAS" IN (0, 1)
            AND s."IN_LABORATORIO_INFORMATICA" IN (0, 1)
            AND s."IN_SALA_MULTIUSO" IN (0, 1)
            AND s."IN_SALA_ATENDIMENTO_ESPECIAL" IN (0, 1)
            AND s."IN_COZINHA" IN (0, 1)
            AND s."IN_REFEITORIO" IN (0, 1)
            AND s."IN_QUADRA_ESPORTES" IN (0, 1)
            AND s."IN_PATIO_COBERTO" IN (0, 1)
            AND s."IN_AUDITORIO" IN (0, 1)
        ) AS is_complete,
        (
            s."IN_AGUA_POTAVEL" IS NULL
            AND s."IN_ENERGIA_REDE_PUBLICA" IS NULL
            AND s."IN_ESGOTO_REDE_PUBLICA" IS NULL
            AND s."IN_LIXO_SERVICO_COLETA" IS NULL
            AND s."IN_BANHEIRO" IS NULL
            AND s."IN_BANHEIRO_PNE" IS NULL
            AND s."IN_BIBLIOTECA" IS NULL
            AND s."IN_SALA_LEITURA" IS NULL
            AND s."IN_LABORATORIO_CIENCIAS" IS NULL
            AND s."IN_LABORATORIO_INFORMATICA" IS NULL
            AND s."IN_SALA_MULTIUSO" IS NULL
            AND s."IN_SALA_ATENDIMENTO_ESPECIAL" IS NULL
            AND s."IN_COZINHA" IS NULL
            AND s."IN_REFEITORIO" IS NULL
            AND s."IN_QUADRA_ESPORTES" IS NULL
            AND s."IN_PATIO_COBERTO" IS NULL
            AND s."IN_AUDITORIO" IS NULL
        ) AS is_all_null,
        (
            (s."IN_AGUA_POTAVEL" IS NOT NULL AND s."IN_AGUA_POTAVEL" NOT IN (0, 1))
            OR (s."IN_ENERGIA_REDE_PUBLICA" IS NOT NULL AND s."IN_ENERGIA_REDE_PUBLICA" NOT IN (0, 1))
            OR (s."IN_ESGOTO_REDE_PUBLICA" IS NOT NULL AND s."IN_ESGOTO_REDE_PUBLICA" NOT IN (0, 1))
            OR (s."IN_LIXO_SERVICO_COLETA" IS NOT NULL AND s."IN_LIXO_SERVICO_COLETA" NOT IN (0, 1))
            OR (s."IN_BANHEIRO" IS NOT NULL AND s."IN_BANHEIRO" NOT IN (0, 1))
            OR (s."IN_BANHEIRO_PNE" IS NOT NULL AND s."IN_BANHEIRO_PNE" NOT IN (0, 1))
            OR (s."IN_BIBLIOTECA" IS NOT NULL AND s."IN_BIBLIOTECA" NOT IN (0, 1))
            OR (s."IN_SALA_LEITURA" IS NOT NULL AND s."IN_SALA_LEITURA" NOT IN (0, 1))
            OR (s."IN_LABORATORIO_CIENCIAS" IS NOT NULL AND s."IN_LABORATORIO_CIENCIAS" NOT IN (0, 1))
            OR (s."IN_LABORATORIO_INFORMATICA" IS NOT NULL AND s."IN_LABORATORIO_INFORMATICA" NOT IN (0, 1))
            OR (s."IN_SALA_MULTIUSO" IS NOT NULL AND s."IN_SALA_MULTIUSO" NOT IN (0, 1))
            OR (s."IN_SALA_ATENDIMENTO_ESPECIAL" IS NOT NULL AND s."IN_SALA_ATENDIMENTO_ESPECIAL" NOT IN (0, 1))
            OR (s."IN_COZINHA" IS NOT NULL AND s."IN_COZINHA" NOT IN (0, 1))
            OR (s."IN_REFEITORIO" IS NOT NULL AND s."IN_REFEITORIO" NOT IN (0, 1))
            OR (s."IN_QUADRA_ESPORTES" IS NOT NULL AND s."IN_QUADRA_ESPORTES" NOT IN (0, 1))
            OR (s."IN_PATIO_COBERTO" IS NOT NULL AND s."IN_PATIO_COBERTO" NOT IN (0, 1))
            OR (s."IN_AUDITORIO" IS NOT NULL AND s."IN_AUDITORIO" NOT IN (0, 1))
        ) AS has_invalid_value
    FROM silver.infraestrutura_comum AS s
    WHERE s."NU_ANO_CENSO" IN (2022, 2023, 2024, 2025)
),
school_year_keys AS (
    SELECT
        year,
        school_id,
        count(*) AS source_rows_for_key,
        bool_and(is_complete) AS all_rows_complete,
        bool_and(is_all_null) AS all_rows_all_null,
        bool_or(has_invalid_value) AS key_has_invalid_value
    FROM source_rows
    WHERE school_id IS NOT NULL
    GROUP BY year, school_id
),
municipality_metrics AS (
    SELECT
        r.year,
        r.municipality_code,
        count(*) AS total_source_rows,
        count(DISTINCT r.school_id) AS identified_school_year_keys,
        count(*) FILTER (WHERE r.school_id IS NULL) AS rows_without_identifier,
        count(DISTINCT r.school_id) FILTER (
            WHERE k.source_rows_for_key > 1
        ) AS duplicate_school_year_keys,
        count(*) FILTER (WHERE r.has_invalid_value) AS invalid_source_rows,
        count(DISTINCT r.school_id) FILTER (
            WHERE k.key_has_invalid_value
        ) AS invalid_school_year_keys,
        count(DISTINCT r.school_id) FILTER (
            WHERE k.source_rows_for_key = 1
              AND k.all_rows_complete
              AND NOT k.key_has_invalid_value
        ) AS complete_school_year_keys,
        count(DISTINCT r.school_id) FILTER (
            WHERE k.source_rows_for_key = 1
              AND k.all_rows_all_null
              AND NOT k.key_has_invalid_value
        ) AS all_null_school_year_keys
    FROM source_rows AS r
    LEFT JOIN school_year_keys AS k
      ON k.year = r.year
     AND k.school_id = r.school_id
    GROUP BY r.year, r.municipality_code
),
ranked_reference_municipalities AS (
    SELECT
        m.*,
        row_number() OVER (
            PARTITION BY m.year
            ORDER BY
                (m.complete_school_year_keys >= 2) DESC,
                m.identified_school_year_keys ASC,
                m.total_source_rows ASC,
                m.municipality_code ASC
        ) AS selection_rank
    FROM municipality_metrics AS m
    WHERE m.municipality_code IS NOT NULL
      AND m.duplicate_school_year_keys = 0
      AND m.rows_without_identifier = 0
      AND m.invalid_source_rows = 0
      AND m.invalid_school_year_keys = 0
      AND m.complete_school_year_keys > 0
),
reference_choice AS (
    SELECT *
    FROM ranked_reference_municipalities
    WHERE selection_rank = 1
),
selected_complete AS (
    SELECT DISTINCT ON (r.year)
        r.year,
        r.municipality_code AS reference_municipality_code,
        r.school_id AS selected_school_id
    FROM source_rows AS r
    JOIN reference_choice AS c
      ON c.year = r.year
     AND c.municipality_code = r.municipality_code
    JOIN school_year_keys AS k
      ON k.year = r.year
     AND k.school_id = r.school_id
    WHERE r.school_id IS NOT NULL
      AND k.source_rows_for_key = 1
      AND k.all_rows_complete
      AND NOT k.key_has_invalid_value
    ORDER BY r.year, r.school_id ASC
),
ranked_all_null_samples AS (
    SELECT
        r.year,
        r.municipality_code AS null_sample_municipality_code,
        r.school_id AS null_sample_school_id,
        row_number() OVER (
            PARTITION BY r.year
            ORDER BY
                (r.municipality_code = c.municipality_code) DESC NULLS LAST,
                m.identified_school_year_keys ASC NULLS LAST,
                r.municipality_code ASC,
                r.school_id ASC
        ) AS selection_rank
    FROM source_rows AS r
    JOIN school_year_keys AS k
      ON k.year = r.year
     AND k.school_id = r.school_id
    LEFT JOIN reference_choice AS c
      ON c.year = r.year
    LEFT JOIN municipality_metrics AS m
      ON m.year = r.year
     AND m.municipality_code = r.municipality_code
    WHERE r.school_id IS NOT NULL
      AND r.municipality_code IS NOT NULL
      AND k.source_rows_for_key = 1
      AND k.all_rows_all_null
      AND NOT k.key_has_invalid_value
),
null_sample_choice AS (
    SELECT *
    FROM ranked_all_null_samples
    WHERE selection_rank = 1
),
years_with_reference AS (
    SELECT
        y.year,
        c.municipality_code AS reference_municipality_code,
        c.total_source_rows AS reference_total_source_rows,
        c.identified_school_year_keys AS reference_identified_school_year_keys,
        c.duplicate_school_year_keys AS reference_duplicate_school_year_keys,
        c.rows_without_identifier AS reference_rows_without_identifier,
        c.invalid_source_rows AS reference_invalid_source_rows,
        c.invalid_school_year_keys AS reference_invalid_school_year_keys,
        c.complete_school_year_keys AS reference_complete_school_year_keys,
        s.selected_school_id
    FROM years AS y
    LEFT JOIN reference_choice AS c
      ON c.year = y.year
    LEFT JOIN selected_complete AS s
      ON s.year = y.year
     AND s.reference_municipality_code = c.municipality_code
),
null_sample_denominators AS (
    SELECT
        n.year,
        n.null_sample_municipality_code,
        n.null_sample_school_id,
        m.total_source_rows AS null_sample_municipality_total_source_rows,
        m.identified_school_year_keys AS null_sample_municipality_identified_school_year_keys,
        m.all_null_school_year_keys AS null_sample_municipality_all_null_school_year_keys,
        m.duplicate_school_year_keys AS null_sample_municipality_duplicate_school_year_keys,
        m.rows_without_identifier AS null_sample_municipality_rows_without_identifier,
        m.invalid_source_rows AS null_sample_municipality_invalid_source_rows,
        m.invalid_school_year_keys AS null_sample_municipality_invalid_school_year_keys
    FROM null_sample_choice AS n
    LEFT JOIN municipality_metrics AS m
      ON m.year = n.year
     AND m.municipality_code = n.null_sample_municipality_code
)
SELECT
    r.year,
    r.reference_municipality_code,
    r.selected_school_id,
    r.reference_total_source_rows,
    r.reference_identified_school_year_keys,
    r.reference_complete_school_year_keys,
    (
        r.reference_complete_school_year_keys
        - CASE WHEN r.selected_school_id IS NOT NULL THEN 1 ELSE 0 END
    ) AS eligible_complete_excluding_selected,
    r.reference_duplicate_school_year_keys,
    r.reference_rows_without_identifier,
    r.reference_invalid_source_rows,
    r.reference_invalid_school_year_keys,
    n.null_sample_municipality_code,
    n.null_sample_school_id,
    n.null_sample_municipality_total_source_rows,
    n.null_sample_municipality_identified_school_year_keys,
    n.null_sample_municipality_all_null_school_year_keys,
    n.null_sample_municipality_duplicate_school_year_keys,
    n.null_sample_municipality_rows_without_identifier,
    n.null_sample_municipality_invalid_source_rows,
    n.null_sample_municipality_invalid_school_year_keys
FROM years_with_reference AS r
LEFT JOIN null_sample_denominators AS n
  ON n.year = r.year
ORDER BY r.year;

```

## Q2

```sql

WITH
params AS (
    SELECT *
    FROM (VALUES
        (2022, $1::integer, $2::bigint, $3::integer, $4::bigint),
        (2023, $5::integer, $6::bigint, $7::integer, $8::bigint),
        (2024, $9::integer, $10::bigint, $11::integer, $12::bigint),
        (2025, $13::integer, $14::bigint, $15::integer, $16::bigint)
    ) AS p(
        year,
        reference_municipality_code,
        selected_school_id,
        null_sample_municipality_code,
        null_sample_school_id
    )
),
source_rows AS (
    SELECT
        s."CO_MUNICIPIO" AS municipality_code,
        s."CO_ENTIDADE" AS school_id,
        s."NU_ANO_CENSO" AS year,
        s."NO_ENTIDADE" AS school_name,
        s."NO_MUNICIPIO" AS municipality_name,
        s."IN_AGUA_POTAVEL",
        s."IN_ENERGIA_REDE_PUBLICA",
        s."IN_ESGOTO_REDE_PUBLICA",
        s."IN_LIXO_SERVICO_COLETA",
        s."IN_BANHEIRO",
        s."IN_BANHEIRO_PNE",
        s."IN_BIBLIOTECA",
        s."IN_SALA_LEITURA",
        s."IN_LABORATORIO_CIENCIAS",
        s."IN_LABORATORIO_INFORMATICA",
        s."IN_SALA_MULTIUSO",
        s."IN_SALA_ATENDIMENTO_ESPECIAL",
        s."IN_COZINHA",
        s."IN_REFEITORIO",
        s."IN_QUADRA_ESPORTES",
        s."IN_PATIO_COBERTO",
        s."IN_AUDITORIO",
        (
            (s."IN_AGUA_POTAVEL" IS NOT NULL AND s."IN_AGUA_POTAVEL" NOT IN (0, 1))
            OR (s."IN_ENERGIA_REDE_PUBLICA" IS NOT NULL AND s."IN_ENERGIA_REDE_PUBLICA" NOT IN (0, 1))
            OR (s."IN_ESGOTO_REDE_PUBLICA" IS NOT NULL AND s."IN_ESGOTO_REDE_PUBLICA" NOT IN (0, 1))
            OR (s."IN_LIXO_SERVICO_COLETA" IS NOT NULL AND s."IN_LIXO_SERVICO_COLETA" NOT IN (0, 1))
            OR (s."IN_BANHEIRO" IS NOT NULL AND s."IN_BANHEIRO" NOT IN (0, 1))
            OR (s."IN_BANHEIRO_PNE" IS NOT NULL AND s."IN_BANHEIRO_PNE" NOT IN (0, 1))
            OR (s."IN_BIBLIOTECA" IS NOT NULL AND s."IN_BIBLIOTECA" NOT IN (0, 1))
            OR (s."IN_SALA_LEITURA" IS NOT NULL AND s."IN_SALA_LEITURA" NOT IN (0, 1))
            OR (s."IN_LABORATORIO_CIENCIAS" IS NOT NULL AND s."IN_LABORATORIO_CIENCIAS" NOT IN (0, 1))
            OR (s."IN_LABORATORIO_INFORMATICA" IS NOT NULL AND s."IN_LABORATORIO_INFORMATICA" NOT IN (0, 1))
            OR (s."IN_SALA_MULTIUSO" IS NOT NULL AND s."IN_SALA_MULTIUSO" NOT IN (0, 1))
            OR (s."IN_SALA_ATENDIMENTO_ESPECIAL" IS NOT NULL AND s."IN_SALA_ATENDIMENTO_ESPECIAL" NOT IN (0, 1))
            OR (s."IN_COZINHA" IS NOT NULL AND s."IN_COZINHA" NOT IN (0, 1))
            OR (s."IN_REFEITORIO" IS NOT NULL AND s."IN_REFEITORIO" NOT IN (0, 1))
            OR (s."IN_QUADRA_ESPORTES" IS NOT NULL AND s."IN_QUADRA_ESPORTES" NOT IN (0, 1))
            OR (s."IN_PATIO_COBERTO" IS NOT NULL AND s."IN_PATIO_COBERTO" NOT IN (0, 1))
            OR (s."IN_AUDITORIO" IS NOT NULL AND s."IN_AUDITORIO" NOT IN (0, 1))
        ) AS has_invalid_value,
        (
            s."IN_AGUA_POTAVEL" IN (0, 1)
            AND s."IN_ENERGIA_REDE_PUBLICA" IN (0, 1)
            AND s."IN_ESGOTO_REDE_PUBLICA" IN (0, 1)
            AND s."IN_LIXO_SERVICO_COLETA" IN (0, 1)
            AND s."IN_BANHEIRO" IN (0, 1)
            AND s."IN_BANHEIRO_PNE" IN (0, 1)
            AND s."IN_BIBLIOTECA" IN (0, 1)
            AND s."IN_SALA_LEITURA" IN (0, 1)
            AND s."IN_LABORATORIO_CIENCIAS" IN (0, 1)
            AND s."IN_LABORATORIO_INFORMATICA" IN (0, 1)
            AND s."IN_SALA_MULTIUSO" IN (0, 1)
            AND s."IN_SALA_ATENDIMENTO_ESPECIAL" IN (0, 1)
            AND s."IN_COZINHA" IN (0, 1)
            AND s."IN_REFEITORIO" IN (0, 1)
            AND s."IN_QUADRA_ESPORTES" IN (0, 1)
            AND s."IN_PATIO_COBERTO" IN (0, 1)
            AND s."IN_AUDITORIO" IN (0, 1)
        ) AS is_complete
    FROM silver.infraestrutura_comum AS s
    WHERE s."NU_ANO_CENSO" IN (2022, 2023, 2024, 2025)
),
key_stats AS (
    SELECT
        year,
        school_id,
        count(*) AS source_rows_for_key,
        bool_and(is_complete) AS all_rows_complete,
        bool_or(has_invalid_value) AS key_has_invalid_value
    FROM source_rows
    WHERE school_id IS NOT NULL
    GROUP BY year, school_id
),
reference_keys AS (
    SELECT DISTINCT
        p.year,
        p.reference_municipality_code,
        r.school_id
    FROM params AS p
    JOIN source_rows AS r
      ON r.year = p.year
     AND r.municipality_code = p.reference_municipality_code
    WHERE p.reference_municipality_code IS NOT NULL
      AND r.school_id IS NOT NULL
),
scoped_rows AS (
    SELECT
        p.year AS requested_year,
        p.reference_municipality_code,
        p.selected_school_id,
        p.null_sample_municipality_code,
        p.null_sample_school_id,
        r.*
    FROM params AS p
    JOIN source_rows AS r
      ON r.year = p.year
    WHERE
        (
            p.reference_municipality_code IS NOT NULL
            AND r.municipality_code = p.reference_municipality_code
        )
        OR EXISTS (
            SELECT 1
            FROM reference_keys AS rk
            WHERE rk.year = r.year
              AND rk.reference_municipality_code = p.reference_municipality_code
              AND rk.school_id = r.school_id
              AND r.municipality_code IS DISTINCT FROM p.reference_municipality_code
        )
        OR (
            p.null_sample_municipality_code IS NOT NULL
            AND p.null_sample_school_id IS NOT NULL
            AND r.municipality_code = p.null_sample_municipality_code
            AND r.school_id = p.null_sample_school_id
        )
),
flagged_rows AS (
    SELECT
        s.*,
        k.source_rows_for_key,
        k.all_rows_complete,
        k.key_has_invalid_value,
        (s.municipality_code = s.reference_municipality_code) AS row_in_reference_municipality,
        (
            s.municipality_code = s.reference_municipality_code
            AND s.selected_school_id IS NOT NULL
            AND s.school_id = s.selected_school_id
        ) AS is_selected_school,
        (
            s.municipality_code = s.null_sample_municipality_code
            AND s.null_sample_school_id IS NOT NULL
            AND s.school_id = s.null_sample_school_id
        ) AS is_null_sample,
        (
            s.municipality_code = s.reference_municipality_code
            AND s.school_id IS NOT NULL
            AND s.selected_school_id IS NOT NULL
            AND s.school_id <> s.selected_school_id
        ) AS potential_comparator_key,
        (
            s.municipality_code = s.reference_municipality_code
            AND s.school_id IS NOT NULL
            AND s.selected_school_id IS NOT NULL
            AND s.school_id <> s.selected_school_id
            AND k.source_rows_for_key = 1
            AND k.all_rows_complete IS TRUE
            AND NOT k.key_has_invalid_value
        ) AS key_in_reference_population,
        (
            s.municipality_code IS DISTINCT FROM s.reference_municipality_code
            AND EXISTS (
                SELECT 1
                FROM reference_keys AS rk
                WHERE rk.year = s.year
                  AND rk.reference_municipality_code = s.reference_municipality_code
                  AND rk.school_id = s.school_id
            )
        ) AS integrity_counterpart_only
    FROM scoped_rows AS s
    LEFT JOIN key_stats AS k
      ON k.year = s.year
     AND k.school_id = s.school_id
),
reference_rollup AS (
    SELECT
        p.year,
        count(DISTINCT f.school_id) FILTER (
            WHERE f.potential_comparator_key
        ) AS potential_comparator_keys,
        count(DISTINCT f.school_id) FILTER (
            WHERE f.key_in_reference_population
        ) AS complete_unique_comparator_keys,
        count(DISTINCT f.school_id) FILTER (
            WHERE f.potential_comparator_key
              AND f.source_rows_for_key > 1
        ) AS duplicate_comparator_keys,
        count(DISTINCT f.school_id) FILTER (
            WHERE f.potential_comparator_key
              AND f.key_has_invalid_value
        ) AS invalid_comparator_keys,
        count(*) FILTER (
            WHERE f.potential_comparator_key
              AND f.has_invalid_value
        ) AS invalid_comparator_source_rows,
        count(*) FILTER (
            WHERE f.row_in_reference_municipality
              AND f.school_id IS NULL
        ) AS reference_rows_without_identifier
    FROM params AS p
    LEFT JOIN flagged_rows AS f
      ON f.requested_year = p.year
     AND f.row_in_reference_municipality
    GROUP BY p.year
),
with_status AS (
    SELECT
        f.*,
        rr.potential_comparator_keys,
        rr.complete_unique_comparator_keys,
        rr.duplicate_comparator_keys,
        rr.invalid_comparator_keys,
        rr.invalid_comparator_source_rows,
        rr.reference_rows_without_identifier,
        (
            rr.duplicate_comparator_keys > 0
            OR rr.invalid_comparator_keys > 0
            OR rr.invalid_comparator_source_rows > 0
            OR rr.reference_rows_without_identifier > 0
        ) AS reference_integrity_blocked,
        CASE
            WHEN f.reference_municipality_code IS NULL
              OR f.selected_school_id IS NULL
                THEN NULL
            WHEN rr.duplicate_comparator_keys > 0
              OR rr.invalid_comparator_keys > 0
              OR rr.invalid_comparator_source_rows > 0
              OR rr.reference_rows_without_identifier > 0
                THEN NULL
            ELSE rr.complete_unique_comparator_keys
        END AS effective_N
    FROM flagged_rows AS f
    JOIN reference_rollup AS rr
      ON rr.year = f.requested_year
)
SELECT
    requested_year AS year,
    municipality_code,
    school_id,
    school_name,
    municipality_name,
    row_in_reference_municipality,
    is_selected_school,
    is_null_sample,
    potential_comparator_key,
    key_in_reference_population,
    integrity_counterpart_only,
    source_rows_for_key,
    key_has_invalid_value,
    "IN_AGUA_POTAVEL",
    "IN_ENERGIA_REDE_PUBLICA",
    "IN_ESGOTO_REDE_PUBLICA",
    "IN_LIXO_SERVICO_COLETA",
    "IN_BANHEIRO",
    "IN_BANHEIRO_PNE",
    "IN_BIBLIOTECA",
    "IN_SALA_LEITURA",
    "IN_LABORATORIO_CIENCIAS",
    "IN_LABORATORIO_INFORMATICA",
    "IN_SALA_MULTIUSO",
    "IN_SALA_ATENDIMENTO_ESPECIAL",
    "IN_COZINHA",
    "IN_REFEITORIO",
    "IN_QUADRA_ESPORTES",
    "IN_PATIO_COBERTO",
    "IN_AUDITORIO",
    potential_comparator_keys,
    complete_unique_comparator_keys,
    duplicate_comparator_keys,
    invalid_comparator_keys,
    invalid_comparator_source_rows,
    reference_rows_without_identifier,
    reference_integrity_blocked,
    effective_N
FROM with_status
ORDER BY
    requested_year,
    row_in_reference_municipality DESC,
    municipality_code NULLS LAST,
    school_id NULLS LAST;

```

## Q3

```sql

WITH
school_municipality_counts AS (
    SELECT
        s."CO_ENTIDADE" AS school_id,
        count(DISTINCT s."CO_MUNICIPIO") AS municipality_code_count
    FROM silver.infraestrutura_comum AS s
    WHERE s."NU_ANO_CENSO" IN (2022, 2023, 2024, 2025)
      AND s."CO_ENTIDADE" IS NOT NULL
    GROUP BY s."CO_ENTIDADE"
),
dimension_by_code AS (
    SELECT
        d.co_municipio,
        count(*) AS dimension_rows,
        array_agg(DISTINCT d.no_municipio ORDER BY d.no_municipio) AS dimension_names
    FROM gold.dim_municipio AS d
    GROUP BY d.co_municipio
)
SELECT
    s."NU_ANO_CENSO" AS year,
    s."CO_ENTIDADE" AS school_id,
    s."NO_ENTIDADE" AS school_name,
    s."CO_MUNICIPIO" AS silver_municipality_code,
    s."NO_MUNICIPIO" AS silver_municipality_name,
    d.dimension_rows,
    d.dimension_names
FROM silver.infraestrutura_comum AS s
JOIN school_municipality_counts AS c
  ON c.school_id = s."CO_ENTIDADE"
LEFT JOIN dimension_by_code AS d
  ON d.co_municipio = s."CO_MUNICIPIO"
WHERE s."NU_ANO_CENSO" IN (2022, 2023, 2024, 2025)
  AND (
      c.municipality_code_count > 1
      OR (
          s."CO_MUNICIPIO" = 1501402
          AND lower(btrim(s."NO_MUNICIPIO")) = 'ananindeua'
      )
  )
ORDER BY
    s."CO_ENTIDADE",
    s."NU_ANO_CENSO",
    s."CO_MUNICIPIO";

```

## Q4

```sql

WITH
dimension_by_code AS (
    SELECT
        d.co_municipio,
        count(*) AS dimension_rows,
        array_agg(DISTINCT d.no_municipio ORDER BY d.no_municipio) AS dimension_names
    FROM gold.dim_municipio AS d
    GROUP BY d.co_municipio
)
SELECT
    s."NU_ANO_CENSO" AS year,
    s."CO_MUNICIPIO" AS municipality_code,
    s."NO_MUNICIPIO" AS silver_municipality_name,
    count(*) AS source_rows,
    count(DISTINCT s."CO_ENTIDADE") AS identified_schools,
    min(s."CO_ENTIDADE") AS minimum_school_id,
    d.dimension_rows,
    d.dimension_names
FROM silver.infraestrutura_comum AS s
LEFT JOIN dimension_by_code AS d
  ON d.co_municipio = s."CO_MUNICIPIO"
WHERE s."NU_ANO_CENSO" IN (2022, 2023, 2024, 2025)
  AND s."CO_MUNICIPIO" = 1504000
GROUP BY
    s."NU_ANO_CENSO",
    s."CO_MUNICIPIO",
    s."NO_MUNICIPIO",
    d.dimension_rows,
    d.dimension_names
ORDER BY
    s."NU_ANO_CENSO",
    s."NO_MUNICIPIO";

```

## Execução e rastreabilidade

Consulte `LEIA-ME.md` para parâmetros, preflight, limites e origem.
