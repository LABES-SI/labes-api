# Arquitetura do labes-api

Documentação da estrutura do backend do observatório de dados. O objetivo deste documento é deixar claro **onde cada coisa vive**, **por que ela vive ali** e **como as camadas conversam entre si**.

## Sumário

1. [Visão geral](#visão-geral)
2. [Estrutura de pastas](#estrutura-de-pastas)
3. [Responsabilidade de cada camada](#responsabilidade-de-cada-camada)
4. [Fluxo de uma requisição](#fluxo-de-uma-requisição)
5. [Exemplos de código](#exemplos-de-código)
6. [Convenções e regras](#convenções-e-regras)
7. [Testes](#testes)
8. [FAQ arquitetural](#faq-arquitetural)

---

## Visão geral

O `labes-api` é o backend do observatório de dados. Ele **não transforma dados** — quem faz isso é o pipeline do squad de dados, via dbt, que entrega tabelas prontas na camada *gold* do data warehouse.

A responsabilidade do backend é:

- Expor uma API HTTP para o frontend.
- Autenticar e autorizar requisições.
- Consultar as tabelas *gold* e adaptar a resposta ao contexto da requisição (filtros, permissões, paginação, formatação).
- Compor dados, quando necessário, com dados operacionais próprios (usuários, permissões, logs de acesso).

A arquitetura adotada é **MVC + Service Layer + Repository Pattern**, que entrega a maior parte dos benefícios da arquitetura hexagonal sem o overhead de cerimônia desnecessária para um backend majoritariamente *read-only*.

### Princípios

1. **Camadas finas e focadas.** Cada camada tem uma responsabilidade só.
2. **A fronteira com o warehouse fica isolada.** Todo acesso ao warehouse passa pelos *repositories*. Se uma tabela mudar, mexemos em um lugar só.
3. **A lógica de aplicação não conhece SQL.** Services chamam repositories, nunca queries diretas.
4. **Schemas validam entrada e saída.** Nada entra ou sai da API sem passar por um schema Pydantic.

---

## Estrutura de pastas

```
labes-api/
├── app/
│   ├── core/              # Configuração, auth, exceções, dependências comuns
│   ├── routes/            # Endpoints HTTP (FastAPI routers)
│   ├── services/          # Lógica de aplicação (autorização, composição, regras)
│   ├── repositories/      # Acesso ao warehouse (queries, mapeamento gold)
│   ├── schemas/           # Pydantic: request/response
│   ├── domain/            # Entidades de domínio (estruturas internas)
│   ├── models/            # ORM do banco operacional próprio (se houver)
│   ├── middleware/        # Middlewares customizados
│   └── utils/             # Helpers transversais
├── tests/
│   ├── routes/
│   ├── services/
│   └── repositories/
├── main.py                # Ponto de entrada
├── pyproject.toml
├── mise.toml
└── README.md
```

---

## Responsabilidade de cada camada

### `app/core/`

Peças transversais que são consumidas por toda a aplicação.

- **`config.py`** — Carregamento de variáveis de ambiente via Pydantic Settings.
- **`auth.py`** — Validação de token JWT, extração de usuário atual.
- **`exceptions.py`** — Exceções customizadas (`NotFoundError`, `ForbiddenError`, etc.) e tradução para HTTP.
- **`dependencies.py`** — *Dependencies* do FastAPI compartilhadas (ex: `get_current_user`, `get_db`).
- **`logging.py`** — Configuração de logger estruturado.

> Regra: nada de regra de negócio aqui. `core/` é infraestrutura da aplicação.

### `app/routes/`

Endpoints HTTP. Em FastAPI, esta camada absorve o papel de "controller" — receber requisição, validar via schema, delegar para o service e devolver a resposta.

> Regra: routes são finas. Não acessam banco, não têm regra de negócio. No máximo: receber, delegar, formatar resposta.

### `app/services/`

Lógica de aplicação. É aqui que vivem as regras de negócio do backend: quem pode ver o quê, como compor dados de fontes diferentes, validações que dependem de contexto.

> Regra: services não conhecem HTTP (não recebem `Request`, não retornam `Response`) e não conhecem SQL (sempre falam via repositories).

### `app/repositories/`

A fronteira com o warehouse. Cada repository encapsula as queries de uma área do *gold* — geralmente um repository por *mart* ou domínio analítico.

> Regra: toda query SQL contra o warehouse vive aqui. Repositories retornam objetos do `domain/`, nunca `dict` solto ou linhas cruas.

### `app/schemas/`

Modelos Pydantic para validação de entrada e saída da API. Separados em `requests.py` e `responses.py` por domínio.

> Regra: schemas são públicos (refletem o contrato da API). Mudanças aqui são *breaking changes* e precisam ser tratadas com versionamento.

### `app/domain/`

Entidades internas de domínio. São objetos que circulam entre service e repository — independentes de Pydantic e de qualquer detalhe de transporte.

> Regra: `domain` é o coração da aplicação. Não importa nada do FastAPI, nada do SQLAlchemy. Apenas Python puro (`dataclass` ou classes simples).

### `app/models/`

ORM do **banco operacional próprio** — se a aplicação tiver um (usuários, permissões, logs de auditoria, configurações). **Não tem nada a ver com o warehouse.** Os dados do warehouse vivem em `repositories/` + `domain/`.

### `app/middleware/`

Middlewares customizados: tracing, request ID, métricas.

### `app/utils/`

Helpers genuinamente transversais e sem estado: formatação de datas, conversão de unidades. Cuidado: `utils/` tende a virar lixeira. Se algo cresce, promova para uma pasta própria.

---

## Fluxo de uma requisição

O caminho típico de uma requisição:

```
Cliente HTTP
    │
    ▼
┌─────────────┐
│ middleware/ │  (tracing, request ID)
└──────┬──────┘
       ▼
┌─────────────┐
│   routes/   │  (recebe, valida via schema, delega)
└──────┬──────┘
       ▼
┌─────────────┐
│  services/  │  (autorização, regras, composição)
└──────┬──────┘
       ▼
┌──────────────────┐
│  repositories/   │  (SQL contra o warehouse)
└──────┬───────────┘
       ▼
   Data Warehouse (gold tables)
```

Resumo: `route → service → repository → warehouse`. Schemas validam entrada e saída; `core/` fornece as peças transversais (auth, config, dependências).

---

## Exemplos de código

Os exemplos abaixo assumem **FastAPI + Pydantic v2 + SQLAlchemy 2.x** (apenas para emitir SQL contra o warehouse, sem usar como ORM full).

Cenário: endpoint que retorna o faturamento mensal por região, respeitando as regiões que o usuário logado tem permissão de ver.

### 1. Schema (request/response)

`app/schemas/revenue.py`

```python
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field


class RevenueByRegionQuery(BaseModel):
    """Filtros aceitos no endpoint."""
    start_date: date
    end_date: date
    regions: list[str] | None = Field(
        default=None,
        description="Se omitido, retorna todas as regiões permitidas ao usuário.",
    )


class RevenueByRegionItem(BaseModel):
    region: str
    month: date
    total_revenue: Decimal
    transactions: int


class RevenueByRegionResponse(BaseModel):
    items: list[RevenueByRegionItem]
    total: Decimal
```

### 2. Domain (entidade interna)

`app/domain/revenue.py`

```python
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class RevenueRecord:
    """Representa uma linha do mart de faturamento (gold.fct_revenue_monthly)."""
    region: str
    month: date
    total_revenue: Decimal
    transactions: int
```

Note que `RevenueRecord` não herda de `BaseModel`. É Python puro. Isso isola o domínio do framework.

### 3. Repository (fronteira com o warehouse)

`app/repositories/revenue_repository.py`

```python
from datetime import date
from decimal import Decimal
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.revenue import RevenueRecord


class RevenueRepository:
    """
    Acessa as tabelas do mart de faturamento na camada gold do warehouse.

    Mart de referência: gold.fct_revenue_monthly
    Owner do mart: squad de dados
    Documentação: <link para dbt docs>
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_monthly_by_region(
        self,
        start_date: date,
        end_date: date,
        regions: list[str],
    ) -> list[RevenueRecord]:
        if not regions:
            return []

        query = text("""
            SELECT
                region,
                month,
                total_revenue,
                transactions
            FROM gold.fct_revenue_monthly
            WHERE month BETWEEN :start_date AND :end_date
              AND region = ANY(:regions)
            ORDER BY month, region
        """)

        result = await self._session.execute(
            query,
            {
                "start_date": start_date,
                "end_date": end_date,
                "regions": regions,
            },
        )

        return [
            RevenueRecord(
                region=row.region,
                month=row.month,
                total_revenue=Decimal(row.total_revenue),
                transactions=row.transactions,
            )
            for row in result
        ]
```

Pontos importantes:

- O repository devolve `RevenueRecord` (do `domain/`), nunca linhas cruas ou `dict`.
- O nome da tabela e os nomes das colunas vivem **só aqui**. Se o squad de dados renomear `total_revenue` para `revenue_total`, mexemos em um arquivo só.
- A docstring referencia o owner do mart e a documentação. Isso deixa o contrato entre squads explícito no código.

### 4. Service (lógica de aplicação)

`app/services/revenue_service.py`

```python
from datetime import date
from decimal import Decimal

from app.core.exceptions import ForbiddenError
from app.domain.revenue import RevenueRecord
from app.domain.user import User
from app.repositories.revenue_repository import RevenueRepository


class RevenueService:
    def __init__(self, repository: RevenueRepository):
        self._repository = repository

    async def get_monthly_by_region(
        self,
        user: User,
        start_date: date,
        end_date: date,
        requested_regions: list[str] | None,
    ) -> tuple[list[RevenueRecord], Decimal]:
        # 1. Resolve quais regiões o usuário pode ver
        allowed = set(user.allowed_regions)

        if requested_regions:
            invalid = set(requested_regions) - allowed
            if invalid:
                raise ForbiddenError(
                    f"Sem permissão para as regiões: {sorted(invalid)}"
                )
            target_regions = list(set(requested_regions) & allowed)
        else:
            target_regions = list(allowed)

        # 2. Busca os dados (delega para o repository)
        records = await self._repository.find_monthly_by_region(
            start_date=start_date,
            end_date=end_date,
            regions=target_regions,
        )

        # 3. Calcula totais (regra de aplicação, não de dados)
        total = sum((r.total_revenue for r in records), Decimal("0"))

        return records, total
```

Pontos importantes:

- O service não sabe nada de SQL nem de HTTP.
- Autorização vive aqui — porque depende do contexto do usuário, não é algo que o dbt poderia pré-computar.
- O cálculo de `total` é simples e aplicável só ao recorte da requisição, então faz sentido aqui. Se fosse um agregado complexo aplicável globalmente, deveria estar no dbt.

### 5. Route (endpoint HTTP)

`app/routes/revenue.py`

```python
from fastapi import APIRouter, Depends, Query
from datetime import date

from app.core.dependencies import get_current_user, get_revenue_service
from app.domain.user import User
from app.schemas.revenue import (
    RevenueByRegionItem,
    RevenueByRegionResponse,
)
from app.services.revenue_service import RevenueService

router = APIRouter(prefix="/revenue", tags=["revenue"])


@router.get("/monthly-by-region", response_model=RevenueByRegionResponse)
async def get_monthly_revenue_by_region(
    start_date: date = Query(...),
    end_date: date = Query(...),
    regions: list[str] | None = Query(default=None),
    user: User = Depends(get_current_user),
    service: RevenueService = Depends(get_revenue_service),
) -> RevenueByRegionResponse:
    records, total = await service.get_monthly_by_region(
        user=user,
        start_date=start_date,
        end_date=end_date,
        requested_regions=regions,
    )

    return RevenueByRegionResponse(
        items=[
            RevenueByRegionItem(
                region=r.region,
                month=r.month,
                total_revenue=r.total_revenue,
                transactions=r.transactions,
            )
            for r in records
        ],
        total=total,
    )
```

Pontos importantes:

- A route é fina: recebe, delega, monta resposta.
- Sem regra de negócio, sem SQL.
- A conversão `RevenueRecord → RevenueByRegionItem` acontece aqui (na fronteira de saída), mantendo o `domain` desacoplado do schema público.

### 6. Wiring (dependências)

`app/core/dependencies.py`

```python
from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import settings
from app.repositories.revenue_repository import RevenueRepository
from app.services.revenue_service import RevenueService


# Session factory criada uma vez no startup
SessionLocal = async_sessionmaker(...)  # configurada com warehouse URL


async def get_warehouse_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


def get_revenue_repository(
    session: AsyncSession = Depends(get_warehouse_session),
) -> RevenueRepository:
    return RevenueRepository(session)


def get_revenue_service(
    repository: RevenueRepository = Depends(get_revenue_repository),
) -> RevenueService:
    return RevenueService(repository)
```

O wiring centralizado garante que a injeção de dependência seja consistente e fácil de mockar nos testes.

### 7. Exception handler

`app/core/exceptions.py`

```python
from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base de todas as exceções de aplicação."""
    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class ForbiddenError(AppError):
    status_code = 403
    code = "forbidden"


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message},
    )
```

Registrado no `main.py` com `app.add_exception_handler(AppError, app_error_handler)`. Isso permite que services lancem exceções de domínio sem saber nada de HTTP.

---

## Convenções e regras

### Regras invioláveis

1. **Routes não acessam banco.** Sempre via service.
2. **Services não escrevem SQL.** Sempre via repository.
3. **Repositories não conhecem usuário/permissão.** Recebem parâmetros já resolvidos.
4. **Domain não importa Pydantic, FastAPI ou SQLAlchemy.** É Python puro.
5. **Schemas validam tudo que entra e sai da API.**

### Nomenclatura

- Repositories: `XxxRepository` (singular do domínio + sufixo).
- Services: `XxxService`.
- Schemas: `XxxRequest`, `XxxResponse`, `XxxItem`.
- Domain: nome do conceito (`RevenueRecord`, `User`, `Permission`).

### Onde colocar nova lógica?

| Tipo de lógica | Camada |
|---|---|
| Cálculo agregado que vale para todos os usuários | dbt (squad de dados) |
| Filtragem por permissão do usuário logado | service |
| Composição de duas queries do warehouse | service |
| Acesso a uma tabela do warehouse | repository |
| Validação de formato do input | schema |
| Tradução de erro de domínio para HTTP | exception handler |
| Configuração de timezone, locale | core/utils |

### Contrato com o squad de dados

- Toda tabela consumida deve estar documentada (dbt docs).
- O nome do mart e seu owner devem aparecer como docstring no repository correspondente.
- Mudanças quebra-contrato (renomear coluna, mudar tipo) precisam ser anunciadas com antecedência e idealmente cobertas por testes de contrato.

---

## Testes

A estrutura de `tests/` espelha `app/`. A estratégia muda por camada:

### `tests/repositories/`

Testes de integração contra um warehouse de teste (idealmente um schema de staging com dados controlados ou um Postgres local com tabelas mockando o gold).

```python
import pytest
from datetime import date
from app.repositories.revenue_repository import RevenueRepository


@pytest.mark.asyncio
async def test_find_monthly_by_region_returns_records_in_range(
    test_session,
    seed_revenue_data,
):
    repo = RevenueRepository(test_session)

    records = await repo.find_monthly_by_region(
        start_date=date(2025, 1, 1),
        end_date=date(2025, 3, 31),
        regions=["SP", "RJ"],
    )

    assert len(records) == 6  # 3 meses × 2 regiões
    assert all(r.region in {"SP", "RJ"} for r in records)
```

### `tests/services/`

Testes unitários com repository mockado. Aqui se testa toda a regra de aplicação sem precisar de banco.

```python
import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock

from app.core.exceptions import ForbiddenError
from app.domain.user import User
from app.domain.revenue import RevenueRecord
from app.services.revenue_service import RevenueService


@pytest.mark.asyncio
async def test_blocks_user_requesting_unauthorized_region():
    repo = AsyncMock()
    service = RevenueService(repo)

    user = User(id=1, allowed_regions=["SP"])

    with pytest.raises(ForbiddenError):
        await service.get_monthly_by_region(
            user=user,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            requested_regions=["SP", "RJ"],
        )

    repo.find_monthly_by_region.assert_not_called()


@pytest.mark.asyncio
async def test_filters_to_allowed_regions_when_no_filter_provided():
    repo = AsyncMock()
    repo.find_monthly_by_region.return_value = [
        RevenueRecord(
            region="SP",
            month=date(2025, 1, 1),
            total_revenue=Decimal("100"),
            transactions=5,
        )
    ]
    service = RevenueService(repo)

    user = User(id=1, allowed_regions=["SP", "RJ"])

    records, total = await service.get_monthly_by_region(
        user=user,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 31),
        requested_regions=None,
    )

    assert total == Decimal("100")
    repo.find_monthly_by_region.assert_awaited_once()
    call_kwargs = repo.find_monthly_by_region.call_args.kwargs
    assert set(call_kwargs["regions"]) == {"SP", "RJ"}
```

### `tests/routes/`

Testes end-to-end com `TestClient`. Validam serialização, status codes e wiring. Use overrides de dependência para isolar do warehouse real.

```python
from fastapi.testclient import TestClient


def test_returns_403_for_unauthorized_region(client: TestClient, auth_token):
    response = client.get(
        "/revenue/monthly-by-region",
        params={
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
            "regions": ["XX"],
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 403
    assert response.json()["code"] == "forbidden"
```

---

## FAQ arquitetural

**E se eu precisar fazer um JOIN entre duas tabelas do warehouse?**
Se o JOIN é estável e útil para todo mundo, peça ao squad de dados para criar um novo mart no gold com o JOIN já feito. Se é específico do contexto da API, faça no repository — mas considere se a complexidade justifica.

**Posso ter mais de um repository por endpoint?**
Sim. Um service pode orquestrar vários repositories. Isso é comum quando você compõe dado do warehouse com dado operacional (ex: lista de relatórios + permissões do usuário).

**Onde fica cache?**
No repository, normalmente, com um decorator ou wrapper. Mantém a interface pública intacta.

**Vou precisar trocar de warehouse no futuro. Isso me protege?**
Sim, parcialmente. Como toda dependência do warehouse está nos repositories, a troca fica contida ali. O dialeto SQL pode mudar, mas a interface dos repositories para os services não muda.

**Quando promover algo de `utils/` para outra pasta?**
Quando o helper começa a ter dependências (não é mais função pura), ou quando vira um conjunto coeso (mais de 3-4 funções relacionadas). Aí merece pasta própria.

**Devo usar ORM ou SQL puro nos repositories?**
Para queries contra o warehouse (read-heavy, analítico), SQL puro com `text()` costuma ser mais claro e flexível. Para o banco operacional próprio (CRUD), ORM faz sentido.

**Como lido com paginação?**
No service. O repository aceita `limit` e `offset` (ou cursor) como parâmetros. O service decide a estratégia e expõe via schema.

---

## Referências

- Fundamentals of Data Engineering — Joe Reis & Matt Housley
- Designing Data-Intensive Applications — Martin Kleppmann
- FastAPI docs — https://fastapi.tiangolo.com
- dbt docs — https://docs.getdbt.com
