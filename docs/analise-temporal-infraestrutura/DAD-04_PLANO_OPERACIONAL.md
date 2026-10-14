# SIE — DAD-04 | Plano operacional de conciliação API × DAD-03

**Estado de partida:** DAD-03B tecnicamente validada (segundo execução e verificações reportadas), encerramento documental no repositório informado pelo usuário. DAD-04 **EM EXECUÇÃO**, ainda sem resposta real da API confrontada. Este documento não homologa indicadores nem modifica a metodologia.

## 1. Objetivo e decisão inicial

Confrontar um endpoint **real** do backend FastAPI com os casos sintéticos DAD-03A e a amostra exploratória DAD-03B, usando a resposta HTTP efetiva (ASGI/HTTPX ou Uvicorn) — não chamar somente a função de cálculo como substituto da DAD-04. O backend local (branch `develop`) já possui `GET /infraestrutura/analise-temporal`, porém não está demonstrado que implemente a comparação **Escola × média das demais escolas do município**. Verificar primeiro código, serviço, repositório, schemas, documentação OpenAPI e comportamento; não inferir equivalência pelo nome.

Se a rota já satisfizer integralmente o contrato, realizar testes e registrar evidências. Se não satisfizer, implementar **apenas em ambiente local e de forma experimental** uma rota/serviço separado para o caso Escola × Município, preservando endpoints existentes e respeitando a arquitetura FastAPI. Evitar publicar como resultado oficial. A DAD-04 só é concluída quando uma resposta real da API for confrontada.

## 2. Fontes e restrições

1. `docs/analise-temporal-infraestrutura/DAD-03B_VALIDACAO_EMPIRICA_EXPLORATORIA.md` — documento local a ler; arquivo não incluído neste kit.
2. `docs/analise-temporal-infraestrutura/DAD-03A_AMOSTRA_SINTETICA_E_PLANO_VALIDACAO.md` — cenários T01–T15.
3. `docs/analise-temporal-infraestrutura/DAD-05_CONTRATO_METODOLOGICO.md` — fórmulas, elegibilidade e indisponibilidade **condicionais**.
4. `docs/analise-temporal-infraestrutura/DAD-01_AUDITORIA_E_HOMOLOGACAO.md` e DAD-02 — limitações de origem, território e comparabilidade.
5. `DAD04_ORACULO_EXPLORATORIO.json` — valores agregados exatos para teste, *não substitui os vetores brutos de Q2*.
6. Evidências preservadas da DAD-03B no diretório local fora do Git, identificador `SIE_DAD03B_20261012T211615Z_433735b9eef44766a6a2c98662a58eeb`; localizar sem expor senhas, sem incorporar dados brutos no Git.

**Bloqueios permanentes para publicação:** DAD-01 não homologada; DAD-02 preliminar; S de 17 indicadores candidatos não homologado; DAD-05 condicional. Conclusão técnica exploratória da DAD-04 não equivale a homologação semântica.

## 3. Fluxo de execução sem retrabalho

**DAD-04.1 — Descoberta (obrigatória, curta).** Inspecionar `git status`, o estado da branch, o `main.py`, a rota `/infraestrutura/analise-temporal`, seus schemas/serviços/queries e os testes. Classificar: `atende`, `atende_parcialmente` ou `não_atende` ao caso Escola × Município, com caminhos/linhas. Comparar campos e semântica com DAD-05; identificar `COALESCE(...,0)` e outras transformações arriscadas sem alterar as rotas existentes.

**DAD-04.2 — Contrato e oráculo.** Congelar a versão experimental de S (17 candidatos), o recorte 2022–2025, cobertura completa provisória, contagens de `sim`, `não`, `NULL`, índice do selecionado, referência municipal **não ponderada** (escola excluída), `N_ref`, `difference_pp`, status e motivo. A resposta deve permitir identificar município por ano, versão condicional, parâmetros e população. Não arredondar antes de comparar ou de subtrair.

**DAD-04.3 — Endpoint, se necessário.** Desenvolver implementação **mínima, local e isolada**, sem modificar endpoints públicos existentes. Dar preferência ao padrão da arquitetura FastAPI do repositório. Nenhum `NULL` pode virar 0. Não juntar `gold.dim_entidade` como dimensão histórica automaticamente; território deriva da observação anual, com alertas em mudanças/discordâncias. Duplicidades e inválidos bloqueiam resultados afetados, não são silenciosamente excluídos. `N_ref=0` → referência/diferença `null`; `N_ref=1` matematicamente definido (aviso provisório); escola sem dado → `null` distinto de 0; não interpolar séries. Para casos inválidos, não publicar `N` artificialmente definitivo.

**DAD-04.4 — Testes automatizados.** Cobrir T01–T15 (incluindo T13A/T13B e T14 de ambos os anos); os casos sintéticos permanecem identificados como sintéticos. Usar fixtures isoladas e integração por cliente HTTP real (por exemplo `httpx.ASGITransport`) e não somente testes unitários de serviço. Checar campos presentes, tipo, nulos, erros, as mesmas fórmulas exatas e exclusões; registrar provas de execução. Se alguma regra ainda for proposta, mantê-la declarada como perfil experimental, sem alegar homologação.

**DAD-04.5 — Conciliação real.** A integração contra o PostgreSQL local deve ser executada manualmente pelo usuário em PowerShell, fora do sandbox do Codex, com o backend local e sem expor `.env` ou credenciais. O Codex prepara os comandos e compara a saída higienizada depois. Consultar a API no banco local por `school_id=15052737`, `municipality_code=1507102` e anos 2022–2025; demonstrar que o recorte da API é compatível com a evidência DAD-03B, ou classificar `não comparável — snapshot/recorte`. Comparar os valores exatos do JSON de oráculo e, com Q2 bruto local, as 17 respostas, denominadores e inclusão/exclusão de cada escola. Registrar request, response higienizado, observados, esperados, diferenças, hashes e condições de execução. Não aceitar igualdade apenas após arredondamento a duas casas.

**DAD-04.6 — Fechamento.** Produzir `docs/analise-temporal-infraestrutura/DAD-04_CONCILIACAO_API_REFERENCIA.md` com contrato efetivo, evidência de API/HTTP, tabela de testes, divergências identificadas/corrigidas/pendentes, limitações e decisão técnica. Aprovar **VALIDAÇÃO TÉCNICA EXPLORATÓRIA** somente se casos obrigatórios passaram, endpoint real foi exercitado, houve comparação exata com a amostra e divergências foram resolvidas ou impeditivos explicitamente marcados. Manter homologação/publicação pendentes.

## 4. Critérios de aceite e bloqueios

- Município e escola corretos por ano, sem trocar código pelo nome ou inferir continuidade territorial.
- Mesmo conjunto fixo de 17 candidatos durante o teste (não versão homologada).
- Respostas 0, 1 e `NULL` preservadas; contagens de `sim`, `não`, `n_valid_indicators`, cobertura e índice corretas.
- Escola selecionada excluída; média simples dos índices individuais elegíveis; `N_ref` correto, não contagem de todas as escolas.
- Diferenças em pp e sem arredondamento intermediário.
- Estados distintos para não observado, all-NULL, parcial, sem comparadoras, N=1, inválido, duplicado e território pendente.
- Todos os cenários DAD-03A comparados **via API** e amostra real DAD-03B conciliada no mesmo recorte.
- Evidências e logs sem segredos, hashes e identificação da execução; nenhuma escrita no PostgreSQL.
- Não expor a funcionalidade como indicador oficial; evitar commits/push e alterações no frontend até revisão.

## 5. Valores exploratórios exatos da DAD-03B

| Ano | Município | Escola | Sim/válidos | N comparadoras | Referência municipal (%) | Diferença (pp) |
|---|---:|---:|---:|---:|---:|---:|
| 2022 | 1507102 | 15052737 | 13/17 | 34 | 8250/289 | +13850/289 |
| 2023 | 1507102 | 15052737 | 13/17 | 34 | 8650/289 | +13450/289 |
| 2024 | 1507102 | 15052737 | 13/17 | 37 | 18400/629 | +29700/629 |
| 2025 | 1507102 | 15052737 | 13/17 | 37 | 20800/629 | +27300/629 |

O índice da selecionada é `1300/17 %` nos quatro anos. Esses números foram reportados e comparados com a extração complementar. **A amostra bruta, o identificador do snapshot e a identidade do alvo devem ser verificados localmente antes de atribuir plena concordância à API.**
