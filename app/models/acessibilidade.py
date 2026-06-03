from sqlalchemy import Column, Integer, MetaData, Numeric, String, Table

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
)


dim_entidade = Table(
    "dim_entidade",
    metadata,
    Column("co_entidade", Integer),
    Column("no_entidade", String),
    Column("no_bairro", String),
    Column("latitude", Numeric),
    Column("longitude", Numeric),
    Column("co_municipio", Integer),
    Column("tp_dependencia", Integer),
    Column("tp_localizacao", Integer),
)


dim_municipio = Table(
    "dim_municipio",
    metadata,
    Column("co_municipio", Integer),
    Column("no_municipio", String),
)


dim_tp_dependencia = Table(
    "dim_tp_dependencia",
    metadata,
    Column("co_tp_dependencia", Integer),
    Column("no_tp_dependencia", String),
)


dim_tp_localizacao = Table(
    "dim_tp_localizacao",
    metadata,
    Column("co_tp_localizacao", Integer),
    Column("no_tp_localizacao", String),
)


ideb_anos_iniciais_escolas = Table(
    "ideb_anos_iniciais_escolas",
    metadata,
    Column("CO_ENTIDADE", Integer),
    Column("IDEB(2005)", Numeric),
    Column("IDEB(2007)", Numeric),
    Column("IDEB(2009)", Numeric),
    Column("IDEB(2011)", Numeric),
    Column("IDEB(2013)", Numeric),
    Column("IDEB(2015)", Numeric),
    Column("IDEB(2017)", Numeric),
    Column("IDEB(2019)", Numeric),
    Column("IDEB(2021)", Numeric),
    Column("IDEB(2023)", Numeric),
)


ideb_anos_finais_escolas = Table(
    "ideb_anos_finais_escolas",
    metadata,
    Column("CO_ENTIDADE", Integer),
    Column("IDEB(2005)", Numeric),
    Column("IDEB(2007)", Numeric),
    Column("IDEB(2009)", Numeric),
    Column("IDEB(2011)", Numeric),
    Column("IDEB(2013)", Numeric),
    Column("IDEB(2015)", Numeric),
    Column("IDEB(2017)", Numeric),
    Column("IDEB(2019)", Numeric),
    Column("IDEB(2021)", Numeric),
    Column("IDEB(2023)", Numeric),
)
