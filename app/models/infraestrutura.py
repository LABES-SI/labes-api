from sqlalchemy import Column, Integer, String, Table

# Reaproveita o mesmo silver_metadata/gold_metadata e as dimensões/IDEB/PIBID já
# modeladas em acessibilidade — são compartilhadas entre os painéis. Aqui só
# definimos a tabela silver específica de infraestrutura.
from app.models.acessibilidade import (
    dim_tp_dependencia,
    dim_tp_localizacao,
    fato_ideb_anos_finais_esc,
    fato_ideb_anos_iniciais_esc,
    fato_ideb_ensino_medio_esc,
    fato_pibid,
    gold_metadata,
    silver_metadata,
)

# Reexporta os nomes compartilhados para que o repositório de infraestrutura os
# importe a partir deste módulo (mesma ergonomia dos outros painéis).
__all__ = [
    "infraestrutura_comum",
    "dim_tp_dependencia",
    "dim_tp_localizacao",
    "fato_ideb_anos_iniciais_esc",
    "fato_ideb_anos_finais_esc",
    "fato_ideb_ensino_medio_esc",
    "fato_pibid",
]


# ============================================================================
# SILVER — fonte única da infraestrutura (não há fato/score na camada gold).
# As colunas do INEP estão em MAIÚSCULO (case-sensitive): o SQLAlchemy detecta
# o nome misto/maiúsculo e as quota automaticamente no SQL, ex.: "IN_AGUA_POTAVEL".
# Só `pibid` é minúsculo. Modelamos apenas as colunas usadas pelos painéis (não
# as 77 da silver): identificação, dimensões (código) e as 17 métricas do score.
# ============================================================================
infraestrutura_comum = Table(
    "infraestrutura_comum",
    silver_metadata,
    Column("CO_MUNICIPIO", Integer),
    Column("CO_ENTIDADE", Integer),
    Column("NU_ANO_CENSO", Integer),
    Column("NO_ENTIDADE", String),
    Column("NO_MUNICIPIO", String),
    Column("TP_DEPENDENCIA", Integer),
    Column("TP_LOCALIZACAO", Integer),
    Column("pibid", Integer),
    # --- Saneamento e serviços básicos ---
    Column("IN_AGUA_POTAVEL", Integer),
    Column("IN_ENERGIA_REDE_PUBLICA", Integer),
    Column("IN_ESGOTO_REDE_PUBLICA", Integer),
    Column("IN_LIXO_SERVICO_COLETA", Integer),
    Column("IN_BANHEIRO", Integer),
    Column("IN_BANHEIRO_PNE", Integer),
    # --- Espaços pedagógicos ---
    Column("IN_BIBLIOTECA", Integer),
    Column("IN_SALA_LEITURA", Integer),
    Column("IN_LABORATORIO_CIENCIAS", Integer),
    Column("IN_LABORATORIO_INFORMATICA", Integer),
    Column("IN_SALA_MULTIUSO", Integer),
    Column("IN_SALA_ATENDIMENTO_ESPECIAL", Integer),
    # --- Alimentação, esporte e convívio ---
    Column("IN_COZINHA", Integer),
    Column("IN_REFEITORIO", Integer),
    Column("IN_QUADRA_ESPORTES", Integer),
    Column("IN_PATIO_COBERTO", Integer),
    Column("IN_AUDITORIO", Integer),
)
