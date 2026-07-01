from sqlalchemy import Column, DateTime, Integer, Numeric, String, Table

# Reaproveita o mesmo gold_metadata e as dimensões/IDEB/PIBID já modeladas em
# acessibilidade — são compartilhadas entre os painéis (mesma fonte gold). Aqui
# só definimos as duas tabelas-fato específicas de conectividade.
from app.models.acessibilidade import (
    dim_entidade,
    dim_municipio,
    dim_tp_dependencia,
    dim_tp_localizacao,
    fato_ideb_anos_finais_esc,
    fato_ideb_anos_iniciais_esc,
    fato_ideb_ensino_medio_esc,
    fato_pibid,
    gold_metadata,
)

# Reexporta os nomes compartilhados para que o repositório de conectividade os
# importe a partir deste módulo (mesma ergonomia do acessibilidade_repository).
__all__ = [
    "fato_conectividade",
    "fato_score_conectividade",
    "dim_entidade",
    "dim_municipio",
    "dim_tp_dependencia",
    "dim_tp_localizacao",
    "fato_ideb_anos_iniciais_esc",
    "fato_ideb_anos_finais_esc",
    "fato_ideb_ensino_medio_esc",
    "fato_pibid",
]


# ============================================================================
# GOLD — usado por todos os painéis de conectividade (tab_percent, dependência,
# localização, total de escolas, evolução temporal e métricas por escola).
# ============================================================================

# fato_conectividade do gold expõe as 17 métricas do notebook (cell-12). Colunas
# de quantidade/tipo (qt_*, tp_rede_local) são tratadas como binário (> 0) no
# repositório.
fato_conectividade = Table(
    "fato_conectividade",
    gold_metadata,
    Column("nu_ano_censo", Integer),
    Column("co_entidade", Integer),
    Column("pibid", Integer),
    Column("in_internet", Integer),
    Column("in_internet_alunos", Integer),
    Column("in_internet_administrativo", Integer),
    Column("in_internet_aprendizagem", Integer),
    Column("in_internet_comunidade", Integer),
    Column("in_banda_larga", Integer),
    Column("in_acesso_internet_computador", Integer),
    Column("in_aces_internet_disp_pessoais", Integer),
    Column("tp_rede_local", Integer),
    Column("in_computador", Integer),
    Column("in_desktop_aluno", Integer),
    Column("qt_desktop_aluno", Integer),
    Column("in_comp_portatil_aluno", Integer),
    Column("qt_comp_portatil_aluno", Integer),
    Column("in_tablet_aluno", Integer),
    Column("qt_tablet_aluno", Integer),
    Column("in_redes_sociais", Integer),
)


# fato_score_conectividade do gold: uma linha por escola por ano censo com as 17
# métricas + score (0–17) e classificação já pré-computados pelo pipeline de
# dados. Lê direto, sem joins — é a base que o mapa do frontend consome. As
# métricas vêm como Numeric (com NULL no banco), por isso são modeladas assim.
fato_score_conectividade = Table(
    "fato_score_conectividade",
    gold_metadata,
    Column("co_entidade", Integer),
    Column("nu_ano_censo", Integer),
    Column("pibid", Integer),
    Column("in_internet", Numeric),
    Column("in_internet_alunos", Numeric),
    Column("in_internet_administrativo", Numeric),
    Column("in_internet_aprendizagem", Numeric),
    Column("in_internet_comunidade", Numeric),
    Column("in_banda_larga", Numeric),
    Column("in_acesso_internet_computador", Numeric),
    Column("in_aces_internet_disp_pessoais", Numeric),
    Column("tp_rede_local", Numeric),
    Column("in_computador", Numeric),
    Column("in_desktop_aluno", Numeric),
    Column("qt_desktop_aluno", Numeric),
    Column("in_comp_portatil_aluno", Numeric),
    Column("qt_comp_portatil_aluno", Numeric),
    Column("in_tablet_aluno", Numeric),
    Column("qt_tablet_aluno", Numeric),
    Column("in_redes_sociais", Numeric),
    Column("score_conectividade", Integer),
    Column("classificacao_conectividade", String),
    Column("ideb_2023_anos_iniciais", Numeric),
    Column("ideb_2023_anos_finais", Numeric),
    Column("ideb_2023_ensino_medio", Numeric),
    Column("ideb_2023_anos_iniciais_mun", Numeric),
    Column("ideb_2023_anos_finais_mun", Numeric),
    Column("ideb_2023_ensino_medio_mun", Numeric),
    Column("dt_carga", DateTime(timezone=True)),
)
