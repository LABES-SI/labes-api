# Convenção de Branches — labes-api

Este documento define o **modelo de branching** e a **convenção de nomes** adotados no repositório. O objetivo é deixar claro de onde cada branch nasce, para onde ela morre, e como nomeá-la.

> **Modelo:** Git Flow clássico, com **release branches dedicadas para validação de QA**.
> **Branch principal de prod:** `main`
> **Branch de integração contínua:** `develop`
> **Branch de validação (staging):** `release/vX.Y.Z`
> **Validação antes de prod:** time de QA testa em `release/*` (deployada em staging); promoção `release/* → main` é manual.

---

## Sumário

1. [Visão geral do fluxo](#visão-geral-do-fluxo)
2. [Branches permanentes](#branches-permanentes)
3. [Branches temporárias](#branches-temporárias)
4. [Fluxo de QA e promoção para produção](#fluxo-de-qa-e-promoção-para-produção)
5. [Convenção de nomes](#convenção-de-nomes)
6. [Tabela de referência rápida](#tabela-de-referência-rápida)
7. [Anti-padrões](#anti-padrões)

---

## Visão geral do fluxo

```
                  ┌───────────────────────────┐
                  │           main            │  ← produção
                  └─────▲─────────────▲───────┘
                        │             │
                  merge │             │ merge (hotfix)
                  (após │             │
                   QA)  │             │
                        │             │
                  ┌─────┴────────┐   ┌┴──────────────┐
                  │ release/v*   │   │  hotfix/*     │
                  │  (staging)   │   └───────────────┘
                  │ ↑ QA testa   │
                  └─────▲────────┘
                        │
                  cut   │  bugfixes
                  from  │  voltam pra
                  develop  develop
                        │
                  ┌─────┴───────────┐
                  │     develop     │  ← integração contínua
                  └──▲────▲────▲────┘
                     │    │    │
              merge  │    │    │  merge
                     │    │    │
              ┌──────┴┐ ┌─┴────┴─┐
              │feature│ │bugfix/*│
              │  /*   │ │        │
              └───────┘ └────────┘
```

- **`feature/*`** e **`bugfix/*`** nascem de `develop` e voltam para `develop`.
- **`develop`** acumula features prontas para validação. **Não é o ambiente de QA** — é uma branch de integração.
- **`release/*`** é cortada de `develop` quando o time decide fechar um pacote para validação. **É a branch que vai para staging** e onde o QA valida.
- Bugs encontrados em QA são corrigidos **diretamente em `release/*`** e propagados de volta para `develop`.
- Quando aprovada, **`release/*` é mergeada em `main` (deploy em prod) e em `develop` (sincronizar correções)**.
- **`hotfix/*`** nasce de `main` e volta para `main` **e** `develop`.

### Por que esse fluxo?

Esse modelo resolve um problema específico: **uma feature reprovada em QA não pode bloquear outras features que estão prontas**.

Se o QA validasse `develop` diretamente, qualquer feature problemática mergeada lá seguraria todas as outras. Com `release/*`, congelamos um conjunto fechado para validar — `develop` continua aceitando novas entradas em paralelo, sem afetar a release em andamento.

O custo desse modelo é mais cerimônia: mais uma branch, mais um merge, e o cuidado de propagar bugfixes de `release/*` para `develop` (senão o bug volta no próximo ciclo).

---

## Branches permanentes

### `main`

- Reflete o que está em **produção**.
- **Protegida**: ninguém faz push direto. Só recebe merge de `release/*` (após QA aprovar) ou de `hotfix/*`.
- Cada commit em `main` corresponde a um deploy em produção.

### `develop`

- Branch de **integração contínua**. É onde features e bugfixes convergem antes de serem agrupados em uma release.
- **Protegida**: só recebe merge via PR aprovada e com CI verde.
- **Não é o ambiente de QA.** O QA valida `release/*`, não `develop`. Isso permite que `develop` continue recebendo novas features em paralelo a uma validação em andamento.
- Pode ser deployada em um ambiente de "dev" (opcional) para os próprios desenvolvedores testarem integrações, mas esse ambiente **não é validado pelo QA**.

---

## Branches temporárias

São criadas para um trabalho específico e **deletadas após o merge**. Sem exceções.

### `feature/*`

Para qualquer trabalho de nova funcionalidade.

- **Origem:** `develop`
- **Destino:** `develop` (via PR)
- **Ciclo de vida:** curto (idealmente menos de 3 dias). Branches longas geram conflitos e divergência.

### `bugfix/*`

Para correção de bug **encontrado antes da produção** — pode ser em `develop` (pré-release) ou em `release/*` (durante validação de QA).

- **Origem e destino:**
  - Bug encontrado em `develop` (pelos próprios devs): `bugfix/* → develop`.
  - Bug encontrado em `release/*` (pelo QA): `bugfix/* → release/*`. Será propagado para `develop` no back-merge final da release.
- **Diferença para `hotfix`:** bugfix corrige problema que **ainda não chegou em produção**. `hotfix` é para bugs já em prod.

### `hotfix/*`

Para correção urgente de bug **em produção**.

- **Origem:** `main`
- **Destino:** `main` **e** `develop` (dois merges, ou cherry-pick para `develop` após merge em `main`).
- **Critério:** só usar quando o bug está em prod e não pode esperar o ciclo normal `feature → develop → main`.
- Após merge em `main`, dispara deploy imediato. Lembre-se de propagar para `develop` para evitar regressão no próximo deploy.

### `release/*`

Para **agrupar e validar um conjunto fechado de mudanças** antes de irem para produção. É a branch que o time de QA testa.

- **Origem:** `develop` (em um ponto onde o time decide "esse conjunto está pronto para validação").
- **Destino:** `main` **e** `develop` (após aprovação do QA).
- **Ciclo de vida:** dura o tempo da validação (idealmente algumas horas a poucos dias).
- **Nome:** `release/vX.Y.Z`, seguindo [SemVer](https://semver.org/lang/pt-BR/).

**Quando criar uma `release/*`:**

- Quando há um conjunto coeso de features prontas em `develop` esperando para ir pra prod.
- Em uma cadência regular (ex: toda terça e quinta de manhã, dependendo do volume de mudanças).
- Quando há urgência em entregar uma feature específica que já está em `develop`.

**Regras importantes:**

1. Uma vez criada, **nenhuma feature nova entra em `release/*`.** Apenas correções de bugs encontrados pelo QA.
2. Bugfixes aplicados em `release/*` precisam ser **propagados de volta para `develop`**, senão o bug ressurge no próximo ciclo. Isso é feito mergeando `release/*` em `develop` no mesmo momento em que mergeia em `main`.
3. **Apenas uma `release/*` ativa por vez.** Não criar `release/v1.5.0` enquanto `release/v1.4.0` ainda está em validação.

---

## Fluxo de QA e promoção para produção

Esta seção descreve como uma feature **caminha de `feature/*` até `main`**.

### 1. Feature mergeada em `develop`

Uma PR `feature/* → develop` é aprovada e mergeada. O CI:

- Roda testes automatizados (unitários, integração).
- Opcionalmente, faz deploy em um ambiente de "dev" (não é o ambiente de QA).

Neste ponto a feature está integrada com as demais, mas **ainda não foi validada pelo QA**.

### 2. Criação da `release/*`

Quando o time decide fechar um pacote para validação (ver [Quando criar uma `release/*`](#release)), alguém com permissão executa:

```bash
git checkout develop
git pull
git checkout -b release/v1.4.0
git push -u origin release/v1.4.0
```

A criação da branch dispara automaticamente o deploy em **staging**.

A partir desse momento:
- **`develop` continua aberta** para novas features e bugfixes — a validação não bloqueia o time.
- **`release/v1.4.0` está congelada** para novas features. Só correções de bugs encontrados pelo QA entram nela.

### 3. QA valida em staging

O time de QA testa a release em staging. Possíveis resultados:

- **Aprovado:** segue para o passo 4 (promoção para prod).
- **Bug encontrado:** abre-se uma `bugfix/*` que **tem como destino `release/v1.4.0`** (não `develop`!).

#### Como tratar bugs encontrados em QA

```bash
# A partir da release branch, não de develop
git checkout release/v1.4.0
git pull
git checkout -b bugfix/LAB-301-fix-region-filter

# ... correções e commits ...

git push -u origin bugfix/LAB-301-fix-region-filter
# Abrir PR: bugfix/LAB-301-fix-region-filter → release/v1.4.0
```

Após o merge, novo deploy em staging, nova rodada de QA.

> **Importante:** o bug corrigido em `release/v1.4.0` precisa ser propagado para `develop`. Isso é garantido no passo 4, quando `release/*` é mergeada em `develop` ao final do ciclo.

### 4. Promoção `release/* → main` (e back-merge para `develop`)

Quando o QA aprova `release/v1.4.0`, executam-se **dois merges**, nesta ordem:

**4.1 — Merge em `main` (deploy em prod):**
- Abrir PR `release/v1.4.0 → main`.
- Aprovação obrigatória de quem aprovou o QA.
- Merge dispara deploy automático em produção.

**4.2 — Back-merge em `develop`:**
- Abrir PR `release/v1.4.0 → develop`.
- Esse merge garante que **todos os bugfixes aplicados na release voltem para `develop`**.
- Sem esse passo, os bugs ressurgem no próximo ciclo.

**4.3 — Tag de versão e cleanup:**
- Criar tag `v1.4.0` no commit de `main` (`git tag v1.4.0 && git push --tags`).
- Deletar a branch `release/v1.4.0`.

### Cadência

Não há janela fixa. A cadência típica em times com QA dedicado é de **2 a 3 ciclos por semana**, mas pode ser maior ou menor dependendo do volume.

O que evitar:
- **Releases muito grandes** (várias semanas de features acumuladas) — aumentam a chance de bugs e dificultam validação.
- **Releases muito frequentes** (várias por dia) — geram cerimônia desproporcional. Se vocês precisam dessa frequência, vale reconsiderar o modelo.

### Diagrama: cenário do bloqueio resolvido

O cenário "feature A reprovada não bloqueia feature B" funciona assim:

```
Tempo →

develop:    ──A──B──────────────────C──D──...  (continua aceitando features)
                  │                  
                  └─ cut release/v1.4.0
                                              
release:           ──[A,B]──fix──fix──✓ approved
                                              │
main:                                          └─ merge → deploy v1.4.0
                                                          (A e B em prod)

Próximo ciclo:
develop:                              ──C──D──E──...
                                              │
                                              └─ cut release/v1.5.0 (com C, D, E)
```

Se a feature A tivesse um bug grave detectado em QA que **não pudesse ser corrigido rapidamente**, há duas saídas:

1. **Reverter A na release/*** (e em `develop`), seguir com B sozinha.
2. **Cancelar a release/***, voltar a feature A para "em desenvolvimento", e cortar nova release apenas com B mais tarde.

A opção 1 é mais rápida; a 2 é mais limpa. Decisão fica com o tech lead.

---

## Convenção de nomes

### Formato

```
<tipo>/<id-do-ticket>-<descrição-curta-em-kebab-case>
```

Exemplos:

```
feature/LAB-123-revenue-by-region-endpoint
feature/LAB-145-add-auth-middleware
bugfix/LAB-198-fix-pagination-offset
hotfix/LAB-204-warehouse-connection-leak
release/v1.4.0
```

### Regras

1. **`<tipo>`** é obrigatório e deve ser um de: `feature`, `bugfix`, `hotfix`, `release`.
2. **`<id-do-ticket>`** referencia a issue/card (Jira, Linear, GitHub Issues). Se o trabalho não tem ticket, **crie um antes de abrir a branch**.
3. **`<descrição-curta>`** em **kebab-case**, em inglês, no infinitivo ou substantivada. Máximo ~50 caracteres.
4. **Sem caracteres especiais, acentos ou espaços.** Apenas `[a-z0-9-]`.
5. **Sem nome de pessoa.** `feature/joao-relatorio` é ruim — quem é dono está no PR, não no nome da branch.
6. **`release/*`** é uma exceção: usa o formato `release/vX.Y.Z` (semver).

### Exemplos bons e ruins

| ✅ Bom | ❌ Ruim | Por quê |
|---|---|---|
| `feature/LAB-123-add-revenue-endpoint` | `feature/revenue` | Sem ID; descrição genérica |
| `bugfix/LAB-198-fix-pagination-offset` | `bug-paginacao` | Sem prefixo padrão; em português |
| `hotfix/LAB-204-warehouse-leak` | `hotfix-urgente` | Sem ID; descrição vaga |
| `feature/LAB-145-auth-middleware` | `feature/Joao_AuthMiddleware` | Nome de pessoa; CamelCase com underscore |
| `release/v1.4.0` | `release/janeiro-2025` | Não segue semver |

---

## Tabela de referência rápida

| Branch | Origem | Destino | Quando usar | Vida útil |
|---|---|---|---|---|
| `main` | — | — | Produção | Permanente |
| `develop` | — | (via `release/*`) | Integração contínua | Permanente |
| `feature/*` | `develop` | `develop` | Nova funcionalidade | Curta (< 3 dias) |
| `bugfix/*` | `develop` ou `release/*` | mesma origem | Bug pré-prod | Curta |
| `release/*` | `develop` | `main` + `develop` | Validação de QA | Curta (horas a dias) |
| `hotfix/*` | `main` | `main` + `develop` | Bug em produção | Muito curta |

---

## Anti-padrões

Coisas que **não fazemos** neste repositório:

- **Push direto em `main`, `develop` ou `release/*`.** Sempre via PR.
- **Branches sem prefixo de tipo.** `LAB-123-revenue` é ambíguo — é feature? bugfix?
- **Branches longas (semanas).** Se uma feature é grande, quebre em sub-features mergeáveis incrementalmente, atrás de feature flag se necessário.
- **Reusar branches.** Cada trabalho, uma branch nova. Não reabra `feature/LAB-100-old-stuff` para um trabalho novo.
- **Nomes com acentos.** Padronizamos para evitar problemas de encoding e manter consistência.
- **Esquecer de deletar a branch após merge.** A configuração do repo deve fazer isso automaticamente; se não fizer, delete manualmente.
- **Hotfix que não volta para `develop`.** Sempre propague — caso contrário, o próximo deploy vai reintroduzir o bug.
- **Promover `release/* → main` sem aval do QA.** A promoção é o gatilho de produção. Sem aprovação registrada, não promove.
- **Esquecer o back-merge `release/* → develop`.** Bugfixes aplicados na release ressurgem no próximo ciclo se não forem propagados. Os dois merges (em `main` e em `develop`) são igualmente obrigatórios.
- **Mergear features novas em `release/*`.** Uma vez criada, a release está congelada — só correções de bugs encontrados pelo QA. Features novas vão para `develop` e entram na próxima release.
- **Ter mais de uma `release/*` ativa simultaneamente.** Apenas uma por vez. Se uma está em validação, a próxima espera.
- **Corrigir bug de QA na branch errada.** Bug encontrado em `release/v1.4.0` deve ter como destino `release/v1.4.0`, não `develop`.
