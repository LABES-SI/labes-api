# SIE — DAD-02 | Matriz de comparabilidade temporal

**Funcionalidade:** Análise Temporal de Infraestrutura — Escola × Município  
**Recorte avaliado:** 2022–2025  
**Versão:** 0.2 — evidência documental anual incorporada; decisão de homologação pendente  
**Base empírica:** resultados Q1–Q8 registrados na DAD-01  
**Estado:** preliminar; 68 verificações documentais registradas; não homologa equivalência semântica nem o conjunto definitivo S  
**Estado herdado da DAD-01:** auditoria estrutural e empírica concluída conforme reportada; parecer documental **NÃO HOMOLOGADA**.

> Este documento reutiliza os resultados e limitações documentados da DAD-01 e incorpora a matriz documental INEP indicada na seção 3.1. Não foram feitas novas consultas SQL, processamento de microdados ou investigação nova de ETL. Disponibilidade na Silver, consistência documental dos dicionários e homologação semântica institucional são dimensões distintas.

## 1. Objetivo e escopo

Construir uma avaliação preliminar da comparabilidade dos 17 indicadores presentes em silver.infraestrutura_comum para 2022, 2023, 2024 e 2025, preservando completude, limitações de fonte e incerteza semântica.

Esta análise não define fórmula, pesos, limite de cobertura ou denominador final do índice — decisões reservadas à DAD-05 — e não implementa a funcionalidade. A DAD-01 permanece NÃO HOMOLOGADA. A classificação técnica preliminar nesta matriz não altera esse parecer nem autoriza uso como conjunto semântico validado.

## 2. Evidências herdadas da DAD-01

As referências locais principais são o [relatório final da DAD-01](DAD-01_AUDITORIA_E_HOMOLOGACAO.md), o [LEIA-ME do pacote de evidências](evidencias/LEIA-ME.md), a [matriz Q5–Q8 e sua reprodução SQL documentada](evidencias/02_EVIDENCIAS_Q5_Q8_SQL.txt) e a [investigação documental e territorial](evidencias/03_INVESTIGACAO_DOCUMENTAL_TERRITORIAL.txt). O SQL existente não foi executado nesta etapa.

Resultados reportados: 13.764 registros escola/ano entre 2022 e 2025; 3.583 em 2022, 3.396 em 2023, 3.393 em 2024 e 3.392 em 2025; 22 municípios por ano. Os 17 campos estão fisicamente presentes na Silver segundo o inventário anterior. Em todas as 68 combinações campo × ano, o domínio observado foi 0, 1 e NULL, com zero valores inválidos.

Para cada ano, as contagens de válidos 0/1 e NULL são iguais nos 17 indicadores. Há 12.515 registros com todos os 17 indicadores válidos e 1.249 registros com todos os 17 NULL; não foram reportados registros com cobertura parcial de 1 a 16 indicadores válidos. Os percentuais usam como denominador o total anual de registros escola/ano.

A matriz documental SIE registra conferência dos dicionários oficiais do INEP de 2022–2025 para os 17 indicadores. O conteúdo verificável e os limites dessa evidência estão detalhados na seção 3.1. Permanecem herdadas da DAD-01 as lacunas de linhagem produtora da Silver, explicação dos 1.249 registros totalmente nulos e decisões territoriais; não foram reabertas nesta atualização.

## 3. Matriz completa de comparabilidade temporal

Formato de cada célula anual: **válidos 0/1 / NULL / completude**. Completude = válidos 0/1 divididos pelo total de registros do ano. Denominadores: 2022 = 3.583; 2023 = 3.396; 2024 = 3.393; 2025 = 3.392. A evidência DAD-01 informa que esses totais se repetem para cada um dos 17 campos.

| Campo técnico | Rótulo operacional da API | Presença/domínio observado na Silver | 2022 | 2023 | 2024 | 2025 | Definição oficial 2022–2025 | Classificação preliminar |
|---|---|---|---:|---:|---:|---:|---|---|
| IN_AGUA_POTAVEL | Água potável | Presente; 0/1/NULL; inválidos 0 | 3.131 / 452 / 87,38% | 3.138 / 258 / 92,40% | 3.132 / 261 / 92,31% | 3.114 / 278 / 91,80% | Verificação documental por ano: seção 3.1 | 2 — consistência documental; comparabilidade semântica pendente |
| IN_ENERGIA_REDE_PUBLICA | Energia (rede pública) | Presente; 0/1/NULL; inválidos 0 | 3.131 / 452 / 87,38% | 3.138 / 258 / 92,40% | 3.132 / 261 / 92,31% | 3.114 / 278 / 91,80% | Verificação documental por ano: seção 3.1 | 2 — consistência documental; comparabilidade semântica pendente |
| IN_ESGOTO_REDE_PUBLICA | Esgoto (rede pública) | Presente; 0/1/NULL; inválidos 0 | 3.131 / 452 / 87,38% | 3.138 / 258 / 92,40% | 3.132 / 261 / 92,31% | 3.114 / 278 / 91,80% | Verificação documental por ano: seção 3.1 | 2 — consistência documental; comparabilidade semântica pendente |
| IN_LIXO_SERVICO_COLETA | Coleta de lixo | Presente; 0/1/NULL; inválidos 0 | 3.131 / 452 / 87,38% | 3.138 / 258 / 92,40% | 3.132 / 261 / 92,31% | 3.114 / 278 / 91,80% | Verificação documental por ano: seção 3.1 | 2 — consistência documental; comparabilidade semântica pendente |
| IN_BANHEIRO | Banheiro | Presente; 0/1/NULL; inválidos 0 | 3.131 / 452 / 87,38% | 3.138 / 258 / 92,40% | 3.132 / 261 / 92,31% | 3.114 / 278 / 91,80% | Verificação documental por ano: seção 3.1 | 2 — consistência documental; comparabilidade semântica pendente |
| IN_BANHEIRO_PNE | Banheiro acessível (PNE) | Presente; 0/1/NULL; inválidos 0 | 3.131 / 452 / 87,38% | 3.138 / 258 / 92,40% | 3.132 / 261 / 92,31% | 3.114 / 278 / 91,80% | Verificação documental por ano: seção 3.1 | 2 — consistência documental; comparabilidade semântica pendente |
| IN_BIBLIOTECA | Biblioteca | Presente; 0/1/NULL; inválidos 0 | 3.131 / 452 / 87,38% | 3.138 / 258 / 92,40% | 3.132 / 261 / 92,31% | 3.114 / 278 / 91,80% | Verificação documental por ano: seção 3.1 | 2 — consistência documental; comparabilidade semântica pendente |
| IN_SALA_LEITURA | Sala de leitura | Presente; 0/1/NULL; inválidos 0 | 3.131 / 452 / 87,38% | 3.138 / 258 / 92,40% | 3.132 / 261 / 92,31% | 3.114 / 278 / 91,80% | Verificação documental por ano: seção 3.1 | 2 — consistência documental; comparabilidade semântica pendente |
| IN_LABORATORIO_CIENCIAS | Laboratório de ciências | Presente; 0/1/NULL; inválidos 0 | 3.131 / 452 / 87,38% | 3.138 / 258 / 92,40% | 3.132 / 261 / 92,31% | 3.114 / 278 / 91,80% | Verificação documental por ano: seção 3.1 | 2 — consistência documental; comparabilidade semântica pendente |
| IN_LABORATORIO_INFORMATICA | Laboratório de informática | Presente; 0/1/NULL; inválidos 0 | 3.131 / 452 / 87,38% | 3.138 / 258 / 92,40% | 3.132 / 261 / 92,31% | 3.114 / 278 / 91,80% | Verificação documental por ano: seção 3.1 | 2 — consistência documental; comparabilidade semântica pendente |
| IN_SALA_MULTIUSO | Sala multiuso | Presente; 0/1/NULL; inválidos 0 | 3.131 / 452 / 87,38% | 3.138 / 258 / 92,40% | 3.132 / 261 / 92,31% | 3.114 / 278 / 91,80% | Verificação documental por ano: seção 3.1 | 2 — consistência documental; comparabilidade semântica pendente |
| IN_SALA_ATENDIMENTO_ESPECIAL | Sala de atendimento especial | Presente; 0/1/NULL; inválidos 0 | 3.131 / 452 / 87,38% | 3.138 / 258 / 92,40% | 3.132 / 261 / 92,31% | 3.114 / 278 / 91,80% | Verificação documental por ano: seção 3.1 | 2 — consistência documental; comparabilidade semântica pendente |
| IN_COZINHA | Cozinha | Presente; 0/1/NULL; inválidos 0 | 3.131 / 452 / 87,38% | 3.138 / 258 / 92,40% | 3.132 / 261 / 92,31% | 3.114 / 278 / 91,80% | Verificação documental por ano: seção 3.1 | 2 — consistência documental; comparabilidade semântica pendente |
| IN_REFEITORIO | Refeitório | Presente; 0/1/NULL; inválidos 0 | 3.131 / 452 / 87,38% | 3.138 / 258 / 92,40% | 3.132 / 261 / 92,31% | 3.114 / 278 / 91,80% | Verificação documental por ano: seção 3.1 | 2 — consistência documental; comparabilidade semântica pendente |
| IN_QUADRA_ESPORTES | Quadra de esportes | Presente; 0/1/NULL; inválidos 0 | 3.131 / 452 / 87,38% | 3.138 / 258 / 92,40% | 3.132 / 261 / 92,31% | 3.114 / 278 / 91,80% | Verificação documental por ano: seção 3.1 | 2 — consistência documental; comparabilidade semântica pendente |
| IN_PATIO_COBERTO | Pátio coberto | Presente; 0/1/NULL; inválidos 0 | 3.131 / 452 / 87,38% | 3.138 / 258 / 92,40% | 3.132 / 261 / 92,31% | 3.114 / 278 / 91,80% | Verificação documental por ano: seção 3.1 | 2 — consistência documental; comparabilidade semântica pendente |
| IN_AUDITORIO | Auditório | Presente; 0/1/NULL; inválidos 0 | 3.131 / 452 / 87,38% | 3.138 / 258 / 92,40% | 3.132 / 261 / 92,31% | 3.114 / 278 / 91,80% | Verificação documental por ano: seção 3.1 | 2 — consistência documental; comparabilidade semântica pendente |

**Leitura da matriz técnica:** as contagens de válidos/NULL continuam sendo resultados reportados pela DAD-01, sem nova contagem nesta atualização. A evidência documental dos nomes, descrições, tipos, domínios e coleta anual dos 68 pares está na seção 3.1; ela não altera os dados observados da Silver nem, por si só, prova instruções de preenchimento, tratamento de ausência ou equivalência operacional.

### 3.1 Evidência documental INEP — 68 pares indicador × ano

A matriz documental informa que foram examinadas as planilhas dos dicionários oficiais do Censo Escolar de 2022, 2023, 2024 e 2025, sem leitura ou processamento de microdados. Para cada par, a fonte informa variável e descrição nas colunas B–C, tipo na D, domínio na F e marca de coleta anual nas colunas V, W, X e Y, respectivamente. O estado abaixo significa que esses atributos foram registrados como conferidos na matriz; não significa homologação institucional.

A revisão local confirmou o SHA-256 do arquivo de 2025 dicionario_2025_extraido.xlsx (140e0f3d0df0241330f1c26fd45e516e63bd2ad60fb7ae3c9ae5cb47c6290166) e conferiu nas 17 linhas citadas o nome, a descrição, Num, domínio 0 - Não / 1 - Sim e s na coluna Y. Os arquivos-fonte de 2022–2024 não estão presentes neste checkout. Para esses anos, as linhas e hashes abaixo são os registros documentais da matriz fornecida e não foram recalculados localmente nesta atualização.

A matriz reporta para os 68/68 pares nomes e descrições idênticos, tipo Num, domínio 0 = Não e 1 = Sim e coleta anual marcada. Não foi detectada divergência nesses atributos nos dicionários examinados, segundo a evidência apresentada.
#### Rastreabilidade indicador × ano (17 × 4)

Em cada célula de ano: linha da planilha e coluna da marca de coleta do ano (`s`). A definição fica nas colunas B–F da mesma linha.

| Indicador | Definição oficial (descrição do dicionário) | 2022 (V) | 2023 (W) | 2024 (X) | 2025 (Y) |
|---|---|---:|---:|---:|---:|
| `IN_AGUA_POTAVEL` | Fornece água potável para o consumo humano | verificado — linha 85: `s` | verificado — linha 100: `s` | verificado — linha 101: `s` | verificado — linha 108: `s` |
| `IN_ENERGIA_REDE_PUBLICA` | Abastecimento de energia elétrica - Rede pública | verificado — linha 91: `s` | verificado — linha 106: `s` | verificado — linha 108: `s` | verificado — linha 115: `s` |
| `IN_ESGOTO_REDE_PUBLICA` | Esgoto sanitário - Rede pública | verificado — linha 97: `s` | verificado — linha 112: `s` | verificado — linha 114: `s` | verificado — linha 121: `s` |
| `IN_LIXO_SERVICO_COLETA` | Destinação do lixo - Serviço de coleta | verificado — linha 102: `s` | verificado — linha 117: `s` | verificado — linha 119: `s` | verificado — linha 126: `s` |
| `IN_BANHEIRO` | Dependências físicas existentes e utilizadas na escola - Banheiro | verificado — linha 119: `s` | verificado — linha 134: `s` | verificado — linha 137: `s` | verificado — linha 144: `s` |
| `IN_BANHEIRO_PNE` | Dependências físicas existentes e utilizadas na escola - Banheiro acessível, adequado ao uso de pessoas com deficiência ou mobilidade reduzida | verificado — linha 121: `s` | verificado — linha 136: `s` | verificado — linha 139: `s` | verificado — linha 146: `s` |
| `IN_BIBLIOTECA` | Dependências físicas existentes e utilizadas na escola - Biblioteca | verificado — linha 125: `s` | verificado — linha 140: `s` | verificado — linha 143: `s` | verificado — linha 150: `s` |
| `IN_SALA_LEITURA` | Dependências físicas existentes e utilizadas na escola - Sala de leitura | verificado — linha 148: `s` | verificado — linha 164: `s` | verificado — linha 167: `s` | verificado — linha 174: `s` |
| `IN_LABORATORIO_CIENCIAS` | Dependências físicas existentes e utilizadas na escola - Laboratório de ciências | verificado — linha 131: `s` | verificado — linha 146: `s` | verificado — linha 149: `s` | verificado — linha 156: `s` |
| `IN_LABORATORIO_INFORMATICA` | Dependências físicas existentes e utilizadas na escola - Laboratório de informática | verificado — linha 132: `s` | verificado — linha 147: `s` | verificado — linha 150: `s` | verificado — linha 157: `s` |
| `IN_SALA_MULTIUSO` | Dependências físicas existentes e utilizadas na escola - Sala multiuso (música, dança e artes) | verificado — linha 145: `s` | verificado — linha 160: `s` | verificado — linha 163: `s` | verificado — linha 170: `s` |
| `IN_SALA_ATENDIMENTO_ESPECIAL` | Dependências físicas existentes e utilizadas na escola - Sala de Recursos Multifuncionais para Atendimento Educacional Especializado (AEE) | verificado — linha 152: `s` | verificado — linha 168: `s` | verificado — linha 171: `s` | verificado — linha 178: `s` |
| `IN_COZINHA` | Dependências físicas existentes e utilizadas na escola - Cozinha | verificado — linha 127: `s` | verificado — linha 142: `s` | verificado — linha 145: `s` | verificado — linha 152: `s` |
| `IN_REFEITORIO` | Dependências físicas existentes e utilizadas na escola - Refeitório | verificado — linha 141: `s` | verificado — linha 156: `s` | verificado — linha 159: `s` | verificado — linha 166: `s` |
| `IN_QUADRA_ESPORTES` | Dependências físicas existentes e utilizadas na escola - Quadra de esportes coberta ou descoberta | verificado — linha 138: `s` | verificado — linha 153: `s` | verificado — linha 156: `s` | verificado — linha 163: `s` |
| `IN_PATIO_COBERTO` | Dependências físicas existentes e utilizadas na escola - Pátio coberto | verificado — linha 134: `s` | verificado — linha 149: `s` | verificado — linha 152: `s` | verificado — linha 159: `s` |
| `IN_AUDITORIO` | Dependências físicas existentes e utilizadas na escola - Auditório | verificado — linha 116: `s` | verificado — linha 131: `s` | verificado — linha 134: `s` | verificado — linha 141: `s` |
**Limite de interpretação:** a consistência textual e de codificação dos dicionários é evidência positiva de compatibilidade documental. Ela não comprova, sem as instruções dos questionários e evidência da transformação, que critérios de resposta, população aplicável, condições de preenchimento, não resposta e transformação para a Silver permaneceram iguais.

## 4. Critérios de classificação

1. **Confirmada documentalmente:** dicionários, leiautes ou documentos oficiais identificados por ano e versão demonstram o campo, sua definição, domínio, códigos/ausências e continuidade semântica entre os anos que se pretende comparar.
2. **Tecnicamente compatível, mas não demonstrada semanticamente:** estrutura de dados disponível e domínio observado coerente, mas documentação oficial insuficiente para confirmar que significado e critérios de preenchimento são equivalentes.
3. **Incompatibilidade demonstrada:** evidência oficial comparável mostra mudança semântica, domínio, aplicabilidade ou regra de preenchimento que impeça tratar os anos como a mesma medida sem harmonização explicitamente autorizada.

Não se promove um indicador à classe 1 por nome igual, tipo igual ou domínio observado igual. Uma diferença empírica nas frequências de 0/1 não demonstra, sozinha, mudança semântica. A classe 3 também exige evidência de incompatibilidade; incerteza documental não equivale a incompatibilidade comprovada.

## 5. Resultados por indicador

- **17 tecnicamente disponíveis:** todos os campos constam da Silver e têm valores observados no recorte dos quatro anos segundo o inventário anterior e Q5–Q8 da DAD-01.
- **17 com domínio observado 0/1/NULL:** nenhum valor fora de 0/1 foi reportado em qualquer dos 68 pares campo/ano.
- **68 verificações documentais de dicionário registradas:** em 17 indicadores × 4 anos, a matriz identifica correspondência nominal/descritiva, tipo Num, domínio 0/1 e coleta anual. Os arquivos 2022–2024 não estão disponíveis neste checkout para recalcular hash/linhas; a evidência local do arquivo 2025 foi conferida.
- **0 com homologação semântica institucional registrada.** A evidência documental agora confirma consistência dos campos do dicionário, mas deixa pendentes instruções operacionais, ausência/aplicabilidade, proveniência da Silver e decisão formal.
- **0 com incompatibilidade semântica demonstrada.**
- **17 permanecem preliminarmente na classe 2:** disponíveis na Silver e consistentes nos atributos de dicionário listados; a classe não equivale a parecer institucional de comparabilidade semântica.

As distribuições de zeros e uns por indicador/ano estão preservadas na evidência Q5–Q8 referenciada na seção 11. Variações nessas frequências são resultados descritivos e não permitem concluir mudança conceitual nem equivalência.

## 6. Proposta preliminar de conjunto fixo

Os **17 indicadores permanecem candidatos preliminares**. O professor orientador esclareceu que foram selecionados por estarem presentes nos quatro anos. A matriz documental também reporta coleta anual nos quatro dicionários. Esse critério justifica disponibilidade e composição temporal comum, mas não substitui a avaliação semântica nem aprova institucionalmente o conjunto S.

Esta lista candidata não é o conjunto fixo definitivo S, não é homologada para cálculo e não afirma que os indicadores medem o mesmo conceito nos quatro anos. Nenhum indicador está atualmente confirmado documentalmente; qualquer decisão final sobre inclusão, exclusão ou harmonização depende da evidência oficial anual e da revisão responsável.

Uma exclusão alteraria o conteúdo do conjunto de recursos representado. Dadas as regras gerais de pesos iguais, a quantidade de indicadores elegíveis poderia afetar denominador, escala ou cobertura do índice, dependendo da fórmula e da regra de dados válidos. Essas consequências não são quantificadas aqui: fórmula, normalização e pesos pertencem à DAD-05.

## 7. Impacto das condições temporais e territoriais

### População anual versus painel fixo

Usar escolas válidas em cada ano maximiza a população observada naquele ano, mas os grupos variam: 3.131 escolas completas em 2022, 3.138 em 2023, 3.132 em 2024 e 3.114 em 2025. Comparações de agregados podem refletir simultaneamente diferenças de infraestrutura e mudanças na composição observada. As evidências não demonstram ausência aleatória.

No período, 3.771 escolas aparecem em pelo menos um ano; 3.178 aparecem nos quatro; 2.892 têm os 17 campos válidos nos quatro anos; e 286 das presentes nos quatro têm ao menos um ano sem indicadores válidos. A interseção de 2.892 pode ser usada como sensibilidade para manter painel fixo, mas a seleção de casos completos pode excluir escolas de forma não aleatória. Nenhuma das duas populações está homologada como estratégia definitiva.

### Conjunto fixo de indicadores e denominadores

Manter o mesmo conjunto de indicadores ao longo do tempo reduz mudanças de composição do que se mede, mas só é justificável após demonstrar equivalência semântica. Para cada ano e escola, a análise futura deve preservar denominadores: registros elegíveis, indicadores válidos e escolas efetivamente incluídas na referência. A definição matemática de cada denominador do índice permanece pendente da DAD-05.

### NULL

NULL significa ausência de observação nesta matriz; não é zero, resposta “Não” ou ausência declarada do recurso. Os 1.249 registros com 17 campos nulos devem permanecer identificáveis. A DAD-01 documenta que o repository da API atual aplica COALESCE(col, 0), risco incompatível com a regra metodológica desta iniciativa. Esta DAD-02 não altera nem redefine o comportamento da API.

### Município por ano e grupo de referência

O município registrado na Silver para o ano da observação é o atributo territorial anual disponível, mas requer ressalvas: foram documentadas quatro escolas com códigos municipais variáveis e quatro linhas com código 1501402 associado ao nome “Ananindeua”. A junção com gold.dim_municipio não teve órfãos ou multiplicação segundo Q8; gold.dim_entidade tem apenas 219, 52, 108 e 3.392 correspondências exatas por ano e não foi homologada como dimensão histórica. Nenhuma divergência deve ser corrigida automaticamente. A decisão final sobre identificação municipal histórica permanece pendente.

Conforme a regra metodológica geral do projeto, a referência municipal futura deve usar o mesmo município e ano e excluir a escola selecionada do grupo de comparação. Deve também registrar quantas outras escolas têm resultado válido no denominador; se não houver grupo válido, não se deve inventar referência. A fórmula e demais regras de cálculo não são estabelecidas nesta etapa.

O corte de 80% não está homologado. A sensibilidade de 14/17 não separa casos parciais neste recorte porque só foram observadas zero ou 17 respostas válidas; não deve ser transformada em requisito definitivo.

## 8. Riscos e pendências essenciais

1. **Semântica e instruções operacionais:** a matriz documental registra nomes, descrições, tipo, domínio 0/1 e coleta anual consistentes nos 68 pares. Ainda faltam instruções de questionário/manual sobre condições de preenchimento, população aplicável, não resposta, ausência/não aplicabilidade, filtros e possíveis mudanças operacionais; é preciso decidir se essas fontes são necessárias para cada indicador.
2. **Rastreabilidade herdada:** a matriz confirma que os dicionários não demonstram a transformação da fonte para silver.infraestrutura_comum. A origem/ETL continua não identificado na DAD-01; os 1.249 registros com os 17 campos nulos e sua associação com TP_LOCALIZACAO_DIFERENCIADA IS NULL continuam sem explicação causal.
3. **Comparação de populações:** a cobertura varia por ano e não há evidência de que as ausências sejam aleatórias; população anual disponível e painel completo respondem a recortes diferentes.
4. **Territorialidade:** divergências de código/nome, escolas com código variável e cobertura temporal desigual de gold.dim_entidade podem mudar a composição municipal; continua pendente decisão sobre proveniência e tratamento, sem correção automática.
5. **Tratamento da API:** COALESCE(NULL, 0) pode converter ausência em valor zero no score atual; não deve ser assumido como regra metodológica válida para o índice futuro.
6. **Decisão institucional:** a disponibilidade comum dos 17 indicadores está justificada, mas inclusão/exclusão final em S requer decisão explícita. Fórmula, pesos, cobertura, painel temporal e demais regras permanecem sujeitos à DAD-05.

A evidência documental reduziu a pendência de identificação e comparação dos dicionários: 68 referências estão registradas e os atributos informados são consistentes. Permanecem pendentes a instrução semântica operacional, a linhagem e os nulos, as decisões territoriais e as aprovações institucionais. A DAD-01 permanece NÃO HOMOLOGADA.

## 9. Critérios objetivos de aceitação da DAD-02

A revisão desta versão altera o estado das verificações documentais, sem transformar automaticamente consistência textual em homologação:

| Critério | Estado nesta versão | Evidência/pendência |
|---|---|---|
| 68 pares indicador × ano com fonte, planilha e linha | **Registrado na matriz; reprodutibilidade local parcial** | Há referências e hashes SHA-256 dos quatro arquivos extraídos. O arquivo 2025 está presente, seu hash foi recalculado e as 17 linhas citadas foram conferidas. Arquivos 2022–2024 não estão no checkout para conferência local independente. |
| Nome, descrição, tipo, domínio 0/1 e coleta anual | **Verificado conforme a matriz para 68/68** | A matriz reporta igualdade textual, tipo Num, 0 = Não, 1 = Sim e s nos quatro anos. |
| Instruções, aplicabilidade, não resposta e mudanças operacionais | **Pendente** | Dicionários não bastam para resolver as regras de preenchimento não registradas; consultar questionários/manuais quando materialmente necessários. |
| Comparabilidade semântica e classe final por indicador | **Parecer técnico preparado; decisão responsável pendente** | Os atributos do dicionário não mostram divergência, mas não demonstram continuidade completa de critérios operacionais ou da transformação para Silver. Nenhum indicador deve ser elevado à classe homologada automaticamente. |
| Conjunto fixo S | **Candidato comum documentado; homologação pendente** | O orientador informou que os 17 foram selecionados por presença nos quatro anos. A escolha final e sua aprovação pertencem à instância responsável. |
| População anual versus painel fixo e tratamento de NULL | **Limites registrados; estratégia final pendente** | Evidência DAD-01 permanece reportada; não reexecutada nesta atualização. |
| Proveniência, ausências e integridade da Silver | **Pendente/limitação herdada da DAD-01** | Matriz não demonstra ETL, regra de nulos, garantia de grão nem causa dos 1.249 casos integralmente nulos. |
| Território e cobertura geográfica | **Decisão pendente/limitação herdada** | Divergências e cobertura desigual de dimensões precisam de regra e decisão documentadas, sem correção automática. |
| Revisão e aprovação formal | **Pendente** | Professor/equipe responsável deve registrar decisão expressa sobre comparabilidade e sobre o conjunto S. |

## 10. Parecer técnico e condições para homologação

**Parecer técnico para apreciação do professor/equipe:** a matriz dos dicionários fornece evidência documental positiva de que os 17 indicadores aparecem nos quatro anos com nome e descrição idênticos, tipo Num, domínio 0 - Não / 1 - Sim e marca de coleta anual. Nos campos do dicionário examinados, os 68 pares são consistentes; não foi identificada incompatibilidade documental nesses atributos. O critério informado pelo orientador — presença nos quatro anos — sustenta mantê-los como candidatos comuns.

Este parecer não transforma identidade textual em equivalência semântica completa nem representa aprovação institucional. Permanecem sem resolução as regras de preenchimento/aplicabilidade e ausência quando não descritas no dicionário, a linhagem da Silver, a causa dos nulos e a decisão territorial herdada da DAD-01. Recomenda-se ao professor/equipe aceitar ou rejeitar explicitamente a comparabilidade documental dos 17 candidatos e definir se instruções complementares alteram essa conclusão. A DAD-02 permanece preliminar, S não homologado, DAD-01 NÃO HOMOLOGADA e DAD-05 condicional.

## 11. Referências documentais e arquivos consultados

- [Relatório técnico final da DAD-01](DAD-01_AUDITORIA_E_HOMOLOGACAO.md) — matriz de definições não verificadas, resultados Q1–Q8, ausências, territorialidade, COALESCE e pendências de homologação.
- [Evidências Q5–Q8 e reprodução SQL documentada](evidencias/02_EVIDENCIAS_Q5_Q8_SQL.txt) — contagens 0/1/NULL/inválidos, denominadores, completude e cardinalidade. Consultado como documento; SQL não executado.
- [Investigação documental e territorial da DAD-01](evidencias/03_INVESTIGACAO_DOCUMENTAL_TERRITORIAL.txt) — achados herdados de ausência e território.
- [Matriz documental INEP 17 × 4](SIE_Matriz_Documental_INEP_17_Indicadores_2022_2025.md) — referências de linha, atributos de dicionário e limites da evidência; hashes/linhas de 2022–2024 não recalculados neste checkout.
- [LEIA-ME do pacote de evidências](evidencias/LEIA-ME.md) — natureza reportada dos resultados e orientação para não repetir Q1–Q8.
- INEP, [Microdados do Censo Escolar](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar) — origem indicada pela matriz documental; atributos e limites dos dicionários estão descritos na seção 3.1.

**Controle de escopo:** documento preliminar elaborado a partir de evidências DAD-01. Não houve consulta SQL, alteração de DAD-01, AGENTS.md, código, banco ou configuração; não houve commit/push. DAD-05 permanece condicional; DAD-03A, DAD-03B e DAD-04 não foram reabertas nesta atualização.
