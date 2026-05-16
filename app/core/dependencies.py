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
from app.services.acessibilidade_service import AcessibilidadeService


async_engine = create_async_engine(
    settings.warehouse_dsn,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
    future=True,
)

SessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_warehouse_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


def get_acessibilidade_repository(
    session: AsyncSession = Depends(get_warehouse_session),
) -> AcessibilidadeRepository:
    return AcessibilidadeRepository(session)


def get_acessibilidade_service(
    repository: AcessibilidadeRepository = Depends(get_acessibilidade_repository),
) -> AcessibilidadeService:
    return AcessibilidadeService(repository)


__all__ = [
    "get_current_user",
    "get_warehouse_session",
    "get_acessibilidade_repository",
    "get_acessibilidade_service",
    "async_engine",
    "SessionLocal",
]
