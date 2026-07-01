from sqlalchemy import Column, DateTime, Integer, MetaData, Numeric, String, Table

# Tudo lê de `gold` (fonte de verdade do notebook): painéis de `gold.fato_acessibilidade`
# e o mapa de `gold.fato_score_acessibilidade` (score/classificação pré-computados).
gold_metadata = MetaData(schema="gold")
silver_metadata = MetaData(schema="silver")

# Alias retrocompatível: a tabela legada `acessibilidade` (silver, não importada por
# nenhum módulo) continua referenciando o metadata silver.
metadata = silver_metadata

acessibilidade = Table(
    "acessibilidade",
    silver_metadata,
    Column("NU_ANO_CENSO", Integer),
    Column("CO_MUNICIPIO", Integer),
    Column("NO_MUNICIPIO", String),
    Column("IN_ACESSIBILIDADE_RAMPAS", Integer),
    Column("IN_ACESSIBILIDADE_CORRIMAO", Integer),
    Column("IN_ACESSIBILIDADE_ELEVADOR", Integer),
    Column("IN_ACESSIBILIDADE_PISOS_TATEIS", Integer),
    Column("IN_ACESSIBILIDADE_VAO_LIVRE", Integer),
    Column("IN_BANHEIRO_PNE", Integer),
)


# ============================================================================
# GOLD — usado por todos os painéis (tab_percent, dependência, localização,
# total de escolas, evolução temporal e métricas por escola).
# ============================================================================

# fato_acessibilidade do gold expõe as 15 métricas do notebook (cell-10). Colunas
# de quantidade/tipo (qt_*, tp_aee) são tratadas como binário (> 0) no repositório.
fato_acessibilidade = Table(
    "fato_acessibilidade",
    gold_metadata,
    Column("nu_ano_censo", Integer),
    Column("co_entidade", Integer),
    Column("pibid", Integer),
    Column("in_acessibilidade_rampas", Integer),
    Column("in_acessibilidade_corrimao", Integer),
    Column("in_acessibilidade_elevador", Integer),
    Column("in_acessibilidade_pisos_tateis", Integer),
    Column("in_acessibilidade_vao_livre", Integer),
    Column("qt_salas_utilizadas_acessiveis", Integer),
    Column("in_acessibilidade_inexistente", Integer),
    Column("in_acessibilidade_sinal_tatil", Integer),
    Column("in_acessibilidade_sinal_sonoro", Integer),
    Column("in_acessibilidade_sinal_visual", Integer),
    Column("tp_aee", Integer),
    Column("in_sala_atendimento_especial", Integer),
    Column("in_reserva_pcd", Integer),
    Column("qt_prof_psicologo", Integer),
    Column("qt_prof_assist_social", Integer),
)


# fato_score_acessibilidade do gold: uma linha por escola por ano censo com as 15
# métricas + score (0–15) e classificação já pré-computados pelo pipeline de dados.
# Lê direto, sem joins — é a base que o mapa do frontend consome. As métricas vêm
# como Numeric (com NULL no banco), por isso são modeladas como Numeric.
fato_score_acessibilidade = Table(
    "fato_score_acessibilidade",
    gold_metadata,
    Column("co_entidade", Integer),
    Column("nu_ano_censo", Integer),
    Column("pibid", Integer),
    Column("in_acessibilidade_rampas", Numeric),
    Column("in_acessibilidade_corrimao", Numeric),
    Column("in_acessibilidade_elevador", Numeric),
    Column("in_acessibilidade_pisos_tateis", Numeric),
    Column("in_acessibilidade_vao_livre", Numeric),
    Column("in_acessibilidade_inexistente", Numeric),
    Column("in_acessibilidade_sinal_tatil", Numeric),
    Column("in_acessibilidade_sinal_sonoro", Numeric),
    Column("in_acessibilidade_sinal_visual", Numeric),
    Column("in_sala_atendimento_especial", Numeric),
    Column("in_reserva_pcd", Numeric),
    Column("qt_salas_utilizadas_acessiveis", Numeric),
    Column("tp_aee", Numeric),
    Column("qt_prof_psicologo", Numeric),
    Column("qt_prof_assist_social", Numeric),
    Column("score_acessibilidade", Integer),
    Column("classificacao_acessibilidade", String),
    Column("ideb_2023_anos_iniciais", Numeric),
    Column("ideb_2023_anos_finais", Numeric),
    Column("ideb_2023_ensino_medio", Numeric),
    Column("ideb_2023_anos_iniciais_mun", Numeric),
    Column("ideb_2023_anos_finais_mun", Numeric),
    Column("ideb_2023_ensino_medio_mun", Numeric),
    Column("dt_carga", DateTime(timezone=True)),
)


dim_entidade = Table(
    "dim_entidade",
    gold_metadata,
    Column("co_entidade", Integer),
    Column("no_entidade", String),
    Column("co_municipio", Integer),
    Column("tp_dependencia", Integer),
    Column("tp_localizacao", Integer),
)


dim_municipio = Table(
    "dim_municipio",
    gold_metadata,
    Column("co_municipio", Integer),
    Column("no_municipio", String),
)


dim_tp_dependencia = Table(
    "dim_tp_dependencia",
    gold_metadata,
    Column("co_tp_dependencia", Integer),
    Column("no_tp_dependencia", String),
)


dim_tp_localizacao = Table(
    "dim_tp_localizacao",
    gold_metadata,
    Column("co_tp_localizacao", Integer),
    Column("no_tp_localizacao", String),
)


# IDEB no gold: uma coluna por ano (ideb_2005..ideb_2023), co_entidade minúsculo.
def _ideb_table(name: str) -> Table:
    return Table(
        name,
        gold_metadata,
        Column("co_entidade", Integer),
        Column("ideb_2005", Numeric),
        Column("ideb_2007", Numeric),
        Column("ideb_2009", Numeric),
        Column("ideb_2011", Numeric),
        Column("ideb_2013", Numeric),
        Column("ideb_2015", Numeric),
        Column("ideb_2017", Numeric),
        Column("ideb_2019", Numeric),
        Column("ideb_2021", Numeric),
        Column("ideb_2023", Numeric),
    )


fato_ideb_anos_iniciais_esc = _ideb_table("fato_ideb_anos_iniciais_esc")
fato_ideb_anos_finais_esc = _ideb_table("fato_ideb_anos_finais_esc")
fato_ideb_ensino_medio_esc = _ideb_table("fato_ideb_ensino_medio_esc")


# PIBID no gold: sem coluna de ano — agregado por escola no repositório.
fato_pibid = Table(
    "fato_pibid",
    gold_metadata,
    Column("co_entidade", Integer),
    Column("subprojeto", String),
    Column("qtd_bolsistas_ativos", Integer),
)
