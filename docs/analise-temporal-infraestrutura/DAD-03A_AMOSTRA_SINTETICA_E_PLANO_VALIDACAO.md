# SIE — DAD-03A | Amostra sintética e plano de validação

**Funcionalidade:** Análise Temporal de Infraestrutura — Escola × Município  
**Versão:** 0.1 — referência sintética para conferência manual  
**Status:** CONCLUÍDA — validação técnica com dados sintéticos; não constitui homologação metodológica nem validação empírica da API.
**Conjunto de exemplo:** \(S^* = \{A,B,C\}\), três indicadores binários fictícios

> \(S^*\) é apenas um conjunto didático de três indicadores. Não corresponde ao conjunto definitivo \(S\), não atribui nomes ou semântica oficial aos campos e não homologa nenhum indicador. Todos os anos, municípios, escolas e valores abaixo são fictícios. A DAD-01 permanece **NÃO HOMOLOGADA documentalmente**, a DAD-02 permanece preliminar, o conjunto \(S\) não está homologado e resultados definitivos não estão autorizados.

## 1. Objetivo e limitações

Este documento oferece casos pequenos, reproduzíveis e calculados manualmente para verificar a especificação condicional da DAD-05, independentemente da futura implementação da API. Os cenários testam denominadores, elegibilidade provisória, população de referência, exclusão da escola selecionada, diferenças em pontos percentuais, ausência, integridade e uso do município registrado no ano observado.

A DAD-03A não consulta PostgreSQL, executa SQL, seleciona escolas reais ou produz indicadores reais/oficiais; não testa código de produção, endpoint ou integração; não homologa \(S\), a política de cobertura completa, o aviso para \(N=1\) ou qualquer regra ainda pendente da DAD-05; não presume que os 22 municípios observados por ano representem todo o Pará; e não inicia DAD-04.

A recomendação provisória da DAD-05 é exigir cobertura completa para a escola selecionada e para as comparadoras da comparação principal. Nos cenários abaixo, “elegível*” significa elegível somente sob esse cenário condicional e sem bloqueio de integridade ou territorial. Não é autorização de publicação.

## 2. Referências metodológicas e convenções

Fonte metodológica primária: [DAD-05 — Contrato metodológico](DAD-05_CONTRATO_METODOLOGICO.md), especialmente as seções 2–8 sobre domínio, índice escolar, cobertura, exclusões metodológicas, integridade, referência e precisão.

Estados herdados:

- [DAD-01 — Auditoria e homologação](DAD-01_AUDITORIA_E_HOMOLOGACAO.md): parecer documental **NÃO HOMOLOGADA**; resultados empíricos são reportados, e há pendências de semântica, linhagem e território.
- [DAD-02 — Matriz de comparabilidade temporal](DAD-02_MATRIZ_COMPARABILIDADE_TEMPORAL.md): preliminar; 17 campos são candidatos, sem equivalência semântica documental confirmada.

Para toda escola \(e\), ano \(y\) e conjunto fictício \(S^*\), seja \(V_{e,y}\) o conjunto dos valores 0/1 e \(n_{e,y}=|V_{e,y}|\). Quando não há inválido e \(n_{e,y}>0\):

\[
I_{e,y}=100\times\frac{\sum_{i\in V_{e,y}}x_{i,e,y}}{n_{e,y}}.
\]

A cobertura do caso didático é \(n_{e,y}/|S^*|\). NULL não é zero, não entra no numerador e não entra no denominador. Um índice parcial pode ser matematicamente calculável, porém não é elegível à comparação principal pela recomendação provisória de cobertura completa.

Para escolas elegíveis do mesmo município e ano, excluindo a escola selecionada:

\[
N_{m,y,-e}=|\{j\in E_{m,y}:j\ne e\}|,
\qquad
R_{m,y,-e}=\frac{1}{N_{m,y,-e}}\sum_{j\in E_{m,y},\,j\ne e}I_{j,y}\quad(N>0),
\]

\[
\Delta_{e,y}=I_{e,y}-R_{m,y,-e}.
\]

A referência é média dos índices escolares, não proporção de todas as respostas agrupadas. Cálculos mantêm precisão sem arredondamento intermediário; arredondamento é somente de apresentação. Neste documento, frações exatas são prioritárias e dízimas com reticências indicam valores não arredondados.

Notação de entrada: vetor \([A,B,C]\); NULL é valor ausente; ∅ indica ausência de linha; INV(2) é um valor inválido deliberadamente sintético; DUP{...} indica mais de uma linha para a mesma chave escola/ano.

## 3. Matriz de casos sintéticos — dados de entrada

Em cada caso, a primeira escola é a selecionada. Os demais nomes identificam candidatos à referência; a elegibilidade é avaliada conforme a política condicional do caso.

| Caso | Ano / município fictício | Dados por escola para \(S^*=\{A,B,C\}\) |
|---|---|---|
| T01 — comparação completa | 2024 / M-A | X* [1,1,0]; Y [1,0,1]; Z [0,0,0] |
| T02 — índice selecionado 0% | 2022 / M-B | X* [0,0,0]; Y [1,0,0]; Z [0,0,0] |
| T03 — índice selecionado 100% | 2023 / M-C | X* [1,1,1]; Y [1,1,0]; Z [1,1,1] |
| T04 — parcial e NULL no denominador | 2024 / M-D | X* [1,NULL,0]; Y [1,0,1]; Z [0,0,0] |
| T05 — observada, todos NULL | 2024 / M-E | X* [NULL,NULL,NULL]; Y [1,0,1] |
| T06 — não observada | 2025 / município não atribuído à observação | Não existe linha de X* no ano; nenhum vetor ou município é inventado |
| T07 — N=0 após exclusões metodológicas | 2024 / M-F | X* [1,1,1]; Y [1,NULL,NULL]; Z [NULL,NULL,NULL]; cenário supõe regra de cobertura completa previamente autorizada apenas para este teste |
| T08 — uma comparadora | 2024 / M-G | X* [1,1,0]; Y [1,0,0] |
| T09 — inválido na selecionada | 2024 / M-H | X* [1,INV(2),0]; Y [1,0,0]; Z [0,0,0] |
| T10 — inválido em potencial comparadora | 2024 / M-I | X* [1,1,1]; Y [1,0,0]; Z [1,INV(2),0]; Z consta da lista de potenciais comparadoras antes da validação do valor |
| T11 — duplicidade da selecionada | 2024 / M-J | X* DUP{[1,1,1]; [0,0,0]}; Y [1,0,0] |
| T12 — duplicidade na referência | 2024 / M-K | X* [1,1,1]; Y [1,0,0]; Z DUP{[1,1,0]; [0,0,0]}; Z é potencial comparadora |
| T13A — exclusão metodológica | 2024 / M-L | X* [1,1,1]; Y [1,NULL,NULL]; Z [0,0,0]; cenário supõe regra completa previamente autorizada para demonstrar exclusão explícita de Y |
| T13B — integridade não é exclusão silenciosa | 2024 / M-L2 | X* [1,1,1]; Y [1,INV(2),0] consta do quadro de potenciais comparadoras; Z [0,0,0] |
| T14 — município do ano observado | 2022 / M-M; 2023 / M-N | X* em 2022 [1,1,1], código M-M; X* em 2023 [1,1,1], código M-N. Y [0,0,0] pertence a M-M/2022; Z [1,0,0] pertence a M-N/2023 |
| T15 — média dos índices versus respostas agrupadas | 2024 / M-O | X* [1,1,1]; P [1,NULL,NULL]; Q [0,0,0]; inclusão de P é cenário alternativo não homologado |

T07 e T13A são fixtures condicionais: supõem, somente para testar o efeito de exclusão metodológica já autorizada no cenário, que a regra completa tenha sido previamente aprovada. Isso não altera o estado real da DAD-05, em que essa regra continua provisória. Em T10 e T13B, a lista de potenciais comparadoras é declarada antes da validação para garantir que o problema de integridade não seja convertido automaticamente em exclusão.

## 4. Resultados esperados por caso

Em “n/3”, o numerador é a quantidade de indicadores válidos sobre três; cobertura é \(n/3\). Elegibilidade marcada com * vale somente sob a recomendação provisória de cobertura completa e sem bloqueio. “N indeterminado” significa bloqueio, não zero. “N —” significa que a comparação não foi executada, por exemplo porque a selecionada não é elegível.

| Caso | Selecionada: válidos; cobertura; índice | Elegibilidade provisória | Referência: escolas usadas; N; média | Diferença | Estado esperado e regra DAD-05 |
|---|---|---|---|---|---|
| T01 | X: 3/3; 100%; \(200/3=66,666\ldots\%\) | Sim* | Y, Z; 2; \(100/3=33,333\ldots\%\) | \(+100/3=+33,333\ldots\) pp | Disponível condicionalmente. Excluir X da própria referência; \(R\) é média dos índices escolares (seções 5 e 8). |
| T02 | X: 3/3; 100%; \(0\)% | Sim* | Y, Z; 2; \(50/3=16,666\ldots\%\) | \(-50/3=-16,666\ldots\) pp | Disponível condicionalmente; testa índice 0%, denominador completo e sinal da diferença (seções 3 e 5). |
| T03 | X: 3/3; 100%; \(100\)% | Sim* | Y, Z; 2; \(250/3=83,333\ldots\%\) | \(50/3=+16,666\ldots\) pp | Disponível condicionalmente; testa índice 100% e média da referência (seções 3 e 5). |
| T04 | X: 2/3; 66,666…%; \(100\times1/2=50\)% | Não para comparação principal* | —; —; não calculada | Indisponível | Índice matemático existe, mas selecionada parcial; NULL fora do denominador. Não comparar sob a recomendação completa (seções 3–4). |
| T05 | X: 0/3; 0%; indisponível | Não | —; —; não calculada | Indisponível | Linha observada sem indicador válido; distinta de T06; não imputar zero (seções 3–4 e 8). |
| T06 | X: não observado; cobertura não aplicável; indisponível | Não observado | —; —; não avaliada | Indisponível | Representar ausência temporal sem linha; não inventar município, zero, interpolação ou imputação (seções 4 e 8). |
| T07 | X: 3/3; 100%; \(100\)% | Sim* | Nenhuma após exclusões autorizadas no fixture; 0; indisponível | Indisponível | \(N=0\); referência e diferença nulas, motivo sem comparadoras. Exclusão metodológica declarada não bloqueia automaticamente (seções 5 e 8). |
| T08 | X: 3/3; 100%; \(200/3=66,666\ldots\%\) | Sim* | Y; 1; \(100/3=33,333\ldots\%\) | \(+100/3=+33,333\ldots\) pp | Referência calculável; aviso de comparadora única é proposta não homologada (seção 5). |
| T09 | X: 2/3 válidos; 66,666…%; índice bloqueado | Não | —; —; não calculada | Indisponível | Valor inválido na selecionada; não eliminar INV(2) para publicar 50%; sinalizar escola/ano/campo e bloquear (seções 3–4 e 8). |
| T10 | X: 3/3; 100%; \(100\)% | Sim* | Y é válida, mas grupo afetado por Z; N indeterminado; média bloqueada | Indisponível | Z é potencial comparadora com inválido. Não remover Z silenciosamente nem declarar \(N=1\); sinalizar integridade da referência (seções 4–5 e 8). |
| T11 | X: duplicada; n, cobertura e índice não consolidados | Não calculável | —; —; não calculada | Indisponível | Duplicidade na chave selecionada escola/ano; não escolher uma das linhas (seções 3–4 e 8). |
| T12 | X: 3/3; 100%; \(100\)% | Sim* | Y válida, mas grupo afetado por Z duplicada; N indeterminado; média bloqueada | Indisponível | Duplicidade em potencial comparadora; não escolher registro nem remover Z silenciosamente (seções 4–5 e 8). |
| T13A | X: 3/3; 100%; \(100\)% | Sim* | Z; 1; \(0\)% | \(+100\) pp | Y é excluída por critério metodológico explícito do fixture; essa exclusão rastreável não bloqueia Z. Aviso \(N=1\) ainda não homologado (seções 4–5 e 8). |
| T13B | X: 3/3; 100%; \(100\)% | Sim* | Z válida, mas grupo afetado por Y inválida; N indeterminado; média bloqueada | Indisponível | Contraste com T13A: Y integra o quadro de potenciais comparadoras e tem problema de integridade; não excluí-la silenciosamente como inelegibilidade (seções 4–5 e 8). |
| T14 — 2022 | X: 3/3; 100%; \(100\)% | Sim*, territorialmente sinalizada | Y em M-M/2022; 1; \(0\)% | \(+100\) pp | Usar código municipal da observação 2022; sinalizar mudança territorial e não publicar como definitivo (seções 5 e 8). |
| T14 — 2023 | X: 3/3; 100%; \(100\)% | Sim*, territorialmente sinalizada | Z em M-N/2023; 1; \(100/3=33,333\ldots\%\) | \(+200/3=+66,666\ldots\) pp | Usar código municipal da observação 2023; não substituir M-N por M-M nem agregar grupos dos dois anos (seções 5 e 8). |
| T15 — política principal | X: 3/3; 100%; \(100\)% | Sim* | Q; 1; \(0\)% | \(+100\) pp | P parcial é excluída se a regra completa vier a ser autorizada; referência usa Q (seções 4–5). |
| T15 — cenário alternativo | X: 3/3; 100%; \(100\)% | Sim* | P, Q; 2; \(50\)% | \(+50\) pp | Incluir P parcial altera a média; cenário não homologado (seções 4–5). |

### 4.1 Conferência dos valores das comparadoras

A tabela explicita, por candidata, quantidade válida, cobertura, índice matemático quando calculável e destino no cenário. Em T10/T13B, a lista de potenciais comparadoras é pré-declarada antes da validação dos indicadores como teste de integridade; isso não homologa inclusão de cobertura parcial na comparação principal. A interação entre esse teste e a futura política de elegibilidade deve ser decidida explicitamente.

| Caso | Escola candidata | Válidos; cobertura; índice | Destino no cenário |
|---|---|---|---|
| T01 | Y | 3/3; 100%; \(200/3\)% | Incluída |
| T01 | Z | 3/3; 100%; \(0\)% | Incluída |
| T02 | Y | 3/3; 100%; \(100/3\)% | Incluída |
| T02 | Z | 3/3; 100%; \(0\)% | Incluída |
| T03 | Y | 3/3; 100%; \(200/3\)% | Incluída |
| T03 | Z | 3/3; 100%; \(100\)% | Incluída |
| T04 | Y | 3/3; 100%; \(200/3\)% | Não usada: selecionada parcial |
| T04 | Z | 3/3; 100%; \(0\)% | Não usada: selecionada parcial |
| T05 | Y | 3/3; 100%; \(200/3\)% | Não usada: selecionada sem válidos |
| T07 | Y | 1/3; 33,333…%; \(100\)% matematicamente | Excluída pelo critério completo autorizado no fixture |
| T07 | Z | 0/3; 0%; índice indisponível | Excluída pelo critério completo autorizado no fixture |
| T08 | Y | 3/3; 100%; \(100/3\)% | Única incluída |
| T09 | Y | 3/3; 100%; \(100/3\)% | Não usada: selecionada inválida |
| T09 | Z | 3/3; 100%; \(0\)% | Não usada: selecionada inválida |
| T10 | Y | 3/3; 100%; \(100/3\)% | Válida, mas referência bloqueada pelo grupo afetado |
| T10 | Z | 2/3; 66,666…%; índice bloqueado por inválido | Potencial integrante; sinalizar e bloquear referência |
| T11 | Y | 3/3; 100%; \(100/3\)% | Não usada: selecionada duplicada |
| T12 | Y | 3/3; 100%; \(100/3\)% | Válida, mas referência bloqueada |
| T12 | Z, linha 1 | 3/3; 100%; \(200/3\)% isoladamente | Não escolher linha; chave duplicada |
| T12 | Z, linha 2 | 3/3; 100%; \(0\)% isoladamente | Não escolher linha; chave duplicada |
| T13A | Y | 1/3; 33,333…%; \(100\)% matematicamente | Excluída por regra metodológica declarada no fixture |
| T13A | Z | 3/3; 100%; \(0\)% | Única incluída |
| T13B | Y | 2/3; 66,666…%; índice bloqueado por inválido | Potencial integrante; sinalizar e bloquear referência |
| T13B | Z | 3/3; 100%; \(0\)% | Válida, mas referência bloqueada |
| T14 — 2022 | Y | 3/3; 100%; \(0\)% | Incluída em M-M/2022; alerta territorial herdado |
| T14 — 2023 | Z | 3/3; 100%; \(100/3\)% | Incluída em M-N/2023; alerta territorial herdado |
| T15 | P | 1/3; 33,333…%; \(100\)% matematicamente | Excluída no cenário principal; incluída somente no alternativo |
| T15 | Q | 3/3; 100%; \(0\)% | Incluída no cenário principal e no alternativo |

**Nota sobre T11 (selecionada X):** X possui duas linhas para a mesma chave escola/ano. Os índices de 100% e 0% são cálculos isolados de cada linha, não resultados válidos da escola; o índice consolidado de X permanece bloqueado por duplicidade.

Nas linhas duplicadas de Z em T12, os índices mostrados são apenas cálculos isolados de cada linha; não constituem índice válido da chave escola/ano, e a referência de T12 permanece bloqueada.

## 5. Cálculos manuais detalhados

### T01 — escola excluída da referência

- X: soma dos válidos = 2; denominador = 3; \(I_X=100\times2/3=200/3\)%.
- Y: \(100\times2/3=200/3\)%; Z: \(100\times0/3=0\)%.
- A referência usa somente Y e Z: \(R=(200/3+0)/2=100/3\)% e \(N=2\).
- Diferença: \(200/3-100/3=100/3\) pp. Se X fosse incluída, a referência mudaria; sua exclusão é requisito do contrato.

### T02 e T03 — extremos

- T02: X = \(0/3=0\)%; Y = \(1/3=100/3\)%; Z = \(0\)%. Logo \(R=(100/3+0)/2=50/3\)% e \(\Delta=0-50/3=-50/3\) pp.
- T03: X = \(3/3=100\)%; Y = \(2/3=200/3\)%; Z = \(3/3=100\)%. Logo \(R=(200/3+100)/2=250/3\)% e \(\Delta=100-250/3=50/3\) pp.

### T04 — NULL no denominador e cobertura parcial

- X tem dois valores válidos: soma = 1; denominador = 2.
- Índice matemático: \(100\times1/2=50\)%; cobertura: \(2/3\) = 66,666…%.
- Não se calcula comparação principal porque a selecionada não tem cobertura completa sob a recomendação provisória. NULL não reduz o resultado para \(100\times1/3\) e não vira zero.

### T07, T08 e T13 — contagem de comparadoras

- T07: depois das exclusões metodológicas autorizadas no fixture, \(E_{m,y}\) não contém outra escola; \(N=0\), então \(R\) e \(\Delta\) são indisponíveis, não zero.
- T08: a única comparadora tem \(I_Y=100/3\)%; portanto \(R=100/3\)%, \(N=1\) e \(\Delta=200/3-100/3=100/3\) pp.
- T13A: Y sai por critério metodológico explícito do fixture, mas Z permanece; \(N=1\), \(R=0\)% e \(\Delta=100\) pp. Não bloquear por uma exclusão legítima.
- T13B: Y não é excluída silenciosamente. Um inválido em potencial comparadora bloqueia a referência afetada na política fail-closed proposta. A contagem efetiva não é reportada como \(N=1\); fica indeterminada enquanto o problema estiver aberto.

### T14 — referência territorial por ano

- 2022: X em M-M tem \(100\)%; Y no mesmo município/ano tem \(0\)%. Assim \(N=1\), \(R=0\)% e \(\Delta=100\) pp.
- 2023: X em M-N tem \(100\)%; Z no mesmo município/ano tem \(100/3\)%. Assim \(N=1\), \(R=100/3\)% e \(\Delta=200/3\) pp.
- A mudança M-M → M-N é sinalizada. Os grupos anuais não se juntam, e a dimensão municipal atual não substitui o código da observação. A sinalização impede interpretação/publicação definitiva até tratamento territorial homologado.

### T15 — média dos índices versus respostas agrupadas

- P, parcial, tem índice matemático \(100\times1/1=100\)%; Q, completa, tem \(0\)%.
- No cenário alternativo de inclusão parcial, a média de índices escolares é \((100+0)/2=50\)%, com \(N=2\).
- Agrupando respostas válidas de P e Q, há 1 resposta 1 em 4 respostas válidas: \(1/4=25\)%. Isso não é a referência contratual, pois dá peso implícito diferente às escolas.
- Sob a recomendação principal de cobertura completa, P é excluída se o critério for aprovado: referência = Q = \(0\)%, \(N=1\), diferença de X = \(+100\) pp. A diferença entre 50% e 25% testa contra agregação indevida de respostas.

## 6. Casos de indisponibilidade e integridade

1. **Sem comparadoras legítimas (T07):** retornar referência e diferença indisponíveis com \(N=0\); não fabricar média zero. A exclusão só é legítima com critério metodológico previamente autorizado e registrado.
2. **Selecionada parcial ou sem dados (T04–T05):** manter eventual índice matemático parcial distinto de elegibilidade; sem indicador válido, não há índice. Não confundir esses estados.
3. **Não observada (T06):** inexistência de linha é ausência temporal, não observação com vetor nulo. Pode haver representação explícita de status, nunca interpolação ou imputação.
4. **Inválido na selecionada (T09):** bloquear índice e contraste; identificar escola, ano e campo. Um índice hipotético após descartar o inválido não é resultado.
5. **Inválido na referência (T10/T13B):** identificar escola/ano/campo, marcar referência afetada e não ocultar potencial comparadora para declarar \(N\), \(R\) ou \(\Delta\) definitivos.
6. **Duplicidade na selecionada ou referência (T11–T12):** não escolher registro por ordem, agregação ou conveniência. Bloquear índice ou referência afetada, sinalizar chave escola/ano e manter \(N\) não determinável se a composição não for segura.
7. **Exclusão legítima (T13A):** uma vez autorizada a política, escola inelegível não integra \(E_{m,y}\) e não bloqueia automaticamente as demais. Guardar a regra/versão de exclusão.
8. **Problema territorial (T14):** conservar associação anual e sinalizar. Não corrigir código/nome automaticamente, usar rótulo atual como histórico ou inferir abrangência estadual.

Os resultados empíricos citados pela DAD-01 não reportaram duplicidades nem valores fora do domínio no recorte auditado. São testes sintéticos para proteger cargas e casos futuros, não afirmação de ocorrência real.

## 7. Critérios de conferência manual

Para cada caso, a revisão independente deve:

1. Confirmar ano, município fictício, escola selecionada e vetor de entrada sem depender de endpoint ou código.
2. Contar valores válidos 0/1, NULL e inválidos separadamente; calcular \(n\) e cobertura com denominador \(|S^*|=3\).
3. Somar os valores 1 válidos e dividir por \(n\), preservando fração exata quando possível.
4. Aplicar a elegibilidade condicional declarada e distinguir exclusão metodológica de integridade.
5. Listar comparadoras do mesmo município/ano, excluir a selecionada e conferir \(N\) contra as escolas usadas.
6. Calcular cada índice escolar antes da média não ponderada.
7. Subtrair referência de índice selecionado e registrar sinal/unidade em pp.
8. Manter precisão nos intermediários e arredondar somente a apresentação.
9. Conferir estado/motivo: disponível condicional, parcial não elegível, sem válidos, não observada, sem comparadoras, integridade bloqueada ou território pendente.
10. Confirmar que ausência não virou zero, que não houve descarte sem regra e que nada foi publicado como definitivo.

As frações da seção 4 e as contas da seção 5 constituem a referência manual independente. Uma futura API/dashboard não deve definir os resultados esperados.

## 8. Plano determinístico para pequena amostra real futura

**Nenhuma escola real foi selecionada nesta DAD-03A.** A DAD-01 reportou 22 municípios por ano, 12.515 registros com os 17 campos válidos e 1.249 registros com os 17 campos NULL; os resultados também reportam registros completos e integralmente nulos em cada ano de 2022–2025. Isso informa a existência reportada dos estratos completo e all-NULL no recorte auditado, mas não autoriza nova consulta nem prova cobertura estadual.

Somente após revisão e autorização específica para DAD-03B, a amostra poderá ser construída sobre recorte de leitura autorizado e congelado (identificador/versão/data de extração registrados). Proposta determinística:

1. Fixar os quatro estratos anuais 2022, 2023, 2024 e 2025 e as classes de cobertura: completa (17 válidos) e integralmente nula (0 válidos), sem criar observações ausentes.
2. Para cada ano e classe disponível, ordenar candidatos por código municipal da própria observação e, como desempate estável, identificador da escola crescente. Selecionar o primeiro que maximize município ainda não representado; se todos já estiverem presentes, selecionar o primeiro da ordenação. Registrar a regra e a versão do recorte. Meta: até oito observações (uma por ano × classe), não uma amostra estatisticamente representativa.
3. Para cada escola completa selecionada, localizar no mesmo ano e município ao menos uma outra escola completa para conferir exclusão da selecionada e referência. Escolher comparadora por identificador estável crescente após aplicar critérios pré-fixados. Se não existir comparadora, registrar o caso sem substituição que esconda \(N=0\).
4. Acrescentar, sem duplicar observações já escolhidas, casos territoriais de revisão: uma observação determinística de escola com código municipal variável; uma ocorrência registrada para código 1501402/nome municipal divergente; e uma divergência nominal de Limoeiro do Ajuru, se acessíveis no recorte autorizado. Essa camada valida alertas, não corrige dados nem representa todas as divergências.
5. Se valores parciais, inválidos ou duplicados aparecerem na futura amostra, registrá-los segundo a regra de integridade; não forçar sua ocorrência. A DAD-01 não reportou casos parciais, inválidos ou duplicados no recorte, portanto permanecem cobertos sinteticamente.
6. Congelar a lista com chave escola/ano/código municipal e critérios usados para permitir reconstrução a partir do mesmo recorte. Não selecionar com base no valor do resultado, evitando cherry-picking.
7. Tratar a amostra como conferência de cálculo e fluxo, não estimativa representativa de escolas, municípios ou do Pará.

### Campos mínimos e cálculos da amostra real

Após autorização, a consulta/extração deve limitar-se ao necessário: identificador da escola; ano; código e nome municipal da observação; os 17 valores de indicadores; campos necessários para verificar grão/duplicidade; e proveniência do recorte. Não incluir dados pessoais ou variáveis sem necessidade. Para validar status territorial, registrar dimensões auxiliares autorizadas e sua cobertura, sem presumir que sejam históricas completas.

Conferir manualmente por escola completa: unicidade escola/ano; soma de 1s; denominador válido; índice sem arredondamento; comparadoras do mesmo ano/código municipal; exclusão da selecionada; N; índices individuais usados na média; referência; diferença em pp; estados e alertas. Para registro integralmente nulo: confirmar linha presente, \(n=0\), índice indisponível e não contribuição à referência, distinguindo-o da escola sem linha. Para divergência territorial: conferir código observado por ano e sinalização, sem correção automática.

## 9. Pendências e critérios de aceite da DAD-03A

### Pendências preservadas

- DAD-01 continua **NÃO HOMOLOGADA documentalmente**; faltam evidências oficiais e linhagem comprovada.
- DAD-02 continua preliminar; não há equivalência semântica confirmada.
- \(S\) continua não homologado; \(S^*\) serve exclusivamente para casos sintéticos.
- Cobertura completa segue recomendação provisória; limite de 80% não é regra.
- Aviso para \(N=1\) permanece proposta não homologada.
- A DAD-01 reportou 22 municípios por ano, sem provar representatividade estadual.
- Nenhum registro real foi selecionado e nenhum resultado definitivo está autorizado.

### Critérios objetivos de aceite

1. Há casos identificados para todos os 15 comportamentos solicitados, combinados apenas quando continuam interpretáveis.
2. Todo caso declara dados sintéticos, ano/município fictício, \(S^*\), papel da selecionada e comparadoras.
3. Cada cálculo válido informa n, cobertura, índice, escolas usadas, N, média e diferença; casos bloqueados distinguem indeterminado/não avaliado de zero.
4. NULL, todos NULL, não observado, inválido e duplicidade têm resultados distintos e nenhuma imputação ou escolha silenciosa.
5. T13A versus T13B distingue exclusão metodológica autorizada de problema de integridade.
6. A média dos índices individuais é contrastada com a proporção de respostas agrupadas.
7. Resultados fracionários foram recomputados independentemente; não houve arredondamento intermediário.
8. O plano real fixa universo, estratos, ordenação, desempate, campos mínimos e tratamento de categoria ausente, sem selecionar registros nesta etapa.
9. O documento não altera DAD-01/DAD-02/DAD-05, não homologa \(S\) e não declara resultado real.

## 10. Plano de leitura para DAD-03B

DAD-03B não está iniciada. Depois da revisão deste documento e de autorização específica, o trabalho de leitura poderá:

1. Confirmar o recorte/fonte de leitura autorizada e a chave escola/ano, sem restaurar backup ou ampliar permissões.
2. Obter somente registros e colunas mínimos definidos na seção 8, com leitura estrita e controles de segurança do projeto. Se SQL for necessário, solicitar autorização específica antes de executá-lo; esta DAD-03A não executa SQL.
3. Aplicar o algoritmo determinístico ao recorte fixado e documentar IDs/ano/município escolhidos em artefato autorizado.
4. Recalcular manualmente resultados de cada escola e comparadora, conferindo denominadores, integridade, território e exclusão da selecionada.
5. Separar evidência observada, decisão metodológica pendente e problema de integridade; não corrigir dados nem publicar resultados definitivos.
6. Interromper validação de resultados definitivos enquanto persistirem bloqueios da DAD-01 e ausência de \(S\) homologado.

## Referências

- [DAD-01 — Auditoria e homologação](DAD-01_AUDITORIA_E_HOMOLOGACAO.md).
- [DAD-02 — Matriz de comparabilidade temporal](DAD-02_MATRIZ_COMPARABILIDADE_TEMPORAL.md).
- [DAD-05 — Contrato metodológico](DAD-05_CONTRATO_METODOLOGICO.md).
- [Pacote de evidências DAD-01 — LEIA-ME](evidencias/LEIA-ME.md), para origem e limites dos resultados empíricos reportados.

**Controle de escopo:** documento sintético/plano criado sem consultas SQL, acesso ao PostgreSQL, seleção de escolas reais, mudanças em código/banco/configurações ou alterações em DAD-01, DAD-02, DAD-05 ou AGENTS.md. Nenhum commit ou push foi realizado. DAD-04 não foi iniciada.
