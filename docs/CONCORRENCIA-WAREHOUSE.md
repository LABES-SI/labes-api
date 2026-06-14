# Concorrência e orçamento de conexões do warehouse

> **Para que serve este documento**
> Ele registra *por que* o acesso ao warehouse usa "sessão por query" + um
> semáforo global, e serve como **plano de implementação** quando um novo painel
> (do mesmo tipo do de acessibilidade) for criado. A última seção é um checklist
> acionável: é ela que você devolve para a IA implementar.

---

## Sumário

1. [TL;DR — o padrão em 3 regras](#tldr--o-padrão-em-3-regras)
2. [O problema](#o-problema)
3. [A solução (estado atual)](#a-solução-estado-atual)
4. [O orçamento de conexões](#o-orçamento-de-conexões)
5. [Plano: como adicionar um novo painel](#plano-como-adicionar-um-novo-painel)
6. [Invariantes e footguns](#invariantes-e-footguns)
7. [Como verificar](#como-verificar)
8. [Arquivos tocados](#arquivos-tocados)

---

## TL;DR — o padrão em 3 regras

1. **Sessão por query.** Cada query abre a sua própria `AsyncSession`. Nunca
   compartilhe uma sessão entre operações concorrentes (`asyncio.gather`).
2. **Um semáforo global.** Há **um** `asyncio.Semaphore` compartilhado por toda
   a API que limita o total de queries de warehouse em voo. Ele segura o burst
   *antes* de pedir conexão, então excesso vira latência, não `TimeoutError`.
3. **Um pool, um semáforo — para todos os painéis.** Painéis novos **reusam** o
   mesmo `async_engine` e o mesmo semáforo. Nunca crie pool/semáforo por painel.

---

## O problema

### 1. O bug original — sessão compartilhada em código concorrente

O `build_painel` dispara ~7 queries em paralelo com `asyncio.gather`, mas todas
compartilhavam **uma única** `AsyncSession` (a injetada pela dependência). Uma
`AsyncSession` gerencia **uma só conexão/transação** e **não é segura para uso
concorrente**. Resultado:

```
sqlalchemy.exc.InvalidRequestError: This session is provisioning a new
connection; concurrent operations are not permitted
```

O `gather` ali não dava paralelismo de banco real — só criava corrida na mesma
sessão. Para paralelizar de verdade é preciso **uma conexão por branch**, ou
seja, uma sessão por query.

### 2. O problema de escala — vários painéis

Com "sessão por query", cada `build_painel` faz um **burst de N conexões**
(uma por query do `gather`). A demanda de conexões é:

```
conexões_no_pico = queries_por_painel × painéis_na_tela × usuários_concorrentes
```

Com `queries_por_painel ≈ 7`:

| Cenário | Conexões pedidas no pico |
|---------|--------------------------|
| 1 painel aberto | 7 |
| 1 dashboard com 3 painéis | 21 |
| 3 usuários × dashboard de 3 painéis | 63 |

Aumentar o pool **não escala**: o teto absoluto é o `max_connections` do
Postgres dividido pelo número de réplicas da API. Por isso a solução não é só
"pool maior" — é **limitar o fan-out** com um semáforo, desacoplado do pool.

---

## A solução (estado atual)

### Sessão por query

`AcessibilidadeRepository` recebe o **sessionmaker** (`SessionLocal`), não uma
sessão. Cada query abre a sua própria sessão via os helpers `_execute` /
`_scalar`:

```python
async def _execute(self, stmt):
    async with self._limit():                 # semáforo global (abaixo)
        async with self._sessionmaker() as session:
            return await session.execute(stmt)
```

> **Por que dá para consumir o resultado depois de fechar a sessão:** as queries
> usam SQLAlchemy Core (`select()` com labels) e retornam `Row`/mappings, não
> entidades ORM. O driver async já bufferiza tudo no `execute`, então não há
> `expire_on_commit` em jogo nem I/O lazy após o fechamento.

### Semáforo global

Um único `asyncio.Semaphore` (singleton de módulo, vive no event loop do
uvicorn) é compartilhado por todos os requests e injetado no repositório. O
`_limit()` o adquire **antes** de abrir a sessão, então o teto vale para o
número de conexões fisicamente em uso:

```python
@asynccontextmanager
async def _limit(self):
    if self._semaphore is None:      # None = sem limite (render scripts)
        yield
    else:
        async with self._semaphore:
            yield
```

- **Produção** (via `get_acessibilidade_repository`): recebe o semáforo
  compartilhado → fan-out limitado.
- **Render scripts** (`tests/visual/*`): passam `None` → sem limite (rodam
  isolados, não disputam o pool).

### Config

Tudo tunável por env, documentado em `app/core/config.py`:

| Env | Default | Papel |
|-----|---------|-------|
| `WAREHOUSE_POOL_SIZE` | 10 | conexões base do pool |
| `WAREHOUSE_MAX_OVERFLOW` | 10 | conexões extras sob pressão |
| `WAREHOUSE_MAX_CONCURRENT_QUERIES` | 16 | teto lógico de queries em voo (semáforo) |

---

## O orçamento de conexões

```
                 ┌─────────────────────────────────────────┐
   requests ───► │  Semáforo global (teto LÓGICO)           │  default: 16
                 │  WAREHOUSE_MAX_CONCURRENT_QUERIES         │
                 └──────────────────┬──────────────────────┘
                                    │ só passa quem tem vaga
                                    ▼
                 ┌─────────────────────────────────────────┐
                 │  Pool de conexões (teto FÍSICO)          │  default: 20
                 │  pool_size + max_overflow = 10 + 10      │
                 └──────────────────┬──────────────────────┘
                                    ▼
                              Postgres warehouse
                       (max_connections ÷ nº de réplicas)
```

**Invariante:** `WAREHOUSE_MAX_CONCURRENT_QUERIES ≤ pool_size + max_overflow`,
com folga (~20%) para health-checks, `pool_pre_ping` e endpoints que não são
painel. Com os defaults: semáforo 16 ≤ pool 20, sobra 4.

**Como o estouro deixa de acontecer:** um dashboard de 3 painéis pede 21 queries.
O semáforo deixa 16 correrem; as 5 restantes esperam alguns milissegundos no
semáforo e entram em seguida. Degradação vira **latência**, não erro de pool.

---

## Plano: como adicionar um novo painel

Checklist para criar `FooRepository` / `FooService` seguindo o mesmo padrão.

### Passo 0 — (recomendado) extrair uma base compartilhada

Hoje `_limit` / `_execute` / `_scalar` vivem dentro de
`AcessibilidadeRepository`. Antes do **segundo** painel, mover esses três para
uma base reaproveitável, ex. `app/repositories/base.py`:

```python
class WarehouseRepository:
    def __init__(self, sessionmaker, semaphore=None):
        self._sessionmaker = sessionmaker
        self._semaphore = semaphore

    @asynccontextmanager
    async def _limit(self): ...      # move daqui
    async def _execute(self, stmt): ...
    async def _scalar(self, stmt): ...
```

E `AcessibilidadeRepository(WarehouseRepository)` herda. Assim cada painel novo
ganha sessão-por-query + semáforo de graça, sem duplicar.

### Passo 1 — repository do novo painel

- Herdar de `WarehouseRepository` (ou replicar o construtor `sessionmaker +
  semaphore` se a base ainda não existir).
- **Toda** query usa `self._execute(stmt)` / `self._scalar(stmt)`. Nunca
  guardar uma sessão única em `self`; nunca chamar `session.execute` direto fora
  dos helpers.
- Queries que rodam várias vezes em loop (ex. buckets por ano) também devem usar
  `self._execute` por chamada — cada uma passa pelo semáforo.

### Passo 2 — wiring no `app/core/dependencies.py`

- Adicionar `get_foo_repository()` que injeta **o mesmo** `SessionLocal` e **o
  mesmo** `warehouse_query_semaphore`:

  ```python
  def get_foo_repository() -> FooRepository:
      return FooRepository(SessionLocal, semaphore=warehouse_query_semaphore)
  ```

- **Não** criar `create_async_engine` novo. **Não** criar `asyncio.Semaphore`
  novo. Reusar os existentes.

### Passo 3 — reavaliar o orçamento

- Estimar `queries_por_painel` do painel novo e quantos painéis aparecem juntos
  na mesma tela.
- Se o pico realista de `painéis_na_tela × queries_por_painel` crescer, **só**
  ajustar as envs (`WAREHOUSE_MAX_CONCURRENT_QUERIES` e, se preciso, o pool),
  respeitando a invariante e o `max_connections` do Postgres.
- Conferir: `(pool_size + max_overflow) × réplicas ≤ max_connections` do banco.

### Passo 4 — (opcional) cap por-request

Só se precisar de **justiça** entre requests grandes (impedir que um único
`build_painel` gigante monopolize o semáforo). Adicionar um
`asyncio.Semaphore` *local ao request* no service e envolvê-lo no `gather`. O
semáforo global já resolve o estouro de pool; o cap por-request é refinamento.

### Passo 5 — verificar

Rodar os checks da seção [Como verificar](#como-verificar) e, se houver acesso
ao warehouse, um render script que exercite o `gather` do painel novo.

---

## Invariantes e footguns

- ✅ **Reusar** engine, pool e semáforo entre painéis.
- ❌ **Nunca** criar pool ou semáforo por painel — o orçamento global se perde e
  `N painéis × pool_size` pode estourar o `max_connections` do Postgres.
- ✅ Manter `WAREHOUSE_MAX_CONCURRENT_QUERIES ≤ pool_size + max_overflow`, com
  folga.
- ❌ **Nunca** guardar uma `AsyncSession` única no repositório e usá-la em
  código concorrente — é o bug original.
- ✅ O semáforo precisa envolver a **abertura da sessão** (`_limit` por fora do
  `sessionmaker()`), senão ele limita a coisa errada.
- ⚠️ O semáforo é um singleton de módulo: vive no event loop do uvicorn. Em
  testes que chamam `asyncio.run` várias vezes, use `semaphore=None`.

---

## Como verificar

```bash
# 1. Compila
.venv/bin/python -m py_compile \
  app/core/config.py app/core/dependencies.py \
  app/repositories/acessibilidade_repository.py

# 2. DI conecta pool + semáforo (não precisa de banco)
.venv/bin/python -c "
from app.core import dependencies as d
print('pool_size =', d.async_engine.pool.size())
print('semaphore =', d.warehouse_query_semaphore._value)
repo = d.get_acessibilidade_repository()
print('semaphore injetado:', repo._semaphore is d.warehouse_query_semaphore)
"
```

Teste de comportamento do semáforo (sessionmaker falso, sem banco): rodar várias
`_execute` concorrentes com `Semaphore(k)` e confirmar que o pico de
concorrência nunca passa de `k`. Com `semaphore=None`, o pico é igual ao número
de chamadas (sem limite).

---

## Arquivos tocados

| Arquivo | Papel |
|---------|-------|
| `app/core/config.py` | settings do orçamento (`WAREHOUSE_POOL_SIZE`, `WAREHOUSE_MAX_OVERFLOW`, `WAREHOUSE_MAX_CONCURRENT_QUERIES`) + invariante documentada |
| `app/core/dependencies.py` | engine/pool a partir da config; `warehouse_query_semaphore` (singleton); injeção no repositório |
| `app/repositories/acessibilidade_repository.py` | construtor `sessionmaker + semaphore`; `_limit` / `_execute` / `_scalar`; todas as queries via helpers |
| `tests/visual/*.py` | render scripts passam `SessionLocal` (e `semaphore=None`) |
