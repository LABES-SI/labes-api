# SIE — DAD-04 | Conciliação API × referência DAD-03

**Estado:** CONCLUÍDA — VALIDAÇÃO TÉCNICA EXPLORATÓRIA.  
**Perfil:** experimental, não homologado.  
**Data desta preparação:** 2026-10-12.

## 1. Objetivo e resultado da descoberta

A rota preexistente `GET /infraestrutura/analise-temporal` **não atende** à comparação Escola × Município. Em `app/routes/infraestrutura.py`, ela recebe `metrica` e `pibid` e chama `build_analise_temporal`; em `app/services/infraestrutura_service.py`, o serviço cria gráficos por localização e dependência. O caminho não recebe escola/município/ano como comparação, não exclui a selecionada de uma referência municipal e não calcula média não ponderada dos índices das demais escolas.

O repositório existente também contém um tratamento legado de valores ausentes com `COALESCE(col, 0)` em `app/repositories/infraestrutura_repository.py::find_pontos_mapa_raw`. A nova rota não chama esse método e não converte `NULL` em zero.

Foi criada a rota experimental separada:

`GET /infraestrutura/analise-temporal/escola-municipio`

Ela preserva a rota legada e não publica nem altera seus resultados. O endpoint lê a observação da escola alvo para cada ano e, em seguida, somente os pares ano/código municipal presentes nessas observações, usando os valores brutos das 17 colunas sem `COALESCE`. O cálculo da resposta usa frações exatas.

## 2. Contrato experimental implementado

A resposta inclui escola, código e nome municipal observados, ano, versão do contrato e do conjunto candidato, status não homologado, contagens de `sim`, `não`, `NULL`, inválidos e válidos, cobertura, elegibilidade, índice individual, N, referência não ponderada das demais escolas, diferença em pontos percentuais, estado, motivo de indisponibilidade, alertas territoriais e problemas de integridade.

A regra de cobertura completa está identificada apenas como perfil experimental condicional. Escolas parciais e all-NULL são excluídas da referência sem bloquear comparadoras válidas. Valores inválidos ou duplicidades em potenciais comparadoras bloqueiam a referência afetada; problemas da selecionada bloqueiam seu índice/contraste. `N=0` mantém referência e diferença nulas. `N=1` retorna a conta matemática com aviso. Código municipal variável por ano usa o código da observação anual e gera alerta. Não existe corte de 80%.

O endpoint retorna frações na forma `numerador/denominador` para evitar arredondamento intermediário. O conjunto S continua marcado como candidato e não homologado; nenhum campo implica autorização de publicação.

## 3. Evidência DAD-03B localizada e identidade do alvo

O pacote complementar foi encontrado fora do repositório, na pasta temporária local `SIE_DAD03B_20261012T211615Z_433735b9eef44766a6a2c98662a58eeb`. Seu `manifest.json` registra o snapshot PostgreSQL `965:965:`, Q1=4, Q2=155, Q3=16 e Q4=4; o estado SQL e a validação estão `complete`, e a homologação permanece `pending`. A pasta está em Temp e é volátil; este relatório não a trata como arquivo permanente nem copia seus dados para o Git.

As quatro linhas reais de Q1 foram lidas localmente. Em cada ano 2022–2025, Q1 aponta município `1507102` e escola selecionada `15052737`. Isso confirma a identidade do alvo em relação aos identificadores da primeira execução reportados na DAD-03B. O snapshot da primeira execução não está identificado, portanto as execuções permanecem snapshots distintos; não se afirma identidade de snapshot.

O manifesto de checksums foi recalculado localmente: **10 arquivos verificados, zero divergências SHA-256**. Nenhuma credencial foi lida ou registrada. Os arquivos de dados escolares continuam fora do repositório.

## 4. Conciliação HTTP com Q2 e cálculos independentes

A rota foi exercitada via HTTP/ASGI, com o repositório substituído por fixture em memória carregada das linhas brutas de Q2 da pasta temporária. O serviço recebeu os indicadores originais da Q2; a resposta HTTP foi comparada com `independent_calculations.json`, sem arredondamento. Isso valida a integração HTTP e a lógica de cálculo sobre o snapshot exportado, mas **não exercita o método SQL do repositório nem uma conexão PostgreSQL**.

| Ano | Escola exata (%) | N | Referência exata (%) | Diferença exata (pp) | Resultado HTTP × cálculo independente |
|---|---:|---:|---:|---:|---|
| 2022 | 1300/17 | 34 | 8250/289 | 13850/289 | Concordante |
| 2023 | 1300/17 | 34 | 8650/289 | 13450/289 | Concordante |
| 2024 | 1300/17 | 37 | 18400/629 | 29700/629 | Concordante |
| 2025 | 1300/17 | 37 | 20800/629 | 27300/629 | Concordante |

A lista dos 17 campos e os registros brutos não foram copiados para este relatório. A verificação acima utilizou esses valores diretamente em memória; só os agregados e o resultado de concordância foram registrados.

## 5. Testes

A suíte HTTP nova exercita a rota, não apenas a função de serviço, contra os cenários sintéticos DAD-03A:

- T01–T15, incluindo T13A e T13B separadamente e T14 em 2022 e 2023;
- escola não observada, all-NULL, parcial, N=0, N=1, inválido selecionado, inválido em comparadora, duplicidade selecionada e em comparadora;
- exclusão da escola selecionada, média de índices escolares, precisão exata, diferença em pp e parâmetros de ano;
- conjunto sintético (S^*={A,B,C}) é marcado como sintético e não homologado. A execução real usa os 17 candidatos fixos.

**Resultado:** `tests/routes/test_infraestrutura_escola_municipio.py` — **18 passed**. A conciliação HTTP com linhas brutas Q2 — **4/4 anos concordantes**.

A suíte completa foi executada: **63 passed, 1 failed**. A falha isolada e reproduzida é `tests/services/test_conectividade_service.py::test_escolas_hover_traz_pibid_e_ideb`: o teste espera o valor inteiro `7`, mas o serviço retorna a string `'7'`. Esse teste e o serviço de conectividade não foram alterados nesta DAD-04; a falha é alheia à rota experimental.

Nenhum teste fez conexão ao PostgreSQL. Não houve alteração de dados, schema, migration, frontend, auditorias anteriores ou documentos metodológicos.

## 6. Integração real e evidências preservadas

A integração real foi executada manualmente no PowerShell local pelo caminho HTTP → FastAPI → repositório → PostgreSQL local. O executor nesta sessão não acessou o banco nem repetiu consultas. A chamada da rota experimental foi concluída com status `experimental_nao_homologado` para a escola `15052737`, município `1507102` e período 2022–2025.

| Ano | N | Índice escolar (%) | Referência municipal (%) | Diferença (pp) | Conciliação com DAD-03B |
|---|---:|---:|---:|---:|---|
| 2022 | 34 | 1300/17 | 8250/289 | 13850/289 | CONCORDANTE |
| 2023 | 34 | 1300/17 | 8650/289 | 13450/289 | CONCORDANTE |
| 2024 | 37 | 1300/17 | 18400/629 | 29700/629 | CONCORDANTE |
| 2025 | 37 | 1300/17 | 20800/629 | 27300/629 | CONCORDANTE |

Os identificadores da escola e do município correspondem ao alvo identificado na DAD-03B. Os quatro anos foram concordantes em N e nas frações exatas do índice, da referência e da diferença. A concordância reproduz os resultados reportados pela DAD-03B para o mesmo alvo, embora as execuções tenham snapshots distintos.

A validação adicional dos denominadores reportou, em cada ano de 2022 a 2025, 17 indicadores válidos, zero inválidos, cobertura `1/1` e zero problemas. Esses resultados confirmam o denominador integral informado para a escola selecionada nos quatro anos.

A evidência HTTP foi preservada fora do Git em `C:\Users\Bragas dev\Documents\SIE_AUDITORIA\DAD04\SIE_DAD04_HTTP_20261012T220030Z.json`. SHA-256 conferido localmente: `001DEC67ECF314348507870A474EC80B3D6212139ADDC7F3CA6611108D64D341`.

A evidência complementar de denominadores também está fora do Git: `C:\Users\Bragas dev\Documents\SIE_AUDITORIA\DAD04\DAD04_DENOMINADORES.json`. SHA-256 conferido localmente: `7477D03AD941CFD6C7A44F938F96034E6703E4D318BFAE0772CF58F02C50E154`. Os hashes verificados correspondem aos informados para os artefatos. Nenhum dado escolar individual foi adicionado ao repositório.

### Escopo das validações

- **Testes sintéticos:** exercitaram os cenários artificiais da DAD-03A por HTTP/ASGI e validaram os comportamentos da rota experimental sem PostgreSQL.
- **Q2 em memória:** as linhas brutas exportadas de Q2 alimentaram um repositório em memória; a resposta HTTP foi comparada com o cálculo independente. Os quatro anos concordaram, mas esse exercício não chamou o repositório SQL nem abriu conexão ao banco.
- **Integração real:** a execução manual descrita nesta seção percorreu a rota HTTP, FastAPI, repositório e PostgreSQL local e concordou com a DAD-03B nos quatro anos. Essa validação técnica exploratória não constitui homologação semântica.

## 7. Decisão técnica e pendências do projeto

**DAD-04: CONCLUÍDA — VALIDAÇÃO TÉCNICA EXPLORATÓRIA.** A rota experimental foi integrada e exercitada no caminho real até o PostgreSQL local; os quatro resultados anuais concordaram com a DAD-03B para a mesma escola e município; os denominadores e a cobertura informados foram conferidos; e os arquivos de evidência preservados fora do Git tiveram seus hashes SHA-256 verificados.

A suíte nova da rota registrou `18 passed`. A suíte completa registrou **63 passed, 1 failed** e, portanto, não está aprovada como um todo. A falha isolada é `tests/services/test_conectividade_service.py::test_escolas_hover_traz_pibid_e_ideb`: o teste espera o inteiro `7` e recebe a string `'7'`. O serviço e o teste de conectividade não foram alterados nesta DAD-04; essa falha permanece registrada como pendência separada.

A conclusão não homologa o significado dos indicadores nem autoriza uso oficial ou publicação. Permanecem explicitamente os estados do projeto: **DAD-01 — NÃO HOMOLOGADA; DAD-02 — matriz preliminar; DAD-05 — contrato metodológico condicional; conjunto S — indicadores candidatos, sem homologação semântica; publicação de indicadores oficiais — não autorizada.**

As próximas etapas do projeto dependem da resolução da falha da suíte completa e das decisões/homologações metodológicas pendentes. Qualquer desenvolvimento posterior deve permanecer dentro dessas condições; a validação técnica exploratória concluída aqui não as substitui.