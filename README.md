# Labes API

API desenvolvida com arquitetura MVC.

## Estrutura do Projeto

```
labes-api/
├── app/                      # Diretório principal da aplicação
│   ├── models/               # Modelos de dados e estruturas de banco de dados
│   ├── controllers/          # Manipuladores de requisições e lógica de controle
│   ├── views/                # Serializadores de resposta e schemas
│   ├── routes/               # Endpoints da API e roteamento
│   ├── services/             # Lógica de negócios e integrações externas
│   ├── middleware/           # Middleware customizado
│   ├── utils/                # Funções utilitárias e helpers
│   └── config/               # Configurações da aplicação
├── tests/                    # Testes unitários e de integração
├── main.py                   # Ponto de entrada da aplicação
├── pyproject.toml            # Configuração do projeto
├── mise.toml                 # Configuração do ambiente
└── README.md                 # Este arquivo
```

## Descrição das Pastas

- **models/**: Define as estruturas de dados e modelos do banco de dados
- **controllers/**: Contém a lógica de controle que processa requisições
- **views/**: Serializa dados para resposta ao cliente
- **routes/**: Define os endpoints e mapeamento de rotas
- **services/**: Implementa a lógica de negócios e integrações
- **middleware/**: Middleware para processar requisições/respostas
- **utils/**: Funções auxiliares reutilizáveis
- **config/**: Configurações gerais da aplicação
- **tests/**: Testes unitários e testes de integração

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