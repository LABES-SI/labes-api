# Labes API

API do observatório de dados, construída com **FastAPI** seguindo a arquitetura MVC + Service Layer + Repository Pattern.

## Documentação

- [Arquitetura](docs/ARCHITECTURE.md) — estrutura de camadas, responsabilidades, fluxo de requisição e exemplos de código
- [Branches](docs/BRANCHING.md) — convenções de branches e fluxo de trabalho com Git

## Estrutura do projeto

```
labes-api/
├── app/
│   ├── core/              # Configuração, auth, exceções, dependências comuns
│   ├── routes/            # Endpoints HTTP (FastAPI routers)
│   ├── services/          # Lógica de aplicação (autorização, composição, regras)
│   ├── repositories/      # Acesso ao warehouse (queries, mapeamento gold)
│   ├── schemas/           # Pydantic: request/response
│   ├── domain/            # Entidades de domínio (estruturas internas)
│   ├── models/            # ORM do banco operacional próprio
│   ├── middleware/        # Middlewares customizados
│   └── utils/             # Helpers transversais
├── tests/
│   ├── routes/
│   ├── services/
│   └── repositories/
├── docs/
│   ├── ARCHITECTURE.md
│   └── BRANCHING.md
├── main.py                # Ponto de entrada
├── pyproject.toml
└── mise.toml
```

## Requisitos

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) — gerenciador de dependências

## Requisitos

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) - Gerenciador de dependências e pacotes Python (recomendado)

## Instalação

### 1. Instalar uv

Para instalar o [uv](https://github.com/astral-sh/uv):

```bash
pip install uv
```

### 2. Instalar dependências do projeto

```bash
# Instale as dependências do projeto
uv sync
```

Após executar `uv sync`, todas as dependências especificadas no `pyproject.toml` e bloqueadas no `uv.lock` serão instaladas.

## Arquivos de Configuração

### `mise.toml`

O arquivo `mise.toml` é uma configuração opcional utilizada pela ferramenta [mise](https://mise.jdx.dev/). Ele permite definir:

- Versão do Python a ser utilizada no projeto
- Variáveis de ambiente
- Ferramentas adicionais necessárias

**Nota:** Este arquivo é **opcional**. Você pode ignorá-lo se não estiver utilizando a ferramenta `mise`.

## Uso

Você pode executar a aplicação de duas formas:

### Usando uv (Recomendado)

```bash
uv run main.py
```

### Usando Python diretamente

```bash
python main.py
```

A API estará disponível em `http://localhost:8000`
