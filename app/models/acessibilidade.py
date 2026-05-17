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
