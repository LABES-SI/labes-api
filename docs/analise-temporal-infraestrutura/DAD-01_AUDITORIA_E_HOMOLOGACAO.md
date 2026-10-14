# SIE — DAD-01 | Auditoria e homologação documental

**Funcionalidade:** Análise Temporal de Infraestrutura — Escola × Município  
**Recorte empírico documentado:** 2022–2025  
**Versão:** 1.1 — atualização documental após esclarecimentos da orientação  
**Data:** 13/10/2026  
**Parecer:** **NÃO HOMOLOGADA**

> Esta versão consolida resultados empíricos anteriormente reportados, evidência documental anual registrada na DAD-02 e esclarecimentos recebidos do professor orientador em 13/10/2026. Nenhuma consulta foi reexecutada e nenhum microdado foi processado. As declarações do professor são identificadas como tais; não são tratadas como verificação do ETL nem como homologação já concedida.

## 1. Resumo executivo

Os resultados Q1–Q8 já registrados descrevem 17 campos em silver.infraestrutura_comum e 13.764 observações escola/ano entre 2022 e 2025. No recorte, foram reportados 12.515 registros com os 17 indicadores válidos e 1.249 registros com os 17 campos NULL, sem cobertura parcial; não foram reportados valores fora de 0/1. Esses resultados continuam sendo evidência reportada, sem reexecução nesta atualização.

A matriz documental associada à DAD-02 registra que os dicionários oficiais de 2022–2025 foram examinados: 17 indicadores em cada edição, com nomes e descrições idênticos, tipo Num, domínio 0 = Não / 1 = Sim e marca de coleta anual. A DAD-02 contém as 68 referências e permanece preliminar: consistência nos campos examinados não equivale a homologação semântica formal.

Segundo esclarecimento recebido do professor orientador em 13/10/2026, os dados utilizados pelo projeto provêm dos microdados oficiais do Censo Escolar/INEP; o processamento que produziu a Silver foi desenvolvido incrementalmente, sem documentação formal preservada, e não foi localizado código original de carga no repositório disponível. Portanto, a origem declarada é conhecida, mas as extrações, filtros, transformações e regras de NULL entre microdados e Silver não foram verificados.

O professor informou também que os 22 municípios observados formam um recorte intencional relacionado à existência de bolsas nesses municípios. Isso afasta a interpretação automática de erro de carga ou de cobertura estadual, mas a regra operacional exata de seleção e as divergências de código municipal ainda precisam ser documentadas e decididas.

**Parecer:** a DAD-01 continua **NÃO HOMOLOGADA** até revisão e decisão expressa do professor ou da equipe. As verificações documentais anuais foram incorporadas; permanecem limitações de proveniência, de explicação dos nulos, de seleção territorial e de resolução das divergências. DAD-02 permanece preliminar, DAD-05 condicional; DAD-03A, DAD-03B e DAD-04 permanecem concluídas no escopo técnico exploratório e não são reabertas aqui.

## 2. Objetivo, escopo e método

A DAD-01 inventaria e qualifica variáveis de infraestrutura que poderão subsidiar, em etapa posterior, uma análise temporal Escola × Município. Não decide o conjunto temporal final de indicadores, fórmula, elegibilidade definitiva nem contrato da funcionalidade; tampouco implementa o índice.

**Escopo documentado:** silver.infraestrutura_comum; os 17 campos da seção 4; anos 2022–2025; e, para controles territoriais, gold.dim_entidade e gold.dim_municipio. Q1–Q8 são tratados conforme reportados. O LEIA-ME determina não repetir Q1–Q8 para recuperar detalhes já disponíveis e esclarece que a inclusão do pacote não constitui reexecução independente nem homologação documental. Q9–Q12 não foram executadas segundo o registro.

Foram lidos integralmente nesta atualização:

- [LEIA-ME.md](evidencias/LEIA-ME.md);
- [01_RELATORIO_DAD01_v0.9.md](evidencias/01_RELATORIO_DAD01_v0.9.md);
- [02_EVIDENCIAS_Q5_Q8_SQL.txt](evidencias/02_EVIDENCIAS_Q5_Q8_SQL.txt);
- [03_INVESTIGACAO_DOCUMENTAL_TERRITORIAL.txt](evidencias/03_INVESTIGACAO_DOCUMENTAL_TERRITORIAL.txt).

A matriz, denominadores, sínteses territoriais, gates de segurança e SQL Q5–Q8 foram recuperados desses arquivos; a matriz documental INEP e as versões atuais da DAD-02 e DAD-05 também foram consultadas. Nenhum SQL foi executado e nenhum microdado foi processado nesta atualização. A reprodução SQL documentada permanece integral no [arquivo 02](evidencias/02_EVIDENCIAS_Q5_Q8_SQL.txt). Esse arquivo preserva o SQL relatado pelo executor, mas não comprova independentemente que cada trecho reproduzido tenha sido exatamente o executado. O material informa que a primeira tentativa de Q7 falhou por alias e a primeira de Q8 por capitalização de colunas; as versões corrigidas foram reportadas como usadas para produzir os resultados. Os SQLs exatos de Q1–Q4 não foram recuperados e não são reconstruídos aqui.

## 3. Ambiente e controles de segurança reportados

O registro da execução anterior informa que, antes das consultas, foram confirmados:

- current_user = sie_auditoria; rolsuper = false;
- SELECT nos três objetos autorizados: silver.infraestrutura_comum, gold.dim_entidade e gold.dim_municipio;
- ausência de privilégios efetivos de escrita nessas tabelas e de CREATE nos schemas silver e gold;
- transaction_read_only = on;
- timeout de conexão de 5 segundos e timeout de consulta de 20 segundos;
- uso exclusivo das variáveis SIE_AUDIT_*, sem acesso ao .env principal ou impressão de credenciais;
- transações explicitamente somente leitura.

O relatório v0.9 registra a branch develop durante a auditoria. Nesta consolidação, o branch foi lido como develop; o estado Git continha AGENTS.md, .codex/ e a pasta de evidências como não rastreados. Nenhum deles foi alterado. Não houve nesta sessão conexão ao banco ou nova consulta. Assim, os gates de execução SQL são **atestados pelos registros anteriores**, não revalidados operacionalmente nesta sessão.

## 4. Inventário dos 17 indicadores e situação documental

Os nomes são campos da Silver e os rótulos são operacionais da API segundo as evidências; não são apresentados como definições oficiais do INEP.

| Nº | Campo técnico | Rótulo operacional | Tipo reportado | 2022 | 2023 | 2024 | 2025 |
|---:|---|---|---|---|---|---|---|
| 1 | IN_AGUA_POTAVEL | Água potável | integer anulável | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 |
| 2 | IN_ENERGIA_REDE_PUBLICA | Energia (rede pública) | integer anulável | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 |
| 3 | IN_ESGOTO_REDE_PUBLICA | Esgoto (rede pública) | integer anulável | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 |
| 4 | IN_LIXO_SERVICO_COLETA | Coleta de lixo | integer anulável | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 |
| 5 | IN_BANHEIRO | Banheiro | integer anulável | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 |
| 6 | IN_BANHEIRO_PNE | Banheiro acessível (PNE) | integer anulável | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 |
| 7 | IN_BIBLIOTECA | Biblioteca | integer anulável | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 |
| 8 | IN_SALA_LEITURA | Sala de leitura | integer anulável | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 |
| 9 | IN_LABORATORIO_CIENCIAS | Laboratório de ciências | integer anulável | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 |
| 10 | IN_LABORATORIO_INFORMATICA | Laboratório de informática | integer anulável | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 |
| 11 | IN_SALA_MULTIUSO | Sala multiuso | integer anulável | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 |
| 12 | IN_SALA_ATENDIMENTO_ESPECIAL | Sala de atendimento especial | integer anulável | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 |
| 13 | IN_COZINHA | Cozinha | integer anulável | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 |
| 14 | IN_REFEITORIO | Refeitório | integer anulável | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 |
| 15 | IN_QUADRA_ESPORTES | Quadra de esportes | integer anulável | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 |
| 16 | IN_PATIO_COBERTO | Pátio coberto | integer anulável | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 |
| 17 | IN_AUDITORIO | Auditório | integer anulável | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 | Verificada via DAD-02 §3.1 |

Conforme a matriz documental registrada na DAD-02, para os 68 pares foram conferidos nome, descrição, tipo Num, domínio 0 = Não / 1 = Sim e marca de coleta anual. Continuam sem demonstração as regras operacionais de preenchimento, população aplicável, não resposta, não aplicabilidade e transformação até a Silver. A presença e os valores observados na Silver não provam, por si sós, essas regras.

## 5. Resultados empíricos Q1–Q8

### 5.1 Q1–Q2 — catálogo, estrutura e tipos

Segundo o relatório v0.9, a estrutura examinada de silver.infraestrutura_comum tinha 77 colunas (70 int4 e 7 textuais); os 17 indicadores eram inteiros anuláveis. Não foram identificadas restrições PK, UNIQUE ou FK nem índices no catálogo consultado. Isso descreve a estrutura reportada no recorte; não estabelece contratos de carga nem garante unicidade futura.

O catálogo de métricas foi associado a app/services/infraestrutura_service.py. A evidência Q5–Q8 cita a linha 21 e a investigação adicional aponta a lista operacional em torno da linha 25; numeração pode variar com revisão. Estrutura física não foi confundida com semântica oficial.

### 5.2 Q3–Q4 — universo, granularidade e denominadores

| Ano | Registros escola/ano | Escolas distintas | Municípios |
|---:|---:|---:|---:|
| 2022 | 3.583 | 3.583 | 22 |
| 2023 | 3.396 | 3.396 | 22 |
| 2024 | 3.393 | 3.393 | 22 |
| 2025 | 3.392 | 3.392 | 22 |
| **Total** | **13.764** | **3.771 distintas no período** | — |

Foi reportada uma linha por par (CO_ENTIDADE, NU_ANO_CENSO), sem duplicidade observada e sem nulos nos identificadores principais nas verificações anteriores. O professor esclareceu em 13/10/2026 que os 22 municípios observados constituem recorte intencional do projeto, associado à existência de bolsas nesses municípios. Não se classifica esse recorte, por si só, como erro de carga nem como cobertura de todo o Pará. Faltam a regra operacional exata, a lista/versão do recorte aplicada por ano e a documentação de como a condição de bolsas determinou a seleção. A redução de registros anuais não demonstra fechamento de escolas; sua causa não foi estabelecida.

### 5.3 Q5 — domínio e matriz quantitativa completa

Cada célula está na ordem **0 / 1 / NULL / inválido**. Denominadores por indicador: 3.583 (2022), 3.396 (2023), 3.393 (2024) e 3.392 (2025). Valores transcritos do registro de evidência Q5–Q8.

| Indicador | 2022 | 2023 | 2024 | 2025 |
|---|---:|---:|---:|---:|
| IN_AGUA_POTAVEL | 513 / 2.618 / 452 / 0 | 548 / 2.590 / 258 / 0 | 590 / 2.542 / 261 / 0 | 517 / 2.597 / 278 / 0 |
| IN_ENERGIA_REDE_PUBLICA | 610 / 2.521 / 452 / 0 | 600 / 2.538 / 258 / 0 | 593 / 2.539 / 261 / 0 | 574 / 2.540 / 278 / 0 |
| IN_ESGOTO_REDE_PUBLICA | 2.312 / 819 / 452 / 0 | 2.311 / 827 / 258 / 0 | 2.301 / 831 / 261 / 0 | 2.289 / 825 / 278 / 0 |
| IN_LIXO_SERVICO_COLETA | 1.323 / 1.808 / 452 / 0 | 1.310 / 1.828 / 258 / 0 | 1.266 / 1.866 / 261 / 0 | 1.197 / 1.917 / 278 / 0 |
| IN_BANHEIRO | 247 / 2.884 / 452 / 0 | 259 / 2.879 / 258 / 0 | 386 / 2.746 / 261 / 0 | 197 / 2.917 / 278 / 0 |
| IN_BANHEIRO_PNE | 1.872 / 1.259 / 452 / 0 | 1.811 / 1.327 / 258 / 0 | 1.756 / 1.376 / 261 / 0 | 1.647 / 1.467 / 278 / 0 |
| IN_BIBLIOTECA | 2.213 / 918 / 452 / 0 | 2.242 / 896 / 258 / 0 | 2.263 / 869 / 261 / 0 | 2.257 / 857 / 278 / 0 |
| IN_SALA_LEITURA | 2.283 / 848 / 452 / 0 | 2.233 / 905 / 258 / 0 | 2.201 / 931 / 261 / 0 | 2.145 / 969 / 278 / 0 |
| IN_LABORATORIO_CIENCIAS | 2.814 / 317 / 452 / 0 | 2.810 / 328 / 258 / 0 | 2.806 / 326 / 261 / 0 | 2.800 / 314 / 278 / 0 |
| IN_LABORATORIO_INFORMATICA | 2.403 / 728 / 452 / 0 | 2.414 / 724 / 258 / 0 | 2.429 / 703 / 261 / 0 | 2.461 / 653 / 278 / 0 |
| IN_SALA_MULTIUSO | 2.977 / 154 / 452 / 0 | 2.980 / 158 / 258 / 0 | 2.972 / 160 / 261 / 0 | 2.918 / 196 / 278 / 0 |
| IN_SALA_ATENDIMENTO_ESPECIAL | 2.256 / 875 / 452 / 0 | 2.231 / 907 / 258 / 0 | 2.171 / 961 / 261 / 0 | 2.056 / 1.058 / 278 / 0 |
| IN_COZINHA | 257 / 2.874 / 452 / 0 | 252 / 2.886 / 258 / 0 | 243 / 2.889 / 261 / 0 | 216 / 2.898 / 278 / 0 |
| IN_REFEITORIO | 2.012 / 1.119 / 452 / 0 | 1.947 / 1.191 / 258 / 0 | 1.856 / 1.276 / 261 / 0 | 1.719 / 1.395 / 278 / 0 |
| IN_QUADRA_ESPORTES | 2.212 / 919 / 452 / 0 | 2.198 / 940 / 258 / 0 | 2.185 / 947 / 261 / 0 | 2.132 / 982 / 278 / 0 |
| IN_PATIO_COBERTO | 1.474 / 1.657 / 452 / 0 | 1.417 / 1.721 / 258 / 0 | 1.376 / 1.756 / 261 / 0 | 1.297 / 1.817 / 278 / 0 |
| IN_AUDITORIO | 2.744 / 387 / 452 / 0 | 2.730 / 408 / 258 / 0 | 2.735 / 397 / 261 / 0 | 2.709 / 405 / 278 / 0 |

Nas 68 combinações foram reportados zero valores fora de {0,1,NULL}; a distribuição de valores inesperados é vazia. Trata-se do domínio **observado na Silver**, não do domínio oficial documentado.

### 5.4 Q6 — completude e denominadores

Os totais de nulos e válidos são iguais para os 17 indicadores dentro de cada ano. A tabela representa cada combinação indicador × ano. Denominador percentual: total de registros escola/ano do respectivo ano. Válido = 0 ou 1; inválido = não nulo e fora de 0/1.

| Ano | Denominador | NULL | NULL % | Válidos 0/1 | Válidos % | Inválidos | Inválidos % |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022 | 3.583 | 452 | 12,62% | 3.131 | 87,38% | 0 | 0% |
| 2023 | 3.396 | 258 | 7,60% | 3.138 | 92,40% | 0 | 0% |
| 2024 | 3.393 | 261 | 7,69% | 3.132 | 92,31% | 0 | 0% |
| 2025 | 3.392 | 278 | 8,20% | 3.114 | 91,80% | 0 | 0% |
| **Total** | **13.764** | **1.249** | **9,08%** | **12.515** | **90,92%** | **0** | **0%** |

Percentuais totais usam 13.764 registros. NULL não foi contado como zero.

### 5.5 Q7 — cobertura por escola/ano e painel

Denominador anual: grupos escola/ano, igual aos totais da seção 5.2. Somente duas classes foram observadas: zero ou 17 indicadores válidos. Cada classe de 1 a 16 teve frequência zero.

| Ano | Denominador | 0 válidos | 17 válidos | Pelo menos 14 | Menos de 14 | Sem válidos |
|---:|---:|---:|---:|---:|---:|---:|
| 2022 | 3.583 | 452 (12,62%) | 3.131 (87,38%) | 3.131 | 452 | 452 |
| 2023 | 3.396 | 258 (7,60%) | 3.138 (92,40%) | 3.138 | 258 | 258 |
| 2024 | 3.393 | 261 (7,69%) | 3.132 (92,31%) | 3.132 | 261 | 261 |
| 2025 | 3.392 | 278 (8,20%) | 3.114 (91,80%) | 3.114 | 278 | 278 |

O corte 14/17 (aproximadamente 80%) é apenas sensibilidade; não separa observações parciais neste conjunto e coincide com a classe de 17 válidos.

| Medida do painel 2022–2025 | Quantidade reportada |
|---|---:|
| Escolas com ao menos um ano observado | 3.771 |
| Presentes nos quatro anos | 3.178 |
| Presentes nos quatro anos e completos em todos | 2.892 |
| Presentes nos quatro anos com ao menos um ano sem indicadores válidos | 286 |
| Escolas com pelo menos um ano de zero indicadores válidos | 584 |
| Registros escola/ano completos | 12.515 |
| Registros escola/ano sem indicadores válidos | 1.249 |

**Implicação:** usar casos disponíveis por ano pode mudar a população comparada ao longo do tempo. A interseção de 2.892 escolas completas é uma alternativa de sensibilidade, não população homologada. As evidências não demonstram ausências aleatórias nem explicam a causa.

### 5.6 Q8 — integridade territorial e cardinalidade

| Verificação reportada | Resultado |
|---|---:|
| Chaves duplicadas em gold.dim_entidade por escola/ano | 0 |
| Chaves duplicadas em gold.dim_municipio por código | 0 |
| Correspondências exatas Silver–entidade por escola + ano | 3.771 |
| Silver sem correspondência exata escola + ano | 9.993 |
| Correspondências Silver–município por código | 13.764 |
| Órfãos de município | 0 |
| Multiplicação nos vínculos por código escolar e municipal | 0 reportada |
| Diferença de código municipal em pares exatos com entidade | 0 |
| Diferença de nome de escola em pares exatos | 3 linhas |
| Diferenças de nome municipal Silver–dimensão | 217 linhas |

Cobertura exata anual de gold.dim_entidade: 2022 = 219; 2023 = 52; 2024 = 108; 2025 = 3.392; total = 3.771. A dimensão tinha 3.771 linhas/escolas e dt_carga reportada como 01/07/2026. Todas as linhas Silver encontraram correspondência por código escolar no vínculo sem ano, sem multiplicação neste recorte; em 9.993 casos o ano cadastrado não coincide com o da Silver. Isso não demonstra finalidade histórica da dimensão.

**Divergências reportadas:**

- 213 linhas do código municipal 1504000: Silver “Limoeiro do Ajuru”; dimensão “Limoeiro do Ajurú”. O material cita referência do IBGE associando o código a Limoeiro do Ajuru; diferenças são compatíveis com acentuação, sem correção aplicada.
- 4 linhas com código 1501402 e nome “Ananindeua” na Silver, contra “Belém” na dimensão: uma em 2023 e três em 2024. A investigação cita o IBGE associando 1501402 a Belém e 1500800 a Ananindeua. Origem e campo prevalente não foram comprovados.
- Quatro escolas variam de código municipal:

| Código da escola | 2022 | 2023 | 2024 | 2025 |
|---|---:|---:|---:|---:|
| 15035557 | 1500800 | 1500800 | 1501402 | 1501402 |
| 15035620 | 1501402 | 1501402 | 1501402 | 1500800 |
| 15037991 | 1500800 | 1501402 | 1501402 | 1501402 |
| 15166031 | 1500800 | 1500800 | 1501402 | 1501402 |

As sequências não provam mudança administrativa legítima nem erro de identificação. O relatório complementar informa que em 2024 os quatro casos com 1501402 ainda traziam “Ananindeua”; em 2025 esse código aparece com “Belém”. Nenhuma correção automática foi feita.

**Risco de junção:** a dimensão municipal por código preservou cardinalidade reportada. Atributos de gold.dim_entidade ligados somente por ID podem pertencer a outro ano; com cobertura temporal desigual, não devem ser tratados como verdade histórica sem definição formal e validação.

## 6. Registros totalmente ausentes

| Ano | 17 campos NULL | Total anual (denominador) | Percentual |
|---:|---:|---:|---:|
| 2022 | 452 | 3.583 | 12,62% |
| 2023 | 258 | 3.396 | 7,60% |
| 2024 | 261 | 3.393 | 7,69% |
| 2025 | 278 | 3.392 | 8,20% |
| **Total** | **1.249** | **13.764** | **9,08%** |

Não foi reportada cobertura parcial: cada linha tem os 17 indicadores válidos ou os 17 nulos. Ausências aparecem em vários municípios. Exemplos: código 1500206, com 39, 39, 43 e 51 linhas ausentes entre 186, 188, 188 e 189 registros por ano; código 1503804, com 36, 36, 37 e 38 entre 84, 83, 83 e 82.

Foi reportada associação perfeita entre TP_LOCALIZACAO_DIFERENCIADA IS NULL e todos os 17 campos estarem NULL no conjunto examinado. É associação, não explicação causal; os materiais não distinguem condição de fonte, não resposta, não aplicabilidade, extração ou transformação. Nenhum registro foi recodificado ou excluído.

Linhas integralmente nulas por valor observado de TP_SITUACAO_FUNCIONAMENTO; legenda oficial não validada:

| Ano | Código 1 | Código 2 | Código 3 |
|---:|---:|---:|---:|
| 2022 | 134 | 269 | 49 |
| 2023 | 38 | 220 | 0 |
| 2024 | 72 | 189 | 0 |
| 2025 | 0 | 234 | 44 |

O relatório complementar também registra 5 linhas completas com código 2 em 2023 e 12 em 2024; a variável isoladamente não explica as ausências. Não se atribuiu semântica aos códigos sem documentação.

## 7. Proveniência e processo de transformação

### Evidência documental e código local

A matriz documental referenciada pela DAD-02 registra a origem INEP para os dicionários anuais do Censo Escolar e a comparação dos 17 indicadores. A DAD-02 documenta os atributos encontrados nos dicionários e suas referências por ano. Isso evidencia o conteúdo documental examinado, mas não vincula automaticamente cada coluna da Silver a uma coluna de microdados por um processo de transformação verificado.

No repositório disponível:

- app/models/infraestrutura.py declara o mapeamento de leitura da tabela silver.infraestrutura_comum e os campos consumidos pela API; não é o produtor da tabela.
- app/services/infraestrutura_service.py contém o catálogo e os rótulos operacionais das métricas.
- app/repositories/infraestrutura_repository.py lê a Silver; o score existente aplica COALESCE(col, 0), convertendo NULL em zero naquele caminho da API.
- docs/ARCHITECTURE.md descreve genericamente um pipeline externo do squad de dados via dbt, mas não identifica o modelo, job ou arquivo que produziu silver.infraestrutura_comum.

### Declarações do professor orientador recebidas em 13/10/2026

- Os dados usados pelo projeto têm origem nos microdados oficiais do Censo Escolar disponibilizados pelo INEP, na fonte pública indicada na seção 8.
- O ETL foi desenvolvido incrementalmente, sem documentação formal preservada; não há, até o momento, código original de carga identificado no repositório disponível.
- Os 22 municípios são um recorte intencional associado à existência de bolsas nesses municípios.
- Os 17 indicadores foram escolhidos porque estão presentes nos quatro anos; a consistência documental dos atributos indicados foi registrada na DAD-02.
- Segundo o professor, ele ou a equipe do projeto pode homologar os indicadores após apresentação e revisão dos resultados. Esta declaração identifica a instância que pode decidir; não é a própria decisão de homologação.

### Fluxo conhecido e limites

Proveniência conhecida por declaração e documentação: INEP → microdados oficiais do Censo Escolar → processamento original desenvolvido incrementalmente, sem documentação formal preservada → silver.infraestrutura_comum.

Não se declara que o ETL foi reconstruído, localizado, executado ou verificado. Permanecem desconhecidos os arquivos concretos de entrada usados nas cargas, versões, extrações e filtros, população selecionada, chaves e junções, transformações campo a campo, conversões de códigos, tratamento de ausências e cargas por ano. Não se atribui ao ETL uma transformação hipotética.

A associação reportada entre TP_LOCALIZACAO_DIFERENCIADA NULL e os 17 indicadores NULL continua sem explicação causal. Não é possível determinar, com a evidência atual, se ela decorre da fonte, de condição de preenchimento, aplicabilidade, não resposta, extração ou transformação. O diagnóstico quantitativo permanece na seção 6; qualquer causa adicional seria hipótese.

Para encerrar a DAD-01, a ausência do ETL original pode ser registrada como limitação aceita, desde que o professor/equipe revise seu impacto sobre as conclusões e registre formalmente essa decisão. A aceitação da limitação não transforma o fluxo incompleto em proveniência verificada.

## 8. Fontes oficiais e evidência documental

A fonte pública do INEP para os microdados do Censo Escolar é a página [Microdados do Censo Escolar](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar). A origem dos microdados efetivamente usados pelo projeto está registrada como esclarecimento do professor de 13/10/2026; não foi verificada nesta atualização por inspeção do ETL ou dos microdados.

A verificação documental dos dicionários oficiais de 2022, 2023, 2024 e 2025 está registrada na [matriz documental INEP 17 × 4](SIE_Matriz_Documental_INEP_17_Indicadores_2022_2025.md) e na [DAD-02, seção 3.1](DAD-02_MATRIZ_COMPARABILIDADE_TEMPORAL.md). A matriz registra 68/68 indicadores localizados, nomes e descrições idênticos, tipo Num, domínio 0 = Não / 1 = Sim e marca de coleta anual. A DAD-02 informa que o hash do arquivo de 2025 foi conferido localmente e que as fontes de 2022–2024 não estão disponíveis no checkout atual para recálculo independente. Não se solicita novamente a documentação já examinada; essa limitação é de reprodutibilidade dos artefatos neste checkout.

Os dicionários não demonstram instruções completas de preenchimento, restrições por tipo de escola, não resposta, não aplicabilidade ou o processamento da fonte para a tabela Silver. Esses elementos devem ser avaliados somente na medida em que possam alterar a interpretação dos indicadores. A homologação semântica continua dependente da revisão e decisão expressa do professor ou da equipe responsável.

Os materiais territoriais da DAD-01 citam referências do IBGE para 1501402, 1500800 e 1504000, mas não preservam cópia, versão ou página consultada. São achados reportados; a fonte territorial histórica e a regra de prevalência ainda precisam de registro para resolver as ocorrências que afetam identificação municipal.

## 9. Riscos metodológicos residuais

| Achado | Risco | Limite da evidência |
|---|---|---|
| Dicionários com nome, descrição, tipo Num, domínio 0/1 e coleta anual consistentes | A consistência de campos documentais pode não capturar diferenças nas instruções de preenchimento | Verificação registrada pela DAD-02; questionários e regras operacionais não foram integralmente revisados |
| 1.249 linhas com os 17 indicadores NULL | População e elegibilidade podem variar entre anos | Quantidade reportada; mecanismo e causa desconhecidos |
| Associação com TP_LOCALIZACAO_DIFERENCIADA NULL | Pode sinalizar mecanismo comum, sem provar causalidade | Associação reportada; não distingue fonte, aplicabilidade, não resposta ou ETL |
| ETL original sem documentação preservada | Transformações, seleção e tratamento de NULL não rastreáveis por código | Origem INEP declarada pelo professor; código/processo produtor não localizado nem verificado |
| COALESCE(NULL, 0) na API existente | Ausência vira valor zero no score daquele caminho | Achado estático documentado; não alterado nesta atualização |
| 22 municípios no recorte | Não representa automaticamente todos os municípios do Pará | Professor esclareceu que é recorte intencional ligado a bolsas; regra operacional precisa ser documentada |
| Divergências territoriais | Associação municipal anual pode alterar o grupo de referência | Variação legítima versus erro permanece sem decisão; nenhum ajuste automático |
| Sem restrição formal de unicidade reportada na Silver | Carga futura pode violar granularidade | Unicidade observada no recorte Q1–Q8; garantia de produção não demonstrada |
| Totais anuais decrescentes | Composição pode variar e afetar comparação | Não prova fechamento de escolas nem causa |

Continuam válidas as regras de interpretação: preservar 0, 1 e NULL como estados distintos; não calcular ausência como zero; manter denominadores; não interpretar o índice como qualidade escolar ou causalidade; e não tratar o recorte intencional de 22 municípios como abrangência estadual. A DAD-02 registra consistência documental dos 17 campos, mas a aprovação semântica formal e a escolha de S continuam pendentes.

## 10. Critérios mínimos de aceite da DAD-01

| Critério | Estado atualizado | Evidência ou ação para conclusão |
|---|---|---|
| Inventário de 17 campos e resultados empíricos Q1–Q8 | Atendido conforme resultados reportados | Pacote local DAD-01 e evidências Q5–Q8; não repetir validações nesta etapa. |
| Evidência documental anual dos 17 indicadores | **Verificada na DAD-02 para os 68 pares nos atributos examinados** | Nomes, descrições, tipo Num, domínio 0/1 e coleta anual. Reprodutibilidade local dos arquivos 2022–2024 permanece limitada conforme a DAD-02. |
| Regras semânticas operacionais | **Pendente de apreciação** | Professor/equipe deve revisar se questionários/manuais acrescentam condições de resposta, aplicabilidade, não resposta ou mudanças que alterem a interpretação; solicitar material adicional somente se essa revisão identificar lacuna relevante. |
| Origem da fonte e proveniência da Silver | **Parcialmente esclarecida; ETL não verificado** | Origem INEP/microdados é declaração do professor. O ETL incremental não tem documentação formal nem código original localizado. Registrar formalmente o impacto e a aceitação dessa limitação, ou fornecer evidência de produtor se existente. |
| Diagnóstico das 1.249 linhas integralmente nulas | Atendido como observação; causalidade pendente | Contagens e associação estão registradas. Explicação não deve ser inventada; professor/equipe deve aceitar formalmente a limitação ou apresentar evidência de fonte/processo que a esclareça. |
| Recorte de 22 municípios | **Intenção esclarecida; regra exata pendente** | Registrar lista/versão por ano, período de referência de bolsas e regra operacional pela qual o vínculo com bolsas determina inclusão. |
| Divergências territoriais | **Reportadas; decisões pendentes** | Registrar fonte oficial histórica e decisão para as quatro escolas com código variável e os quatro pares 1501402/“Ananindeua”; definir regra de nome para 1504000/acentuação. Preservar valores originais e não corrigir automaticamente. |
| Grão, unicidade e integridade da carga | Atendido como diagnóstico reportado, garantia não demonstrada | Q1–Q8 reportam unicidade no recorte; reconhecer ausência de constraint/contrato de carga e registrar aceite do risco ou controle do produtor se disponível. |
| Responsável e decisão de homologação | **Autoridade identificada; aprovação pendente** | O professor informou que ele ou a equipe pode homologar após apresentação/revisão. Registrar decisão expressa, data, escopo, limitações aceitas e indicadores aprovados/excluídos. |
| Parecer e escopo | **Atualizado sem homologar** | Manter NÃO HOMOLOGADA até registro da decisão anterior; preservar estados de DAD-02/DAD-05 e conclusão exploratória de DAD-03A/B/DAD-04. |

## 11. Parecer documental para apreciação do professor/equipe

**Parecer atual da DAD-01: NÃO HOMOLOGADA, aguardando decisão expressa.**

A evidência documental disponível sustenta que os 17 indicadores estão identificados nos dicionários oficiais dos quatro anos com nomes, descrições, tipos, domínio binário e marca de coleta anual consistentes, conforme registrado pela DAD-02. O critério de seleção informado pelo professor — presença nos quatro anos — justifica mantê-los como candidatos comuns. Essa evidência prepara a apreciação sem substituir a homologação semântica institucional.

A proveniência pode ser descrita até o nível conhecido: origem INEP declarada, microdados do Censo Escolar, processamento original incremental sem documentação preservada e tabela Silver consumida pela API. Não há evidência para afirmar quais filtros ou transformações foram aplicados. O diagnóstico das 1.249 observações NULL permanece observacional, sem causa atribuída. O recorte dos 22 municípios foi esclarecido como intencional e ligado a bolsas, mas seu critério operacional exato não foi registrado. Divergências territoriais podem afetar a associação por ano e ainda precisam de disposição documentada.

O professor esclareceu que ele ou a equipe do projeto pode homologar após apresentação e revisão. Até que essa revisão ocorra e seja registrada, a declaração de autoridade não é aprovação. Para fechar a DAD-01, recomenda-se que os responsáveis decidam expressamente: (a) se os dicionários bastam para a comparabilidade dos 17 candidatos ou se alguma instrução complementar é material; (b) se aceitam a limitação do ETL e dos nulos sem reconstrução; (c) qual regra operacional define os 22 municípios e como resolver ou aceitar cada divergência territorial; e (d) quais indicadores ficam aprovados para seguir à etapa decisória DAD-02.

Este parecer não homologa S, não declara os resultados oficiais e não autoriza publicação. A DAD-02 permanece preliminar e a DAD-05 permanece condicional. DAD-03A, DAD-03B e DAD-04 permanecem concluídas em seu escopo técnico exploratório; suas validações não foram repetidas.

## 12. Recomendações e restrições de uso

- Preservar NULL distinto de 0/1; não converter ausência em “Não”.
- Tratar COALESCE(col, 0) como comportamento de risco na API existente, não como regra metodológica validada.
- Não afirmar que o ETL foi reproduzido ou verificado; descrever sua ausência documental e a decisão de risco que for aprovada.
- Descrever os 22 municípios como recorte intencional ligado a bolsas somente com atribuição ao esclarecimento do professor; documentar a regra exata e não inferir cobertura estadual.
- Não corrigir códigos/nomes territoriais nem excluir registros sem decisão formal e trilha.
- Manter os 17 indicadores como candidatos comuns segundo o critério de presença em todos os anos até a decisão formal de comparabilidade e S.
- Preservar denominadores e distinções entre ausente, não observado, não aplicável e inválido quando houver evidência para classificá-los.
- Não interpretar resultados como qualidade escolar ou causalidade e não autorizar publicação oficial sem homologação.

As validações exploratórias da DAD-03A, DAD-03B e DAD-04 permanecem concluídas e não são reabertas por este documento.

## 13. Referências e trilha de auditoria

**Pacote local de evidências DAD-01:** [LEIA-ME.md](evidencias/LEIA-ME.md); [relatório v0.9](evidencias/01_RELATORIO_DAD01_v0.9.md); [matriz, denominadores e SQL Q5–Q8](evidencias/02_EVIDENCIAS_Q5_Q8_SQL.txt); [investigação documental e territorial](evidencias/03_INVESTIGACAO_DOCUMENTAL_TERRITORIAL.txt).

**Evidência documental atualizada:** [DAD-02 — Matriz de comparabilidade temporal](DAD-02_MATRIZ_COMPARABILIDADE_TEMPORAL.md), versão 0.2, seção 3.1; [matriz documental INEP 17 × 4](SIE_Matriz_Documental_INEP_17_Indicadores_2022_2025.md). A DAD-02 registra referências e hashes dos dicionários e explicita os limites de reprodutibilidade local para 2022–2024.

**Esclarecimentos da orientação:** recebidos em 13/10/2026, conforme os itens identificados nas seções 1, 5.2, 5.6, 7 e 11. São declarações atribuídas ao professor e não verificação independente do ETL.

**Artefatos locais de código consultados:** AGENTS.md (não alterado); docs/ARCHITECTURE.md; app/models/infraestrutura.py; app/services/infraestrutura_service.py; app/repositories/infraestrutura_repository.py; app/routes/infraestrutura.py. Eles demonstram leitura e uso na API, não o processo produtor da tabela Silver.

**Fonte oficial indicada:** INEP, [Microdados do Censo Escolar](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar). Os dicionários anuais e a inspeção documentada estão referenciados na DAD-02; esta atualização não baixou ou processou microdados. Referências territoriais do IBGE permanecem descritas no material de investigação sem cópia/versionamento/página suficiente para reprodução independente.

## 14. Continuidade: pendências essenciais e decisão de encerramento

### Evidências/decisões já obtidas nesta atualização

1. A DAD-02 incorporou as 68 verificações de dicionário para nome, descrição, tipo Num, domínio 0/1 e marca de coleta anual. Não solicitar novamente esses dicionários sem apontar uma lacuna concreta nas referências existentes.
2. O professor esclareceu a origem declarada dos dados, a ausência de ETL formal preservado, a intenção do recorte de 22 municípios, o critério de presença anual dos 17 indicadores e a autoridade que pode homologar.

### Pendências para encerramento da DAD-01

1. **Regra territorial operacional:** documentar a lista ou versão dos municípios considerada em cada ano, o período de referência das bolsas e a regra concreta que converte esse vínculo em seleção do recorte. A explicação de que o recorte é intencional está registrada, mas ainda não permite reproduzir a seleção.
2. **Disposição de divergências territoriais:** o professor/equipe deve decidir e registrar a regra de associação por ano e a fonte oficial histórica prevalente para (a) as quatro escolas com códigos municipais variáveis; (b) as quatro ocorrências do código 1501402 com nome “Ananindeua”; e (c) o nome de 1504000, “Limoeiro do Ajuru/Ajurú”. Para 1501402 e escolas variáveis, a decisão deve tratar do potencial efeito sobre a composição municipal; a acentuação de 1504000 pode ser tratada como regra de nome/display se confirmado que o código não está em disputa. Não efetuar correção automática.
3. **Aceitação formal da lacuna de ETL e dos nulos:** apresentar o fluxo conhecido e as limitações deste relatório; o professor/equipe deve aceitar o impacto de não haver código/documentação original e de não se conhecer a causa dos 1.249 casos NULL, ou fornecer evidência adicional existente. Não reconstruir ETL por hipótese e não atribuir causalidade a TP_LOCALIZACAO_DIFERENCIADA.
4. **Revisão semântica final:** professor/equipe deve revisar a DAD-02 e decidir se nomes, descrições, tipos, domínio e coleta anual dos dicionários bastam para aprovar comparabilidade dos 17 candidatos, ou indicar instrução complementar material. Manuais/questionários adicionais só devem ser solicitados se necessários para resolver uma ambiguidade identificada.
5. **Decisão formal de homologação:** registrar responsável (professor ou equipe), data, escopo, decisão por indicador ou grupo, limitações de ETL/ausência/território aceitas e condicionantes. A autoridade esclarecida pelo professor não é a própria aprovação.

### Critério para alterar o parecer

A DAD-01 poderá ser marcada como homologada somente após a apresentação e revisão acima e registro explícito da decisão dos responsáveis. A aprovação pode aceitar limitações documentais declaradas, mas deve especificar seu impacto e restringir as interpretações permitidas. Sem decisão formal, manter **NÃO HOMOLOGADA**.

A DAD-02 já está atualizada, mas continua preliminar até sua própria apreciação e decisão sobre o conjunto S. DAD-05 continua condicional. DAD-03A, DAD-03B e DAD-04 permanecem concluídas no escopo técnico exploratório e não são reabertas nesta continuidade.

---

**Controle desta atualização:** alterado exclusivamente este relatório para incorporar a matriz DAD-02 e os esclarecimentos do professor de 13/10/2026. Não houve SQL, processamento de microdados, alteração de código, banco, configuração, branch, commit ou push; os demais documentos DAD não foram modificados.
