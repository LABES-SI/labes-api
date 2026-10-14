# SIE — DAD-05 | Contrato metodológico

**Funcionalidade:** Análise Temporal de Infraestrutura — Escola × Município  
**Versão:** 0.2 — atualização após esclarecimentos da orientação  
**Status:** contrato metodológico condicional; princípio da média aritmética aprovado expressamente; decisões complementares e homologação semântica pendentes  
**Dependências:** DAD-01 documentalmente **NÃO HOMOLOGADA**; DAD-02 preliminar; conjunto fixo de indicadores (S) não homologado.

> Este documento formaliza um contrato metodológico condicional. Não homologa os indicadores nem autoriza resultados definitivos. As DAD-03A, DAD-03B e DAD-04 estão concluídas no escopo técnico exploratório e não são reabertas. Os exemplos são inteiramente fictícios.

## 1. Contexto, escopo e estado das decisões

A funcionalidade compara o índice de disponibilidade de recursos de uma escola com a referência das demais escolas elegíveis do mesmo município e ano. O cálculo individual precede a referência municipal; as fórmulas desta versão preservam a média aritmética não ponderada dos índices individuais, a exclusão da escola selecionada e a diferença em pontos percentuais.

Em esclarecimento de 13/10/2026, o professor aprovou expressamente a utilização da média aritmética para a comparação Escola × Município. A aprovação registrada aqui alcança o princípio da média aritmética. Não amplia automaticamente a aprovação para definir a população de referência, a elegibilidade, a cobertura completa, exclusões, casos-limite, territorialidade ou publicação.

A DAD-01 versão 1.1 permanece **NÃO HOMOLOGADA**. A DAD-02 versão 0.2 registra 68 verificações documentais dos 17 indicadores candidatos entre 2022 e 2025: nomes, descrições, tipos, domínios e marcação de coleta anual. Essa consistência documental não é homologação semântica. O conjunto S continua candidato, sem aprovação formal.

As DAD-03A, DAD-03B e DAD-04 estão concluídas no escopo técnico exploratório. Seus testes e resultados são evidência de implementação e validação técnica, não decisão metodológica. A DAD-05 não reabre essas validações.

O contrato distingue: (1) calculabilidade matemática; (2) elegibilidade para comparação, definida por política aprovada; (3) validação técnica experimental, que cobre apenas os cenários exercitados; e (4) homologação metodológica e publicação, que dependem de decisões expressas dos responsáveis e dos bloqueios documentais aplicáveis.

O quadro de decisões da seção 10 registra separadamente regras expressamente aprovadas, regras implementadas e validadas experimentalmente, e regras ainda pendentes de aprovação formal.## 2. Notação e domínio

Sejam:

- (Y): anos da comparação, conforme a série que venha a ser homologada (a matriz preliminar cobre 2022–2025);
- (S): conjunto fixo, não vazio, versionado e comum aos anos comparados, após homologação;
- \(e\): escola selecionada; \(j\): escola candidata à referência;
- (y): ano da observação;
- (m(e,y)): município associado à escola na observação daquele ano;
- \(x_{i,e,y}\): valor do indicador \(i ∈ S\) para escola \(e\), ano \(y\).

Domínio tratado pelo método:

- `1`: resposta válida interpretada como presença do recurso, conforme a definição oficial a homologar;
- `0`: resposta válida interpretada como ausência do recurso, conforme a definição oficial a homologar;
- `NULL`: valor ausente, não convertido em 0 e não incluído no denominador;
- qualquer outro valor: inválido para esta especificação e sujeito à sinalização e bloqueio do cálculo afetado.

A interpretação de 0/1 depende da documentação oficial por ano. A notação matemática não comprova equivalência semântica entre anos.

## 3. Índice escolar: calculabilidade

Para uma observação escola/ano única e sem valor inválido entre os campos de (S), defina o conjunto de indicadores válidos:

\[
V_{e,y}=\{i\in S: x_{i,e,y}\in\{0,1\}\},
\qquad n_{e,y}=|V_{e,y}|.
\]

Se \(n_{e,y}>0\), o índice matematicamente calculável é:

\[
I_{e,y}=100\times\frac{\sum_{i\in V_{e,y}}x_{i,e,y}}{n_{e,y}}.
\]

Cada indicador válido tem peso igual. O denominador é \(n_{e,y}\), a quantidade de indicadores válidos — não o total de respostas esperadas quando houver `NULL`. Com dados completos, \(n_{e,y}=|S|\). Se \(n_{e,y}=0\), o índice é indisponível, não zero.

Um índice parcial pode ser matematicamente calculável, mas isso não o torna automaticamente elegível para comparação. A composição variável dos indicadores válidos pode reduzir a comparabilidade entre escolas e anos.

Se ocorrer valor inválido em qualquer campo de (S), a recomendação é bloquear o índice daquela observação escola/ano e sinalizar o problema; não eliminar o campo inválido do denominador, recodificá-lo ou escolher outra linha silenciosamente. A ocorrência de duplicidade escola/ano também bloqueia o cálculo até resolução documentada.

## 4. Elegibilidade para comparação

### 4.1 Regra proposta para a comparação principal

Recomenda-se, **provisoriamente e sem homologação**, exigir cobertura completa de \(S\) para a escola selecionada e para as escolas usadas na referência. Essa restrição oferece uma composição uniforme de indicadores na comparação principal, mas não substitui a comprovação semântica dos campos nem resolve os bloqueios da DAD-01.

Uma observação com cobertura parcial pode ter índice calculável pela fórmula da seção 3. Pela proposta conservadora, não entra na comparação principal enquanto a regra de cobertura parcial não for homologada. A análise de sensibilidade com limite de 80% permanece apenas cenário: para 17 indicadores, corresponderia a pelo menos 14 válidos, mas não é critério aprovado nem requisito definitivo.

### 4.2 Exclusões metodológicas versus problemas de integridade

Uma **exclusão metodológica** é a retirada de uma escola por critério de população previamente definido, documentado e aprovado — por exemplo, a regra de cobertura completa, se vier a ser homologada. Uma escola que seja legitimamente inelegível segundo tal regra não bloqueia automaticamente a referência municipal; sua exclusão deve ser rastreável e aplicada consistentemente.

Um **problema de integridade** não é uma exclusão metodológica. Valor inválido ou duplicidade escola/ano envolvendo escola que poderia integrar a comparação deve ser sinalizado. Não se pode remover silenciosamente essa escola para fazer a referência parecer válida. A política explícita deverá determinar a extensão do bloqueio; a recomendação deste contrato é bloquear a referência afetada quando não for possível determinar com segurança a contribuição da população elegível. O problema deve indicar escola, ano, tipo de ocorrência e se afeta o índice selecionado, a referência municipal ou ambos, sem escolher arbitrariamente uma linha.

Enquanto a regra de elegibilidade ainda não for homologada, não se deve tratar a recomendação de cobertura completa como autorização para exclusões definitivas ou publicação.

### 4.3 Situações individuais

- **Completa:** índice calculável e, se os demais requisitos forem atendidos, potencialmente elegível à comparação principal.
- **Parcial:** índice matematicamente calculável se \(n_{e,y}>0\); elegibilidade de comparação pendente, com recomendação provisória de não inclusão na comparação principal.
- **Observada sem indicadores válidos:** há linha escola/ano, \(n_{e,y}=0\), índice indisponível; não é zero e não contribui à referência.
- **Não observada:** não há linha escola/ano. Pode ser representada explicitamente como ausência temporal (`nao_observada`), mas não se cria observação nem se interpola ou imputa valor.
- **Inválida ou duplicada:** sinalizar e bloquear o cálculo afetado, sem recodificação, escolha arbitrária ou exclusão silenciosa.
- **Escola com município variável:** associar cada observação ao código municipal registrado para aquele ano; não propagar código atual para anos anteriores. Ocorrências territoriais documentadas exigem sinalização e política aprovada antes de publicar contrastes afetados.

## 5. Referência municipal e diferença

Seja \(E_{m,y}\) a população de escolas elegíveis para o ano \(y\) e município \(m\), definida por política metodológica previamente aprovada. Para a escola selecionada \(e\), use \(m=m(e,y)\) e exclua (e) explicitamente:

\[
N_{m,y,-e}=|\{j\in E_{m,y}:j\ne e\}|.
\]

Quando \(N_{m,y,-e}>0\), a referência é a média aritmética dos índices individuais das demais escolas elegíveis:

\[
R_{m,y,-e}=\frac{1}{N_{m,y,-e}}
\sum_{\substack{j\in E_{m,y}\\j\ne e}}I_{j,y}.
\]

Cada escola comparadora tem peso igual, independentemente da quantidade de respostas válidas que teria sob uma política de cobertura parcial. Não se deve agrupar respostas individuais de todas as escolas para formar uma proporção municipal. (N) registra o número efetivo de outras escolas usadas no denominador.

A diferença é:

\[
\Delta_{e,y}=I_{e,y}-R_{m,y,-e}.
\]

Como os índices estão na escala percentual 0–100, \(Δ\) é reportada em pontos percentuais (pp). Diferença positiva indica índice escolar acima da referência calculada; negativa, abaixo. Isso não representa avaliação de qualidade escolar.

Se \(N=0\), a referência e a diferença são indisponíveis (`NULL`), com motivo “sem comparadoras”; o índice próprio pode continuar disponível. Se \(N=1\), a média é matematicamente definida. **Exibir com aviso de comparadora única** é uma proposta ainda não homologada; eventual supressão depende de regra aprovada.

Exclusões metodológicas autorizadas são aplicadas antes de formar \(E_{m,y}\) e, quando corretamente definidas, não bloqueiam por si sós o cálculo. Problemas de integridade em potenciais integrantes não são tratados como exclusões. Valor inválido ou duplicidade que impeça conhecer a composição/contribuição do grupo deve ser sinalizado e pode bloquear a referência afetada conforme política explícita; a recomendação é não publicar uma referência afetada sem resolução ou regra aprovada que justifique o tratamento.

## 6. Precisão numérica e apresentação

Os cálculos devem preservar precisão numérica durante a soma, divisão, média municipal e subtração. Não arredondar índices escolares antes de calcular a referência nem arredondar a referência antes de calcular a diferença. Arredondamento ocorre apenas na apresentação; a quantidade de casas exibidas deverá ser definida na especificação de apresentação. Contagens \(n_{e,y}\) e \(N_{m,y,-e}\) são inteiras e não arredondadas.

Os exemplos abaixo mostram resultados com reticências para indicar valores não arredondados internamente; valores com duas casas aparecem somente como ilustração de exibição.

## 7. Exemplos fictícios reproduzíveis

Os exemplos são sintéticos, não representam escolas, municípios ou valores reais do SIE. Para cálculo manual, considere (S=\{A,B,C\}), com pesos iguais.

### 7.1 Escola selecionada completa e comparadoras completas

| Escola fictícia | A | B | C | Situação | Índice matemático |
|---|---:|---:|---:|---|---:|
| Selecionada X | 1 | 1 | 0 | Completa | \(100\times2/3=66,666\ldots\%\) |
| Comparadora Y | 1 | 0 | 1 | Completa | \(100\times2/3=66,666\ldots\%\) |
| Comparadora Z | 0 | 0 | 0 | Completa | \(0\%\) |
| Escola P | 1 | `NULL` | `NULL` | Parcial | \(100\times1/1=100\%\), parcial, parcial |

**Comparação principal sob a recomendação provisória de cobertura completa:** P não integra \(E\), caso esse critério venha a ser aprovado. A referência de X usa Y e Z:

\[
R_{-X}=\frac{66,666\ldots+0}{2}=33,333\ldots\%,\quad N=2,
\]

\[
\Delta_X=66,666\ldots-33,333\ldots=+33,333\ldots\text{ pp}.
\]

**Cenário alternativo de sensibilidade — incluir P, ainda não homologado:**

\[
R^{alt}_{-X}=\frac{66,666\ldots+0+100}{3}=55,555\ldots\%,\quad N=3,
\]

\[
\Delta^{alt}_X=66,666\ldots-55,555\ldots=+11,111\ldots\text{ pp}.
\]

Os valores exibidos, arredondados apenas para ilustração, seriam respectivamente \(33,33\%\\) e \(+33,33\\) pp no cenário principal, e \(55,56\%\\) e \(+11,11\\) pp no cenário alternativo. P tem índice matematicamente calculável, mas sua inclusão muda a referência; o cenário alternativo não é regra aprovada.

### 7.2 Efeito de `NULL` no denominador

Para valores fictícios ((1,\text{NULL},0)), há dois indicadores válidos:

\[
I=100\times(1+0)/2=50\%.
\]

O `NULL` não é convertido em zero; por isso o denominador é 2, não 3. A elegibilidade dessa observação parcial para comparação continua sujeita à regra aprovada.

### 7.3 Sem outras escolas de referência

Uma escola fictícia W com \((1,1,0)\) tem índice calculável \(66,666\ldots\%\). Se não houver outras escolas elegíveis no mesmo município/ano, (N=0); referência e diferença ficam indisponíveis, com motivo “sem comparadoras”. Não se atribui média zero.

### 7.4 Uma única comparadora

Se a escola selecionada tiver proporção fictícia \(2/3\), seu índice será \(100\times2/3=66,666\ldots\%\). Uma única comparadora elegível com proporção \(1/3\) terá índice \(100\times1/3=33,333\ldots\%\). Assim, \(N=1\), a referência é \(33,333\ldots\%\) e a diferença é \(+33,333\ldots\) pp. Exibir com aviso é a proposta não homologada; o número não deve ocultar que a referência depende de uma única escola.

### 7.5 Inválido, duplicidade e escola não observada

- Valores fictícios \((1,2,0)\): o valor 2 é inválido; bloquear o índice afetado e sinalizar, sem removê-lo para calcular \(50\%\).
- Duas linhas para a mesma chave escola/ano: bloquear cálculo da observação. Se essa escola puder integrar a referência, sinalizar a referência municipal afetada; não escolher uma das linhas.
- Nenhuma linha de uma escola num ano: representar `nao_observada`. Não confundir com uma linha existente cujos indicadores são todos `NULL` (`observada_sem_indicadores_validos`). Não interpolar nem imputar qualquer dos casos.

## 8. Casos-limite e sinalização

| Situação | Índice selecionado | Referência/diferença | Sinalização conceitual |
|---|---|---|---|
| \(n=0\), linha observada | Indisponível | Não contribui à referência | `observada_sem_indicadores_validos` |
| Escola sem linha no ano | Não calculado | Não aplicável para essa escola | `nao_observada` |
| \(N=0\) | Pode estar disponível | Indisponíveis | `sem_comparadoras` |
| \(N=1\) | Pode estar disponível | Calculáveis; aviso proposto | `comparadora_unica` |
| Valor inválido na escola selecionada | Bloqueado | Diferença também bloqueada | `entrada_invalida` + escola/ano/campo |
| Valor inválido em potencial comparadora | Pode estar disponível | Referência afetada deve ser sinalizada e tratada por política explícita; recomendação: bloquear se composição não puder ser determinada | `integridade_referencia` + escola/ano/campo |
| Duplicidade na escola selecionada | Bloqueado | Diferença bloqueada | `duplicidade_escola_ano` + chave |
| Duplicidade em potencial comparadora | Pode estar disponível | Referência afetada deve ser sinalizada e tratada por política explícita; recomendação: bloquear até resolução | `duplicidade_referencia` + chave |
| Inelegibilidade conforme critério metodológico aprovado | Calculável ou não, conforme dados | Excluída explicitamente de (E); não bloqueia automaticamente | `exclusao_metodologica` + regra/versão |
| Território sob revisão | Pode existir | Contraste municipal deve ser sinalizado; publicação depende de política aprovada | `territorio_pendente` |

O sinalizador de integridade deve identificar o escopo do impacto — índice individual, composição da referência ou ambos — e não expor um valor como válido quando o cálculo foi bloqueado. Uma política futura pode definir resolução documentada para certos casos; até lá, não se exclui silenciosamente uma potencial comparadora para produzir resultado.

## 9. Contrato conceitual de saída

Os campos a seguir são conceituais; não definem endpoint, esquema físico ou implementação:

| Campo conceitual | Conteúdo |
|---|---|
| `school_id` | Identificador da escola consultada |
| `municipality_code_reference` | Código municipal associado à observação daquele ano |
| `municipality_name_display` | Nome para exibição com proveniência; não substitui o código como chave |
| `year` | Ano da observação |
| `school_index_pct` | Índice escolar, nulo quando indisponível/bloqueado |
| `municipal_mean_excluding_school_pct` | Média dos índices das outras escolas efetivamente usadas |
| `difference_pp` | Índice escolar menos referência municipal, em pontos percentuais |
| `n_valid_indicators` | \(n_{e,y}\), número de indicadores válidos na escola selecionada |
| `n_selected_indicators` | (|S|), número de indicadores do conjunto versionado |
| `n_comparable_schools` | \(N_{m,y,-e}\), outras escolas efetivamente incluídas na referência |
| `index_status` | Estado de cálculo/observação, como `complete`, `partial`, `observada_sem_indicadores_validos`, `nao_observada`, `entrada_invalida` ou `duplicidade_escola_ano` |
| `reference_status` | Estado da referência, como `available`, `sem_comparadoras`, `comparadora_unica`, `integridade_referencia` ou `territorio_pendente` |
| `unavailability_reason` | Motivo explícito quando índice, referência ou diferença estiverem indisponíveis |
| `methodology_version` | Versão do contrato metodológico aplicado |
| `indicator_set_version` | Identificador/versão de (S); não deve sugerir homologação enquanto pendente |

Estados e nomes são propostas de contrato, não implementação. A saída temporal pode explicitar que uma escola não foi observada em determinado ano sem inventar score ou comparação para completar uma série.

## 10. Quadro de decisões metodológicas

### 10.1 Aprovada expressamente pelo professor

| Regra | Evidência e limite da aprovação |
|---|---|
| Utilização da média aritmética na comparação Escola × Município | Esclarecimento do professor orientador em 13/10/2026. A especificação operacional preservada neste contrato é a média aritmética não ponderada dos índices individuais das demais escolas elegíveis. A aprovação do princípio não decide quem é elegível nem quais exclusões formam a população. |

### 10.2 Implementadas e validadas tecnicamente em escopo experimental

| Regra/comportamento | Evidência técnica | Limite |
|---|---|---|
| Índice individual pela proporção de respostas 1 entre os indicadores válidos, na escala percentual 0–100 | Casos sintéticos e conferência independente dos valores brutos reportados na DAD-03B; frações exatas preservadas | O uso do conjunto S depende de homologação semântica. |
| Média dos índices individuais das comparadoras e diferença índice escolar menos referência | Implementado na rota experimental; DAD-03B e DAD-04 reportam conferência/concordância dos quatro anos | População elegível e exclusões permanecem decisões do contrato. |
| Exclusão da escola selecionada da própria referência | Implementada e exercitada nos cenários sintéticos e na comparação experimental | Não há evidência de aprovação expressa separada pelo professor; requer confirmação formal. |
| NULL distinto de zero; valores ausentes não entram no denominador de uma fração parcial | Coberto por exemplos e testes experimentais | O significado de ausência e eventual não aplicabilidade na fonte não foi homologado. |
| N=0 sem referência/diferença numéricas; N=1 com cálculo matematicamente definido | Comportamentos exercitados nos testes | Aviso, supressão ou apresentação de N=1 ainda requer decisão. |
| Bloqueio de cálculo afetado por valor inválido ou duplicidade; sinalização e preservação de evidência | Testes sintéticos e validação local do exportador DAD-03B | Política final de resolução e extensão do bloqueio requer aprovação formal. |
| Município associado à observação do próprio ano e alerta para variação territorial | Implementado/exercitado na rota experimental da DAD-04 | Disposição das divergências reais identificadas na DAD-01 continua pendente. |
| Precisão exata, sem arredondamento intermediário; diferença em pontos percentuais | Conferência matemática independente reportada na DAD-03B e conciliação experimental da DAD-04 | Número de casas e formato final de exibição ainda não foram definidos. |
| Estado experimental não homologado e bloqueio de alegação de publicação oficial | Presente na rota/status e nos relatórios DAD-03B/DAD-04 | Publicação depende de homologação metodológica e documental. |

### 10.3 Pendente de aprovação formal: regras e perguntas para apreciação

| Regra | Estado atual | Pergunta objetiva ao professor/equipe |
|---|---|---|
| Média não ponderada dos índices individuais | Princípio aprovado; fórmula operacional documentada e validada experimentalmente | Confirma-se que a aprovação se limita ao princípio da média não ponderada dos índices por escola, deixando elegibilidade e composição da população para decisões próprias? |
| Exclusão da escola selecionada | Implementada e validada experimentalmente; aprovação expressa separada não documentada | A escola selecionada deve ser sempre excluída da referência do mesmo município e ano? |
| Elegibilidade e cobertura completa dos 17 indicadores | Cobertura completa é perfil experimental condicional | A comparação principal exigirá 17/17 valores válidos tanto para a escola selecionada como para cada comparadora? Como tratar observações parciais? |
| NULL e não aplicabilidade | NULL não é zero; causa e semântica de não aplicabilidade não estabelecidas | Há distinção documentada entre não resposta, não aplicabilidade e ausência de dado? Quais estados entram no índice ou são excluídos? |
| N=0 e N=1 | N=0 produz referência indisponível; N=1 é calculável e foi exercitado | Com N=0, deve-se apenas informar indisponibilidade? Com N=1, apresentar com aviso, suprimir ou aplicar outra regra? |
| Duplicidades e valores inválidos | Bloqueio fail-closed implementado nos cenários cobertos | Todo inválido ou duplicidade em potencial comparadora deve bloquear a referência municipal/ano até resolução? Quais resoluções documentadas serão permitidas? |
| Mudanças territoriais entre anos | Código anual preservado e alerta experimental | Deve prevalecer o código municipal registrado em cada observação anual? Qual decisão se aplica às divergências específicas da DAD-01? |
| Precisão, arredondamento e apresentação | Precisão integral preservada nos cálculos; sem arredondamento intermediário | Quantas casas decimais e qual formato usar apenas na exibição? |
| Condições para homologação e publicação | S e regras complementares sem homologação; publicação oficial não autorizada | Quais decisões documentais e metodológicas são gates obrigatórios para homologar S, aprovar a DAD-05 e autorizar publicação? |

O professor esclareceu em 13/10/2026 que ele próprio ou a equipe do projeto pode homologar os indicadores após apresentação e revisão. Essa atribuição identifica os responsáveis aptos a decidir; não é homologação automática, não aprova todas as regras deste contrato e não autoriza publicação.

### 10.4 Bloqueios documentais e institucionais

- **DAD-01:** permanece **NÃO HOMOLOGADA**. A versão 1.1 registra origem INEP declarada, processamento original sem documentação formal preservada, 1.249 linhas integralmente nulas sem causa comprovada, recorte intencional de 22 municípios cuja regra exata falta e divergências territoriais a decidir.
- **DAD-02:** matriz preliminar com 68 verificações documentais. Os atributos examinados são consistentes conforme a matriz; a homologação semântica de S continua pendente.
- **Conjunto S:** os 17 indicadores são candidatos por presença nos quatro anos; não formam conjunto definitivamente homologado.
- **População de referência:** a intenção territorial de 22 municípios associada a bolsas foi esclarecida, mas sua regra operacional e as ocorrências territoriais ainda não foram decididas.
- **Publicação oficial:** não autorizada enquanto faltarem as homologações e decisões aplicáveis. A conclusão técnica exploratória das DAD-03A/B e DAD-04 não remove esses gates.

## 11. Registro da decisão e critérios de aceite

A decisão final do professor ou da equipe deverá registrar, no mínimo:

1. responsável pela decisão (professor ou equipe identificada);
2. data da revisão;
3. escopo aprovado: versão do contrato, período, conjunto de indicadores e finalidade;
4. decisão explícita para cada regra da seção 10.3, incluindo aprovação, rejeição ou condição;
5. limitações aceitas e impacto permitido na interpretação, incluindo proveniência/ETL, ausências e territorialidade quando aplicáveis;
6. tratamento aprovado para divergências e exceções, sem alteração silenciosa de dados;
7. estado de homologação da DAD-01, DAD-02, conjunto S e DAD-05;
8. autorização ou vedação expressa de publicação e seus limites.

Critérios para considerar a DAD-05 metodologicamente encerrada:

- o conjunto S e sua comparabilidade foram formalmente deliberados;
- população de referência, cobertura/elegibilidade e exclusões estão definidas;
- NULL, não aplicabilidade, N=0/N=1, duplicidades, inválidos e variação territorial têm política aprovada;
- precisão e apresentação foram aprovadas, preservando os cálculos internos sem arredondamento intermediário;
- bloqueios da DAD-01 foram resolvidos ou aceitos formalmente com limitações e escopo explícitos;
- a decisão final tem responsável, data e escopo registrados.

As DAD-03A, DAD-03B e DAD-04 podem ser referenciadas como evidência técnica nos cenários exercitados. Isso não substitui os critérios acima nem exige repetir suas validações nesta atualização.

## 12. Parecer técnico atualizado

**DAD-05: CONTRATO METODOLÓGICO CONDICIONAL — NÃO HOMOLOGADO.**

O princípio de utilizar média aritmética na comparação Escola × Município foi aprovado expressamente pelo professor orientador em 13/10/2026. Permanecem inalteradas as fórmulas: índice individual na escala percentual, média não ponderada dos índices individuais das demais escolas elegíveis, exclusão da escola consultada, diferença em pontos percentuais e ausência de arredondamento intermediário.

A implementação experimental e as validações das DAD-03A, DAD-03B e DAD-04 demonstram comportamento nos casos sintéticos e no escopo empírico reportado. Isso comprova validação técnica nos cenários cobertos, sem homologar elegibilidade, cobertura completa, tratamento de não aplicabilidade, regras de N, integridade, política territorial ou apresentação final.

A homologação semântica de S, as decisões complementares listadas neste contrato e a autorização de publicação permanecem pendentes. DAD-01 continua **NÃO HOMOLOGADA**; DAD-02 permanece preliminar; DAD-03A, DAD-03B e DAD-04 continuam concluídas no escopo técnico exploratório, sem reabertura nesta atualização. Nenhum resultado é declarado oficial.

## 13. Continuidade do projeto e estado das cinco DADs

| DAD | Estado registrado | Pendência para avanço/encerramento |
|---|---|---|
| DAD-01 | **NÃO HOMOLOGADA** | Revisão/decisão formal; aceite ou evidência adicional para ETL e nulos; regra e decisões territoriais; critério operacional do recorte de 22 municípios. |
| DAD-02 | **Matriz preliminar; 68 verificações documentais registradas** | Deliberação semântica formal sobre o conjunto S; avaliar material adicional somente se surgir lacuna interpretativa concreta. |
| DAD-03A | Concluída no escopo sintético e de planejamento | Nenhuma reabertura proposta. |
| DAD-03B | Validação empírica exploratória concluída | Não confundir resultados exploratórios com homologação semântica ou publicação oficial. |
| DAD-04 | Concluída — validação técnica exploratória | Não representa homologação metodológica; a falha da suíte completa permanece registrada no relatório DAD-04. |
| DAD-05 | **Contrato metodológico condicional; decisão final pendente** | Resolver e registrar as decisões da seção 10.3 e os critérios desta seção. |

A conclusão geral das cinco DADs requer deliberações documentadas para DAD-01, DAD-02/S e DAD-05. As DAD-03A, DAD-03B e DAD-04 permanecem encerradas no escopo atribuído. O desenvolvimento/publicação posterior depende dos gates expressamente aprovados; este parecer não inicia backend nem DAD-04.
## Referências locais

- [DAD-01 — Auditoria e homologação](DAD-01_AUDITORIA_E_HOMOLOGACAO.md): resultados Q1–Q8 reportados, qualidade, ausências, riscos da API, território, limites de rastreabilidade e parecer não homologado.
- [DAD-02 — Matriz de comparabilidade temporal](DAD-02_MATRIZ_COMPARABILIDADE_TEMPORAL.md): matriz preliminar 17 × 4, classificações técnicas, limitações semânticas e questões de população temporal.
- [Pacote de evidências — LEIA-ME](evidencias/LEIA-ME.md): escopo e natureza reportada das evidências.
- [Evidências Q5–Q8 e SQL documentado](evidencias/02_EVIDENCIAS_Q5_Q8_SQL.txt): matriz quantitativa, denominadores, cobertura e integridade territorial; SQL consultado como evidência, não executado nesta atividade.
- [Investigação documental e territorial](evidencias/03_INVESTIGACAO_DOCUMENTAL_TERRITORIAL.txt): limitações de acesso às fontes oficiais e achados complementares herdados.

## Controle de escopo

Atualizado exclusivamente este documento para incorporar o esclarecimento do professor de 13/10/2026 e alinhar o quadro decisório às evidências DAD existentes. As fórmulas e os exemplos matemáticos das seções 2–9 foram preservados. Não houve SQL, processamento de microdados, alteração de banco, código, frontend, testes ou documentos de outras DADs; nenhum commit ou push foi realizado.