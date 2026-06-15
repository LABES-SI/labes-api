from sqlalchemy import Column, Integer, MetaData, Numeric, String, Table

# Dois schemas: os painéis leem de `gold` (fonte de verdade do notebook), enquanto
# o mapa permanece em `silver` porque seu score/classificação depende de colunas que
# só existem no silver (in_banheiro_pne, in_acessibilidade_sinalizacao, in_prof_*).
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


# ============================================================================
# SILVER — usado apenas pelo mapa (score/classificação dependem de colunas que
# não existem no gold). Sufixo `_silver` para deixar a fronteira explícita.
# ============================================================================

fato_acessibilidade_silver = Table(
    "fato_acessibilidade",
    silver_metadata,
    Column("nu_ano_censo", Integer),
    Column("co_entidade", Integer),
    Column("in_banheiro_pne", Integer),
    Column("in_sala_atendimento_especial", Integer),
    Column("in_acessibilidade_rampas", Integer),
    Column("in_acessibilidade_corrimao", Integer),
    Column("in_acessibilidade_elevador", Integer),
    Column("in_acessibilidade_pisos_tateis", Integer),
    Column("in_acessibilidade_vao_livre", Integer),
    Column("in_acessibilidade_inexistente", Integer),
    Column("in_acessibilidade_sinal_tatil", Integer),
    Column("in_acessibilidade_sinal_sonoro", Integer),
    Column("in_acessibilidade_sinal_visual", Integer),
    Column("in_acessibilidade_sinalizacao", Integer),
    Column("in_prof_psicologo", Integer),
    Column("in_prof_trad_libras", Integer),
    Column("in_prof_revisor_braille", Integer),
    Column("in_prof_assist_social", Integer),
    Column("in_prof_fonaudiologo", Integer),
    keep_existing=True,
)


dim_entidade_silver = Table(
    "dim_entidade",
    silver_metadata,
    Column("co_entidade", Integer),
    Column("no_entidade", String),
    Column("no_bairro", String),
    Column("latitude", Numeric),
    Column("longitude", Numeric),
    Column("co_municipio", Integer),
    Column("tp_dependencia", Integer),
    Column("tp_localizacao", Integer),
    keep_existing=True,
)


dim_municipio_silver = Table(
    "dim_municipio",
    silver_metadata,
    Column("co_municipio", Integer),
    Column("no_municipio", String),
    keep_existing=True,
)


dim_tp_dependencia_silver = Table(
    "dim_tp_dependencia",
    silver_metadata,
    Column("co_tp_dependencia", Integer),
    Column("no_tp_dependencia", String),
    keep_existing=True,
)


dim_tp_localizacao_silver = Table(
    "dim_tp_localizacao",
    silver_metadata,
    Column("co_tp_localizacao", Integer),
    Column("no_tp_localizacao", String),
    keep_existing=True,
)
