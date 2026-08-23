# AI TREND SCOUT

# PHASE -1 — DISCOVERY FEASIBILITY REPORT V1.0

**Data:** 19/08/2026
**Produto:** AI Trend Scout
**Fase:** -1 — Discovery Feasibility
**Objetivo:** Determinar se existe uma estratégia tecnicamente viável, sustentável e suficientemente rica para alimentar o mecanismo de descoberta autônoma de tendências.

---

# 1. DECISÃO EXECUTIVA

## STATUS: PASS WITH ARCHITECTURAL CONDITION

A descoberta autônoma é **tecnicamente viável**.

Porém, a arquitetura não deverá depender exclusivamente da API oficial do Instagram.

A estratégia recomendada é:

```text
                         DISCOVERY
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
        Meta Official   Discovery     Future Sources
             API         Provider
              │             │             │
              └─────────────┼─────────────┘
                            ▼
                     SOURCE ABSTRACTION
                            ▼
                       RAW CONTENT
                            ▼
                         EVIDENCE
                            ▼
                      TREND ENGINE
```

A conclusão da Fase -1 é:

> **GO para implementação da infraestrutura, mas NÃO acoplar o produto ao Instagram Graph API como único mecanismo de discovery.**

---

# 2. DESCOBERTA MAIS IMPORTANTE

A API oficial da Meta possui recursos de descoberta pública, incluindo acesso a hashtag search, mas seu modelo de acesso é limitado e direcionado principalmente ao ecossistema de contas profissionais. A documentação da Meta indica que o Instagram API permite, entre outras coisas, encontrar mídia associada a hashtags e obter determinados metadados/métricas de contas e criadores profissionais.

Isso é útil.

Mas não resolve sozinho o nosso problema.

O nosso problema é:

```text
"Encontre o que está começando a acontecer."
```

e não:

```text
"Encontre conteúdos associados a uma hashtag que eu forneci."
```

Essa diferença é fundamental.

---

# 3. API OFICIAL DA META

## Resultado

### VEREDITO: PARTIAL FIT

A API oficial deve existir como connector.

Mas não deverá ser considerada:

```text
PRIMARY AUTONOMOUS DISCOVERY ENGINE
```

sem validação adicional.

---

# 4. O QUE A API OFICIAL CONSEGUE

A documentação atual indica suporte a funcionalidades como:

* hashtag search;
* mídia associada a hashtags;
* dados de contas profissionais;
* métricas de determinadas mídias;
* publicação;
* comentários;
* menções;
* insights.

A API com Facebook Login não é destinada a contas consumidoras comuns; o acesso é voltado a contas Instagram Professional.

---

# 5. LIMITAÇÃO CRÍTICA

O produto quer descobrir:

```text
novos padrões
novos formatos
novos hooks
novos áudios
novos comportamentos
novos criadores
```

sem que a usuária diga antecipadamente:

```text
"procure #x"
```

A API oficial, por suas superfícies e limitações, não deve ser assumida como um mecanismo completo de descoberta global e irrestrita.

Portanto:

```text
Meta API
=
important source

Meta API
≠
entire discovery strategy
```

---

# 6. HASHTAG DISCOVERY

A API oficial possui hashtag search.

Porém, existem limitações relevantes.

Entre elas, há limite de hashtags consultáveis em uma janela de tempo e restrições sobre os dados retornados. Fontes que documentam o comportamento atual da API indicam limite de 30 hashtags únicas em sete dias, além de restrições na recuperação de mídia recente.

Isso torna impossível utilizar:

```text
todas as hashtags da internet
```

como mecanismo primário de discovery.

---

# 7. PROBLEMA DAS HASHTAGS

Mesmo que tivéssemos:

```text
#marketing
#fitness
#beauty
#odontologia
...
```

isso ainda seria insuficiente.

Porque trends podem surgir através de:

```text
formato
áudio
hook
edição
comportamento
estrutura narrativa
creator behavior
```

sem depender de uma hashtag explícita.

Portanto:

> **Hashtag discovery é um sinal, não o Discovery Engine inteiro.**

---

# 8. DESCOBERTA POR PERFIS

Uma segunda estratégia é monitorar perfis.

```text
Creator A
Creator B
Creator C
...
```

e detectar mudanças:

```text
frequência
formatos
hooks
engagement
topics
audio
```

Isso é muito útil para:

```text
competitor intelligence
creator intelligence
trend confirmation
```

Mas possui uma limitação:

> Precisamos saber quais perfis monitorar.

Portanto, novamente:

```text
profile monitoring
=
evidence/discovery component

não
=
global discovery
```

---

# 9. CONCLUSÃO SOBRE A META API

A API oficial deverá ser implementada como:

```text
OfficialInstagramConnector
```

com capacidade de:

```text
HASHTAG_DISCOVERY
PROFESSIONAL_ACCOUNT_DATA
MEDIA_METADATA
INSIGHTS
```

quando permitido pelas permissões disponíveis.

Ela deverá ser considerada uma fonte de alta confiança.

---

# 10. DISCOVERY PROVIDERS DE TERCEIROS

A pesquisa encontrou uma segunda categoria:

```text
Managed Instagram Data Providers
```

Esses serviços oferecem infraestrutura de coleta pública e entregam dados já estruturados.

Dois exemplos relevantes encontrados foram:

* Bright Data
* Apify

Eles não devem ser tratados como "Instagram APIs oficiais".

São uma camada externa de coleta.

---

# 11. BRIGHT DATA

A oferta atual de Instagram da Bright Data inclui coleta de:

```text
profiles
posts
reels
comments
engagement
views
likes
timestamps
hashtags
```

e oferece APIs de coleta, execução em lote e jobs agendados.

A página atual também informa:

```text
5.000 records/mês
free tier

$1.50 / 1.000 records
pay-as-you-go

$499/mês
384.000 records
```

para o produto de Instagram/Reels, conforme o plano.

---

# 12. VANTAGEM DA BRIGHT DATA

A principal vantagem arquitetural é:

```text
nosso sistema
     ↓
Bright Data API
     ↓
Instagram
```

em vez de:

```text
nosso sistema
     ↓
proxy
     ↓
browser
     ↓
Instagram
```

A infraestrutura de coleta, proxy, rendering e mecanismos de acesso fica fora do nosso domínio.

Isso reduz bastante a complexidade operacional do MVP.

---

# 13. RISCO DA BRIGHT DATA

Não devemos confundir:

```text
"tecnicamente acessível"
```

com:

```text
"legalmente autorizado para qualquer finalidade"
```

A própria Meta estabelece restrições relevantes sobre coleta automatizada. Os termos atuais dizem que coleta automatizada de dados dos produtos Meta requer permissão expressa por escrito, salvo quando explicitamente autorizada, e impõem condições sobre uso, segurança, rate limiting e dados coletados.

Portanto:

> **Bright Data reduz o problema técnico. Não elimina a análise de termos, permissões e compliance.**

---

# 14. APIFY

A pesquisa encontrou múltiplos Actors para Instagram.

Um deles oferece descoberta de Reels por palavra-chave sem login, com dados como:

```text
plays
likes
comments
shares
captions
hashtags
audio
creator
```

e informa preço inicial de aproximadamente:

```text
$1.50 / 1.000 resultados
```

no Actor analisado.

Outro Actor encontrado oferece descoberta de Reels por país, incluindo Brasil, utilizando a experiência pública/logged-out de Reels e distinguindo resultados diretamente surfaced pelo feed de descoberta de outros conteúdos encontrados a partir dos criadores.

---

# 15. DESCOBERTA POR PAÍS

Esse ponto é especialmente interessante para nosso produto.

O Actor de discovery analisado permite:

```text
countryCode = BR
```

e relata que a descoberta pode ser executada dentro do contexto regional correspondente.

Isso abre uma possibilidade:

```text
Brazil Discovery
       ↓
Public Reels Sample
       ↓
Trend Detection
```

em vez de depender apenas de:

```text
hashtags
```

---

# 16. LIMITAÇÃO IMPORTANTE DO FEED DE DESCOBERTA

O próprio material do provider alerta que o feed descoberto não deve ser interpretado como um ranking oficial global de popularidade.

Ou seja:

```text
"Instagram mostrou"
```

não significa necessariamente:

```text
"isso é o conteúdo mais popular do Brasil"
```

Isso é importante.

Mas para nosso produto isso não é necessariamente um problema.

Na verdade:

> **Estamos procurando sinais de descoberta, não um ranking oficial de popularidade.**

---

# 17. OUTRO APIFY ACTOR

Também foi encontrado um Actor que trabalha com Reels de perfis públicos, fornecendo:

```text
caption
hashtags
mentions
likes
comments
views
duration
creator
timestamps
```

e informa preço de aproximadamente:

```text
$0.49 / 1.000 resultados
```

no momento da pesquisa.

Porém, este é mais adequado a:

```text
profile monitoring
```

do que a:

```text
global discovery
```

---

# 18. NOVA CONCLUSÃO ARQUITETURAL

Precisamos de pelo menos **três tipos de discovery**.

```text
DISCOVERY
│
├── EXPLORATION
│      ↓
│   descobrir novos conteúdos
│
├── MONITORING
│      ↓
│   acompanhar perfis/fontes
│
└── VALIDATION
       ↓
    confirmar sinais
```

Isso é melhor do que tentar encontrar uma única API que faça tudo.

---

# 19. ARQUITETURA RECOMENDADA

```text
                    AUTONOMOUS SCOUT
                           │
                           ▼
                  DISCOVERY ORCHESTRATOR
                           │
           ┌───────────────┼────────────────┐
           │               │                │
           ▼               ▼                ▼
     Exploration       Monitoring       Validation
           │               │                │
           ▼               ▼                ▼
      Provider A       Provider B       Official API
           │               │                │
           └───────────────┼────────────────┘
                           ▼
                      RAW CONTENT
```

---

# 20. PROVIDER ABSTRACTION

A arquitetura deverá continuar usando:

```python
class TrendSource:
    async def discover(...):
        ...

    async def health_check(...):
        ...

    async def capabilities(...):
        ...
```

Mas agora deverá existir uma distinção adicional:

```text
DiscoveryMode
```

com valores:

```text
EXPLORATION
MONITORING
VALIDATION
```

---

# 21. EXPLORATION

Responsável por:

```text
descobrir coisas que ainda não conhecemos
```

Exemplos:

```text
public Reels discovery
keyword discovery
regional discovery
web discovery
```

---

# 22. MONITORING

Responsável por:

```text
acompanhar algo que já descobrimos
```

Exemplos:

```text
creator
competitor
profile
topic
audio
format
```

---

# 23. VALIDATION

Responsável por:

```text
confirmar se o sinal é real
```

Exemplos:

```text
official API
second provider
historical sample
cross-source evidence
```

---

# 24. POR QUE ISSO É MELHOR

Imagine:

```text
Provider A
```

encontra:

```text
Format X
```

O sistema não precisa acreditar imediatamente.

Ele pode:

```text
A encontrou
    ↓
B confirmou
    ↓
crescimento observado
    ↓
múltiplos creators
    ↓
TREND CANDIDATE
```

Isso reduz falsos positivos.

---

# 25. DISCOVERY NÃO DEVE SER "LLM SEARCH"

Não devemos criar:

```text
LLM
 ↓
"procure trends no Instagram"
```

e considerar isso discovery.

A IA pode:

```text
gerar queries
interpretar sinais
classificar conteúdo
```

mas a coleta precisa existir como camada independente.

---

# 26. AI-GENERATED DISCOVERY STRATEGY

Uma evolução futura poderá ser:

```text
Client DNA
      ↓
LLM
      ↓
Discovery Strategy
      ↓
keywords
topics
formats
creators
hashtags
regions
      ↓
Discovery Providers
```

Isso é muito mais poderoso.

Mas não deve ser requisito para provar o MVP.

---

# 27. O PRIMEIRO EXPERIMENTO

O experimento recomendado é:

```text
BR
+
public Reels discovery
+
100–500 conteúdos
+
2 execuções em momentos diferentes
```

Objetivo:

verificar:

```text
volume
freshness
duplicates
metadata
creator diversity
engagement fields
timestamps
```

---

# 28. EXPERIMENTO 2

Executar:

```text
same discovery
+
different time window
```

e medir:

```text
new content
repeated content
changed metrics
new creators
new formats
```

Isso começará a provar:

```text
temporal intelligence
```

---

# 29. EXPERIMENTO 3

Executar dois caminhos:

```text
Discovery Provider A
        VS
Discovery Provider B
```

comparar:

```text
overlap
unique content
creator overlap
metadata overlap
freshness
```

---

# 30. EXPERIMENTO 4

Criar um dataset pequeno contendo uma tendência artificialmente conhecida:

```text
Trend A
Trend B
Trend C
Noise
Viral isolated
```

O Trend Engine deverá receber somente os dados.

Objetivo:

```text
detect trend
reject noise
rank emerging signal
```

---

# 31. EXPERIMENTO 5

Cross-Niche:

```text
Niche A
Niche B
Niche C
```

Inserir uma mesma estrutura de conteúdo em evolução.

O sistema deverá detectar:

```text
same mechanism
+
different niches
=
cross-niche trend
```

---

# 32. CRITÉRIOS QUANTITATIVOS PROPOSTOS

Para aprovação inicial do Discovery Provider:

### Freshness

Pelo menos:

```text
80% dos conteúdos
```

deverão estar dentro da janela temporal definida pelo experimento.

---

### Deduplication

Após normalização:

```text
>95%
```

dos duplicados óbvios deverão ser identificados.

---

### Availability

Durante o experimento:

```text
≥95%
```

de execuções bem-sucedidas.

---

### Metadata

Pelo menos:

```text
80%
```

dos registros deverão possuir:

```text
timestamp
+
URL/ID
```

e a cobertura dos demais campos será medida separadamente.

---

### Repeatability

No mínimo:

```text
3 execuções
```

deverão produzir resultados processáveis.

---

# 33. CRITÉRIO MAIS IMPORTANTE

Não basta conseguir:

```text
1000 posts
```

Precisamos conseguir:

```text
1000 posts
+
tempo
+
creator
+
metrics
+
metadata
```

com qualidade suficiente para o Trend Engine.

---

# 34. DISCOVERY QUALITY SCORE

Cada provider deverá receber:

```text
Discovery Quality Score
```

com:

```text
Freshness       20%
Coverage        20%
Metadata        15%
Reliability     15%
Diversity       10%
Cost            10%
Validation      10%
```

Pesos poderão ser ajustados após os experimentos.

---

# 35. PROVIDER COMPARISON

| Critério                   |               Meta API |        Managed Scraper |              Apify Actor |
| -------------------------- | ---------------------: | ---------------------: | -----------------------: |
| Oficial                    |                      ✅ |                      ❌ |                        ❌ |
| Discovery amplo            |                     ⚠️ |                      ✅ |                        ✅ |
| Hashtag                    |                      ✅ | dependendo do provider |      dependendo do Actor |
| Reels discovery            |               limitado |                      ✅ |                        ✅ |
| Dados profissionais        |                      ✅ |               variável |                 variável |
| Login da usuária           |    não necessariamente |                    não | não nos Actors avaliados |
| Infra de coleta            |                  nossa |               provider |                 provider |
| Controle                   |                   alto |                  médio |                    médio |
| Custo inicial              | API/platform dependent |                   pago | geralmente baixo/modular |
| Risco de provider          |                  baixo |                  médio |               médio/alto |
| Adequado como único source |                      ❌ |                      ❌ |                        ❌ |
| Adequado como connector    |                      ✅ |                      ✅ |                        ✅ |

---

# 36. RECOMENDAÇÃO

A arquitetura recomendada é:

### Tier 1

```text
Official Meta API
```

para:

```text
trusted evidence
professional accounts
official metrics
```

---

### Tier 2

```text
Managed Discovery Provider
```

para:

```text
exploration
public Reels discovery
scale
```

---

### Tier 3

```text
Second Provider
```

para:

```text
validation
fallback
cross-source verification
```

---

### Tier 4

```text
Web / Other Platforms
```

para:

```text
cross-platform signals
```

---

# 37. NÃO ESCOLHER AINDA UM PROVIDER DEFINITIVO

Apesar de existirem candidatos tecnicamente interessantes, **não devemos hardcodar Bright Data ou Apify como decisão final nesta fase**.

Primeiro:

```text
benchmark
```

Depois:

```text
provider selection
```

Isso preserva o contrato.

---

# 38. DECISÃO DE IMPLEMENTAÇÃO

A Fase 0 deverá implementar:

```text
SourceRegistry
TrendSource
DiscoveryMode
DiscoveryQuery
RawContent
SourceHealth
```

mas **não deverá acoplar o domínio a um provider específico**.

---

# 39. PRIMEIRO CONNECTOR

O primeiro connector experimental deverá ser implementado atrás de:

```text
InstagramDiscoveryProvider
```

e sua implementação concreta poderá ser:

```text
MetaOfficialProvider
```

ou:

```text
ManagedInstagramProvider
```

ou ambos.

---

# 40. SEGUNDO CONNECTOR

Deverá ser planejado desde o início:

```text
AlternativeDiscoveryProvider
```

Mesmo que inicialmente seja utilizado apenas no benchmark.

---

# 41. NOVA REGRA DE ARQUITETURA

O sistema deverá permitir:

```text
Provider A DOWN
       ↓
Provider B
       ↓
Discovery continua
```

quando a estratégia de fallback estiver configurada.

---

# 42. RISCO LEGAL / COMPLIANCE

Este é o maior ponto que não pode ser mascarado.

A Meta afirma atualmente que coleta automatizada de dados dos seus produtos exige permissão expressa por escrito, salvo quando explicitamente autorizada, e também proíbe contornar mecanismos tecnológicos de controle de acesso.

Portanto:

```text
"scraper funciona"
```

não equivale a:

```text
"podemos operar comercialmente dessa forma"
```

A implementação deverá ter uma camada de compliance que permita substituir o provider caso a estratégia escolhida não seja aceitável para o uso pretendido.

---

# 43. IMPLICAÇÃO PARA O MVP

Não devemos armazenar indiscriminadamente:

```text
vídeos
imagens
comentários
PII
```

se não forem necessários.

Inicialmente, priorizar:

```text
content ID
URL
timestamp
creator identifier
caption
hashtags
metrics
audio identifier
metadata
```

e somente armazenar mídia quando houver necessidade técnica e base apropriada.

---

# 44. DATA RETENTION

O sistema deverá ter retenção configurável.

Exemplo:

```text
raw content:
30–90 dias

aggregated signals:
longer retention

trend entities:
long-term
```

Os valores definitivos deverão ser definidos após análise jurídica/operacional.

---

# 45. PRINCIPAL RISCO TÉCNICO

O maior risco não é:

```text
Python
FastAPI
PostgreSQL
LLM
```

É:

# DATA ACCESS + DATA QUALITY

Sem dados suficientemente ricos e recorrentes:

```text
Trend Engine
```

não terá matéria-prima.

---

# 46. PRINCIPAL RISCO DE PRODUTO

Mesmo com bons dados:

```text
data ≠ trend
```

Teremos que provar:

```text
content
→ signal
→ pattern
→ trend
```

Esse será o segundo grande experimento.

---

# 47. DECISÃO SOBRE O BLUEPRINT V1.2

O Blueprint V1.2 continua válido.

Mas deverá receber estas alterações:

### Adicionar

```text
DiscoveryMode
EXPLORATION
MONITORING
VALIDATION
```

### Adicionar

```text
Evidence Engine
```

como componente de primeira classe.

### Adicionar

```text
Provider Benchmark
```

à Fase -1.

### Adicionar

```text
Compliance Gate
```

à decisão de provider.

---

# 48. NOVO ROADMAP

A ordem recomendada passa a ser:

```text
PHASE -1
Discovery Feasibility
       ↓
PHASE 0
Foundation
       ↓
PHASE 1
Provider Benchmark
       ↓
PHASE 2
Discovery Infrastructure
       ↓
PHASE 3
Evidence + Normalization
       ↓
PHASE 4
Content Intelligence
       ↓
PHASE 5
Temporal Intelligence
       ↓
PHASE 6
Trend Engine
       ↓
PHASE 7
Scoring + Confidence
       ↓
PHASE 8
Client DNA
       ↓
PHASE 9
Client Matching
       ↓
PHASE 10
AI Adaptation
       ↓
PHASE 11
Radar
       ↓
PHASE 12
Feedback
       ↓
PHASE 13
Learning
       ↓
PHASE 14
Autonomous Scout
       ↓
PHASE 15
Expansion
```

---

# 49. FASE -1 — RESULTADO

## Technical Feasibility

```text
PASS
```

Existe tecnologia suficiente para executar discovery automatizado.

---

## Autonomous Discovery

```text
PASS
```

É tecnicamente possível construir uma camada de discovery que opere sem a usuária procurar manualmente as trends.

---

## Official API as Sole Source

```text
FAIL
```

Não deve ser utilizada como única estratégia.

---

## Managed Providers

```text
PASS WITH VALIDATION
```

Existem soluções capazes de fornecer dados de Reels e discovery em escala, mas deverão ser submetidas ao benchmark e ao compliance gate antes da seleção definitiva.

---

## Multi-Provider Architecture

```text
PASS
```

É a arquitetura recomendada.

---

## Evidence Architecture

```text
PASS
```

É tecnicamente viável e deve ser obrigatória.

---

## Temporal Trend Detection

```text
PASS WITH DATASET VALIDATION
```

A arquitetura é viável, mas o algoritmo deverá ser validado com dados reais antes de qualquer claim de qualidade.

---

# 50. GO / NO-GO

## GO

Para:

```text
Foundation
+
Provider Benchmark
+
Discovery Infrastructure
```

---

## NO-GO

Para:

```text
full product
```

antes de concluir:

```text
Provider Benchmark
+
Evidence Validation
+
Trend Detection Benchmark
```

---

# 51. DECISÃO FINAL

# PHASE -1 = PASS

Com uma condição:

> **O projeto deve avançar para um benchmark real de providers antes de escolher definitivamente o mecanismo de discovery.**

---

# 52. PRÓXIMO EXPERIMENTO

O próximo artefato técnico deverá ser:

# PHASE -1.1 — PROVIDER BENCHMARK

Objetivo:

Comparar pelo menos:

```text
Meta Official API
+
Provider A
+
Provider B
```

utilizando exatamente o mesmo protocolo.

---

# 53. DATASET DO BENCHMARK

Executar:

```text
Brazil
Reels
public discovery
3 execuções
```

com:

```text
100–500 resultados por execução
```

quando a fonte permitir.

---

# 54. CAMPOS A COMPARAR

```text
id
url
creator
timestamp
caption
hashtags
likes
comments
views
audio
duration
media type
source
```

Além de:

```text
collection timestamp
```

---

# 55. MÉTRICAS DO BENCHMARK

Medir:

```text
records returned
unique records
duplicate rate
freshness
creator diversity
metadata completeness
execution success
latency
cost
```

---

# 56. RESULTADO ESPERADO

Produzir:

```text
provider-benchmark.json
provider-benchmark.csv
provider-benchmark-report.md
```

e uma decisão:

```text
PRIMARY PROVIDER
SECONDARY PROVIDER
OFFICIAL VALIDATION PROVIDER
```

---

# 57. CRITÉRIO DE SELEÇÃO

O provider vencedor não será simplesmente:

```text
mais barato
```

ou:

```text
mais dados
```

Será aquele que maximizar:

```text
QUALITY
+
FRESHNESS
+
DIVERSITY
+
RELIABILITY
+
COST
+
COMPLIANCE VIABILITY
```

---

# 58. CONCLUSÃO

A pesquisa muda nossa percepção de um ponto importante:

Não precisamos encontrar **"a API mágica do Instagram"**.

Precisamos construir:

# UM SISTEMA DE OBSERVAÇÃO

com múltiplas fontes e múltiplos mecanismos de evidência.

O verdadeiro ativo do AI Trend Scout será:

```text
                     DATA SOURCES
                          ↓
                     OBSERVATION
                          ↓
                       SIGNALS
                          ↓
                       PATTERNS
                          ↓
                        TRENDS
                          ↓
                      EVIDENCE
                          ↓
                     INTELLIGENCE
                          ↓
                    OPPORTUNITY
```

O provider é substituível.

O **Trend Intelligence Engine** é o produto.

---

# 59. STATUS OFICIAL

```text
AI TREND SCOUT
PHASE -1

STATUS: PASS

DISCOVERY:
FEASIBLE

OFFICIAL META API:
VALID SOURCE / NOT SOLE SOURCE

MANAGED DISCOVERY:
TECHNICALLY VIABLE / VALIDATION REQUIRED

MULTI-PROVIDER:
RECOMMENDED

EVIDENCE ENGINE:
MANDATORY

COMPLIANCE:
GATE REQUIRED

NEXT PHASE:
PROVIDER BENCHMARK

FINAL DECISION:
GO
```

# 60. REGRA PARA O AGENTE

O agente não deverá escolher um provider baseado em documentação ou preço.

Ele deverá:

```text
INSTALL / CONNECT
        ↓
RUN BENCHMARK
        ↓
COLLECT RESULTS
        ↓
MEASURE
        ↓
COMPARE
        ↓
REPORT
        ↓
RECOMMEND
```

Somente depois disso poderá declarar:

```text
PRIMARY DISCOVERY PROVIDER
```

**FIM — PHASE -1 DISCOVERY FEASIBILITY REPORT V1.0**
