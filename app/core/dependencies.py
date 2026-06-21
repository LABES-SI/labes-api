import asyncio
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.auth import get_current_user
from app.core.config import settings
from app.repositories.acessibilidade_repository import AcessibilidadeRepository
from app.repositories.conectividade_repository import ConectividadeRepository
from app.services.acessibilidade_service import AcessibilidadeService
from app.services.conectividade_service import ConectividadeService
from app.services.filtros_service import FiltrosService


async_engine = create_async_engine(
    settings.warehouse_dsn,
    pool_pre_ping=True,
    pool_size=settings.warehouse_pool_size,
    max_overflow=settings.warehouse_max_overflow,
    future=True,
)

SessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Semáforo global (singleton de módulo, vive no event loop do uvicorn) que
# limita o total de queries de warehouse em voo entre TODOS os requests/painéis.
# Segura o burst do asyncio.gather antes de pedir conexão, então excesso vira
# latência em vez de TimeoutError de pool. Ver docs/CONCORRENCIA-WAREHOUSE.md.
warehouse_query_semaphore = asyncio.Semaphore(
    settings.warehouse_max_concurrent_queries
)


async def get_warehouse_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


def get_acessibilidade_repository() -> AcessibilidadeRepository:
    # Injeta o sessionmaker (sessão-por-query) + o semáforo compartilhado, nunca
    # uma sessão única — sessão única em código concorrente é o bug original.
    return AcessibilidadeRepository(
        SessionLocal, semaphore=warehouse_query_semaphore
    )


def get_acessibilidade_service(
    repository: AcessibilidadeRepository = Depends(get_acessibilidade_repository),
) -> AcessibilidadeService:
    return AcessibilidadeService(repository)


def get_conectividade_repository() -> ConectividadeRepository:
    # Mesmo padrão de acessibilidade: sessionmaker (sessão-por-query) + o
    # semáforo compartilhado de warehouse.
    return ConectividadeRepository(
        SessionLocal, semaphore=warehouse_query_semaphore
    )


def get_conectividade_service(
    repository: ConectividadeRepository = Depends(get_conectividade_repository),
) -> ConectividadeService:
    return ConectividadeService(repository)


def get_filtros_service(
    repository: AcessibilidadeRepository = Depends(get_acessibilidade_repository),
) -> FiltrosService:
    # Reaproveita o mesmo repositório/pool/semáforo — filtros são dimensionais
    # e compartilhados entre painéis.
    return FiltrosService(repository)


__all__ = [
    "get_current_user",
    "get_warehouse_session",
    "get_acessibilidade_repository",
    "get_acessibilidade_service",
    "get_conectividade_repository",
    "get_conectividade_service",
    "get_filtros_service",
    "async_engine",
    "SessionLocal",
    "warehouse_query_semaphore",
]
