# SIE — Evidência documental de comparabilidade nominal dos 17 indicadores (2022–2025)

**Situação:** verificação documental técnica concluída; homologação semântica e aprovação institucional pendentes.

## Escopo e método

Foram examinadas exclusivamente as planilhas de dicionário de variáveis do Censo Escolar contidas nos pacotes fornecidos pelo projeto. **Não foram lidos ou processados os arquivos de microdados de escolas ou alunos.** Em cada ano, conferiram-se as colunas B (variável), C (descrição), D (tipo), F (categoria/domínio), e a coluna de coleta anual correspondente (2022: V; 2023: W; 2024: X; 2025: Y).

Conclusões verificadas: 17/17 variáveis localizadas em cada edição (68/68 pares variável × ano); descrições e categorias textualmente idênticas nas quatro planilhas; tipo `Num` em todas; domínio `0 - Não` / `1 - Sim`; marcação anual de coleta `s` para todos os indicadores. Nenhuma diferença nesses campos foi detectada.

## Fontes específicas

| Ano | Arquivo-fonte | Aba | SHA-256 do Excel (extraído) |
|---|---|---|---|
| 2022 | `microdados_censo_escolar_2022.zip → Anexos/ANEXO I - Dicionário de Dados/dicionário_dados_educação_básica.xlsx` | `Cadastro_Escolas` | `87e00e20cb50183d7f6d3966e8582f632019cc3c8ac70994edab17517b7d5fd1` |
| 2023 | `microdados_censo_escolar_2023.zip → Anexos/ANEXO I - Dicionário de Dados/dicionário_dados_educação_básica.xlsx` | `microdados_unidade_coleta` | `64a86f4d99478e5c4efbb78f1dabbde51ebb91d279997b86f77ad21ee4523888` |
| 2024 | `microdados_censo_escolar_2024.zip → Anexos/ANEXO I - Dicionário de Dados/dicionário_dados_educação_básica.xlsx` | `microdados_unidade_coleta` | `7b864d016abb815663a8fbaf513212be6de77c494213887bfc88d73b33e59cb8` |
| 2025 | `Anexos.zip → Anexos/ANEXO I - Dicionário de Dados/dicionário_dados_educação_básica.xlsx` | `Tabela_de_Escola` | `140e0f3d0df0241330f1c26fd45e516e63bd2ad60fb7ae3c9ae5cb47c6290166` |

## Matriz de rastreabilidade das 68 verificações

Em cada célula de ano: linha da planilha e coluna da marca de coleta do ano (`s`). A definição fica nas colunas B–F da mesma linha.

| Indicador | Definição oficial (descrição do dicionário) | 2022 (V) | 2023 (W) | 2024 (X) | 2025 (Y) |
|---|---|---:|---:|---:|---:|
| `IN_AGUA_POTAVEL` | Fornece água potável para o consumo humano | linha 85: `s` | linha 100: `s` | linha 101: `s` | linha 108: `s` |
| `IN_ENERGIA_REDE_PUBLICA` | Abastecimento de energia elétrica - Rede pública | linha 91: `s` | linha 106: `s` | linha 108: `s` | linha 115: `s` |
| `IN_ESGOTO_REDE_PUBLICA` | Esgoto sanitário - Rede pública | linha 97: `s` | linha 112: `s` | linha 114: `s` | linha 121: `s` |
| `IN_LIXO_SERVICO_COLETA` | Destinação do lixo - Serviço de coleta | linha 102: `s` | linha 117: `s` | linha 119: `s` | linha 126: `s` |
| `IN_BANHEIRO` | Dependências físicas existentes e utilizadas na escola - Banheiro | linha 119: `s` | linha 134: `s` | linha 137: `s` | linha 144: `s` |
| `IN_BANHEIRO_PNE` | Dependências físicas existentes e utilizadas na escola - Banheiro acessível, adequado ao uso de pessoas com deficiência ou mobilidade reduzida | linha 121: `s` | linha 136: `s` | linha 139: `s` | linha 146: `s` |
| `IN_BIBLIOTECA` | Dependências físicas existentes e utilizadas na escola - Biblioteca | linha 125: `s` | linha 140: `s` | linha 143: `s` | linha 150: `s` |
| `IN_SALA_LEITURA` | Dependências físicas existentes e utilizadas na escola - Sala de leitura | linha 148: `s` | linha 164: `s` | linha 167: `s` | linha 174: `s` |
| `IN_LABORATORIO_CIENCIAS` | Dependências físicas existentes e utilizadas na escola - Laboratório de ciências | linha 131: `s` | linha 146: `s` | linha 149: `s` | linha 156: `s` |
| `IN_LABORATORIO_INFORMATICA` | Dependências físicas existentes e utilizadas na escola - Laboratório de informática | linha 132: `s` | linha 147: `s` | linha 150: `s` | linha 157: `s` |
| `IN_SALA_MULTIUSO` | Dependências físicas existentes e utilizadas na escola - Sala multiuso (música, dança e artes) | linha 145: `s` | linha 160: `s` | linha 163: `s` | linha 170: `s` |
| `IN_SALA_ATENDIMENTO_ESPECIAL` | Dependências físicas existentes e utilizadas na escola - Sala de Recursos Multifuncionais para Atendimento Educacional Especializado (AEE) | linha 152: `s` | linha 168: `s` | linha 171: `s` | linha 178: `s` |
| `IN_COZINHA` | Dependências físicas existentes e utilizadas na escola - Cozinha | linha 127: `s` | linha 142: `s` | linha 145: `s` | linha 152: `s` |
| `IN_REFEITORIO` | Dependências físicas existentes e utilizadas na escola - Refeitório | linha 141: `s` | linha 156: `s` | linha 159: `s` | linha 166: `s` |
| `IN_QUADRA_ESPORTES` | Dependências físicas existentes e utilizadas na escola - Quadra de esportes coberta ou descoberta | linha 138: `s` | linha 153: `s` | linha 156: `s` | linha 163: `s` |
| `IN_PATIO_COBERTO` | Dependências físicas existentes e utilizadas na escola - Pátio coberto | linha 134: `s` | linha 149: `s` | linha 152: `s` | linha 159: `s` |
| `IN_AUDITORIO` | Dependências físicas existentes e utilizadas na escola - Auditório | linha 116: `s` | linha 131: `s` | linha 134: `s` | linha 141: `s` |

## O que esta evidência NÃO demonstra

1. As regras de preenchimento, o tratamento de não aplicabilidade, restrições por tipo de escola e eventuais alterações operacionais ao longo dos anos não foram auditados aqui a partir dos questionários ou do pipeline. A coincidência textual das descrições não basta, isoladamente, para homologação semântica completa.
2. A origem e a transformação de cada campo da tabela `silver.infraestrutura_comum` não são demonstradas pelas planilhas: o ETL original não está documentado/preservado conforme esclarecimento recebido da orientação. Não se conclui que a tabela Silver reproduz necessariamente os arquivos brutos sem transformações.
3. Esta evidência não esclarece as 1.249 observações com os 17 campos nulos, divergências de códigos/nome municipal ou garantia de carga.
4. O uso da média aritmética e a delimitação aos 22 municípios foram esclarecidos pela orientação do projeto, mas não são propriedades provadas pelos dicionários.
5. **Decisão de homologação:** a revisão e a assinatura/registro pelos responsáveis do projeto são uma etapa separada. Não alterar o estado das DADs automaticamente.

## Uso recomendado nas DADs

- **DAD-02:** anexar esta matriz como evidência de consistência nominal, descritiva, de domínio e de coleta anual dos 17 candidatos nas quatro edições; submeter ao responsável para a decisão de comparabilidade semântica.
- **DAD-01:** registrar a localização da fonte primária do INEP, mas manter ressalva de proveniência do processo de carga e pendências territoriais/ausência.
- **DAD-05:** registrar separadamente a aprovação da média aritmética pelo professor e solicitar a decisão explícita sobre as demais regras condicionais.
