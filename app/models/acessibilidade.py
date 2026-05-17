from sqlalchemy import Column, Integer, MetaData, String, Table

metadata = MetaData(schema="silver")

acessibilidade = Table(
    "acessibilidade",
    metadata,
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

fato_acessibilidade = Table(
    "fato_acessibilidade",
    metadata,
    Column("nu_ano_censo", Integer),
    Column("co_entidade", Integer),
    Column("in_acessibilidade_rampas", Integer),
    Column("in_acessibilidade_corrimao", Integer),
    Column("in_acessibilidade_elevador", Integer),
    Column("in_acessibilidade_pisos_tateis", Integer),
    Column("in_acessibilidade_vao_livre", Integer),
    Column("in_banheiro_pne", Integer),
)

dim_entidade = Table(
    "dim_entidade",
    metadata,
    Column("co_entidade", Integer),
    Column("tp_localizacao", Integer),
)

dim_tp_localizacao = Table(
    "dim_tp_localizacao",
    metadata,
    Column("co_tp_localizacao", Integer),
    Column("no_tp_localizacao", String),
)
