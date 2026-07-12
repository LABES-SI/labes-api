import asyncio
from enum import Enum

from app.core.exceptions import NotFoundError
from app.repositories.acessibilidade_repository import AcessibilidadeRepository
from app.services.acessibilidade_service import METRIC_FIELDS
from app.services.conectividade_service import METRIC_FIELDS as CONECTIVIDADE_METRIC_FIELDS
from app.services.infraestrutura_service import METRIC_FIELDS as INFRAESTRUTURA_METRIC_FIELDS

REDES_ENSINO: list[str] = ["Federal", "Estadual", "Municipal", "Privada"]
TIPOS_LOCALIZACAO: list[str] = ["Urbana", "Rural"]

# Registro painel → catálogo de métricas (chave, label). As métricas são
# específicas de cada painel; os demais filtros (municípios/anos/rede/localização)
# são dimensionais e compartilhados. Novos painéis só adicionam sua entrada aqui
# e passam a ser servidos por GET /filtros?painel=<nome> sem editar a rota.
PAINEL_METRICAS: dict[str, list[tuple[str, str]]] = {
    "acessibilidade": METRIC_FIELDS,
    "conectividade": CONECTIVIDADE_METRIC_FIELDS,
    "infraestrutura": INFRAESTRUTURA_METRIC_FIELDS,
}

# Enum derivado do registry para que o parâmetro ?painel vire um dropdown no
# Swagger (e seja validado com 422) em vez de texto livre. Registrar um novo
# painel em PAINEL_METRICAS o adiciona automaticamente às opções disponíveis.
PainelDisponivel = Enum(
    "PainelDisponivel",
    {nome: nome for nome in PAINEL_METRICAS},
    type=str,
)

FILTROS_DESCRICAO = "filtros_aplicaveis"


class FiltrosService:
    """Serviço genérico de filtros aplicáveis, compartilhável entre painéis.

    Reutiliza o `AcessibilidadeRepository` (mesmo warehouse/pool/semáforo —
    "um pool, um semáforo para todos os painéis", ver docs/CONCORRENCIA-WAREHOUSE.md)
    para as opções dimensionais (municípios/anos) e resolve as métricas por
    painel via `PAINEL_METRICAS`.
    """

    def __init__(self, repository: AcessibilidadeRepository):
        self._repository = repository

    async def build_filtros(self, painel: str | None = None) -> dict:
        """Monta as opções de filtro aplicáveis.

        - Sempre retorna os filtros dimensionais (municípios, anos, rede de
          ensino, tipo de localização).
        - Com `painel` informado, anexa o catálogo de métricas daquele painel.
          Painel desconhecido levanta `NotFoundError` (404).
        """
        municipios, anos = await asyncio.gather(
            self._repository.find_municipios_disponiveis(),
            self._repository.find_anos_disponiveis(),
        )

        data: dict = {
            "municipios": [
                {"codigo": codigo, "nome": nome} for codigo, nome in municipios
            ],
            "anos": anos,
            "rede_ensino": REDES_ENSINO,
            "tp_localizacao": TIPOS_LOCALIZACAO,
        }

        if painel is not None:
            metricas = PAINEL_METRICAS.get(painel)
            if metricas is None:
                raise NotFoundError(
                    f"Painel inválido: {painel!r}. Esperado um de: "
                    f"{sorted(PAINEL_METRICAS)}"
                )
            data["metricas"] = [
                {"chave": chave, "label": label} for chave, label in metricas
            ]

        return {"descricao": FILTROS_DESCRICAO, "data": data}
