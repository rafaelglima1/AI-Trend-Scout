# AI TREND SCOUT

## IMPLEMENTATION CONTRACT V1.0

**Status:** Implementation Candidate
**Versão:** 1.0
**Base:** Blueprint V1.2
**Data:** 19/08/2026
**Produto:** AI Trend Scout
**Objetivo:** Transformar a descoberta de tendências para Social Media em um processo autônomo, contínuo, mensurável e acionável.

---

# 1. NATUREZA DESTE DOCUMENTO

Este documento é o **contrato técnico de implementação** do AI Trend Scout.

O Blueprint V1.2 define **o que o produto deve ser**.

Este documento define:

* o que deve ser implementado;
* como os componentes devem se relacionar;
* quais contratos devem existir;
* quais comportamentos são obrigatórios;
* como cada fase será validada;
* o que constitui PASS;
* o que constitui FAIL;
* o que constitui BLOCKER;
* quando o agente de desenvolvimento pode avançar;
* quando uma implementação deve ser rejeitada.

O agente de desenvolvimento **não deve interpretar livremente requisitos críticos deste documento**.

Quando houver conflito entre:

1. implementação existente;
2. preferência de implementação do agente;
3. suposição técnica;
4. este contrato;

este contrato prevalece.

---

# 2. MISSÃO DO PRODUTO

O AI Trend Scout deverá descobrir autonomamente tendências relevantes para Social Media.

A usuária não deverá precisar:

* procurar manualmente trends;
* pesquisar hashtags;
* navegar durante horas;
* acompanhar dezenas de criadores;
* procurar formatos manualmente;
* fornecer previamente a tendência que deseja analisar.

O sistema deverá executar:

```text
DISCOVER
   ↓
COLLECT
   ↓
NORMALIZE
   ↓
ANALYZE
   ↓
DETECT
   ↓
VALIDATE
   ↓
SCORE
   ↓
MATCH
   ↓
CURATE
   ↓
ADAPT
```

A saída final deverá responder:

> **"O que está acontecendo agora e o que isso significa para este cliente?"**

---

# 3. REGRA ABSOLUTA DO PRODUTO

## AUTONOMOUS DISCOVERY RULE

Se a Social Media precisar realizar manualmente a descoberta que o sistema deveria realizar, o produto estará incompleto.

É permitido:

* configurar fontes;
* configurar clientes;
* configurar nichos;
* configurar preferências;
* revisar resultados;
* fornecer feedback.

Não é permitido que a operação normal dependa de:

```text
usuária encontra trend
        ↓
usuária envia trend
        ↓
IA analisa
```

O fluxo esperado é:

```text
IA encontra
        ↓
IA analisa
        ↓
IA valida
        ↓
IA prioriza
        ↓
usuária recebe
```

---

# 4. PRINCÍPIOS ARQUITETURAIS

## 4.1 Source Independence

Nenhuma regra de negócio poderá depender diretamente de Instagram, TikTok, Reddit ou outro provider.

---

## 4.2 AI Provider Independence

Nenhuma regra de negócio poderá depender diretamente de um fornecedor específico de LLM ou embedding.

---

## 4.3 Evidence First

Nenhuma trend poderá ser considerada real apenas porque um LLM afirmou que ela existe.

Uma trend deverá possuir evidências observáveis.

---

## 4.4 Temporal Intelligence

Trend detection deverá considerar comportamento ao longo do tempo.

Similaridade isolada não é suficiente.

---

## 4.5 Explainability

Toda recomendação deverá explicar:

* por que foi detectada;
* por que recebeu determinada pontuação;
* por que foi recomendada ao cliente;
* quais evidências sustentam a conclusão;
* quais riscos existem.

---

## 4.6 Fail Closed

Quando o sistema não possuir evidência suficiente:

```text
não afirmar
```

Deverá retornar algo equivalente a:

```text
INSUFFICIENT_EVIDENCE
```

---

## 4.7 Replaceability

Qualquer connector, LLM, embedding provider ou mecanismo de fila deverá poder ser substituído sem reescrever o domínio.

---

# 5. STACK BASE

## Backend

```text
Python 3.12+
FastAPI
Pydantic
SQLAlchemy
Alembic
PostgreSQL
pgvector
Redis
```

## Frontend

```text
Next.js
TypeScript
React
Tailwind CSS
```

## Infraestrutura

```text
Docker
Docker Compose
CI/CD
```

## Observabilidade

```text
OpenTelemetry
Structured Logging
Metrics
Tracing
```

A escolha de biblioteca específica poderá mudar durante implementação apenas mediante justificativa técnica documentada.

---

# 6. ESTRUTURA ARQUITETURAL

Arquitetura lógica:

```text
                        FRONTEND
                           │
                           ▼
                     API / BFF
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
     Client Domain    Trend Domain      AI Gateway
          │                │                │
          └────────────────┼────────────────┘
                           │
                           ▼
                 Intelligence Layer
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
      Discovery        Evidence        Temporal
        Engine          Engine         Intelligence
          │                │                │
          └────────────────┼────────────────┘
                           │
                           ▼
                    Source Connectors
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
      Instagram           Web         Future Sources
```

---

# 7. REGRA DE DEPENDÊNCIA

Dependências devem apontar para dentro.

O domínio não deverá conhecer:

* FastAPI;
* PostgreSQL;
* Redis;
* SDK de LLM;
* SDK de Instagram;
* SDK de embeddings.

Esses elementos pertencem à infraestrutura/adapters.

---

# 8. ESTRUTURA INICIAL DO REPOSITÓRIO

Estrutura de referência:

```text
ai-trend-scout/
│
├── src/
│   └── trend_scout/
│       ├── domain/
│       │   ├── clients/
│       │   ├── trends/
│       │   ├── content/
│       │   ├── discovery/
│       │   └── common/
│       │
│       ├── application/
│       │   ├── discovery/
│       │   ├── intelligence/
│       │   ├── trends/
│       │   ├── clients/
│       │   └── adaptation/
│       │
│       ├── infrastructure/
│       │   ├── database/
│       │   ├── queue/
│       │   ├── ai/
│       │   ├── embeddings/
│       │   ├── connectors/
│       │   └── observability/
│       │
│       └── api/
│           ├── routes/
│           ├── schemas/
│           └── dependencies/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   └── e2e/
│
├── migrations/
├── docker/
├── docs/
├── scripts/
├── pyproject.toml
├── docker-compose.yml
└── README.md
```

O agente poderá ajustar a estrutura física, mas deverá preservar a separação arquitetural.

---

# 9. DOMÍNIO PRINCIPAL

As entidades mínimas são:

```text
User
Client
ClientDNA

RawContent
NormalizedContent
ContentAnalysis

ContentCluster

Trend
TrendEvidence
TrendSignal
TrendLifecycle

TrendScore
TrendMatch

Adaptation

Feedback
PreferenceProfile

DiscoveryJob
Source
SourceHealth
```

---

# 10. RAW CONTENT

Contrato mínimo:

```text
RawContent
├── id
├── source
├── external_id
├── url
├── author
├── published_at
├── collected_at
├── text
├── media_type
├── media_reference
├── hashtags
├── audio_reference
├── raw_metrics
└── metadata
```

O objeto deverá preservar os dados originais disponíveis.

Dados derivados não devem sobrescrever os dados brutos.

---

# 11. NORMALIZED CONTENT

Após coleta:

```text
RawContent
      ↓
Normalization
      ↓
NormalizedContent
```

O conteúdo normalizado deverá possuir estrutura consistente independentemente da origem.

---

# 12. CONTENT INTELLIGENCE

A análise deverá extrair, quando possível:

```text
topic
subtopics
niche
hook
format
structure
tone
emotion
cta
keywords
entities
content_intent
visual_features
audio_features
text_features
```

A ausência de uma característica não poderá causar falha do processamento inteiro.

---

# 13. EMBEDDINGS

Embeddings deverão ser utilizados para:

* similaridade;
* agrupamento;
* descoberta de padrões;
* busca semântica;
* comparação entre conteúdos.

O provider deverá ser abstraído.

Contrato conceitual:

```python
class EmbeddingProvider:
    async def embed(
        self,
        text: str
    ) -> list[float]:
        ...
```

---

# 14. DISCOVERY CONNECTOR

Todo connector deverá implementar contrato equivalente a:

```python
class TrendSource(Protocol):

    async def discover(
        self,
        query: DiscoveryQuery
    ) -> list[RawContent]:
        ...

    async def health_check(
        self
    ) -> SourceHealth:
        ...

    async def capabilities(
        self
    ) -> SourceCapabilities:
        ...
```

---

# 15. SOURCE CAPABILITIES

Cada fonte deverá declarar suas capacidades.

Exemplo:

```text
search
discovery
author_metadata
metrics
publication_date
media
audio
hashtags
pagination
historical_data
```

O sistema não deverá assumir que todas as fontes possuem todas as capacidades.

---

# 16. DISCOVERY QUERY

Uma consulta deverá poder conter:

```text
source
niche
topic
keywords
language
region
time_range
content_type
limit
cursor
```

A ausência de query manual não poderá impedir o Autonomous Scout.

---

# 17. AUTONOMOUS DISCOVERY

O Scout deverá ser capaz de gerar estratégias de descoberta.

Exemplo:

```text
Client DNA
     ↓
Discovery Strategy
     ↓
Source Selection
     ↓
Queries / Signals
     ↓
Collection
```

A estratégia poderá ser:

* temática;
* semântica;
* baseada em crescimento;
* baseada em formatos;
* baseada em criadores;
* baseada em sinais previamente encontrados.

---

# 18. EVIDENCE ENGINE

A Evidence Engine será responsável por sustentar as conclusões do Trend Engine.

Cada trend deverá possuir:

```text
TrendEvidence[]
```

Uma evidência deverá possuir, no mínimo:

```text
source
content_id
observed_at
metric_snapshot
signal_type
relevance
```

---

# 19. TREND CANDIDATE

Um cluster não será automaticamente uma trend.

Fluxo:

```text
Contents
   ↓
Clusters
   ↓
Candidate Pattern
   ↓
Evidence Validation
   ↓
Trend Candidate
```

---

# 20. TREND ENTITY

Estrutura mínima:

```text
Trend
├── id
├── name
├── description
├── mechanism
├── lifecycle
├── first_seen_at
├── last_seen_at
├── score
├── confidence
├── signals
├── evidence
├── clusters
├── niches
└── status
```

---

# 21. TREND MECHANISM

O sistema deverá tentar identificar:

```text
hook
format
structure
visual_pattern
audio_pattern
narrative_pattern
behavior
cta
emotion
```

A trend deverá ser abstraída de modo que possa ser adaptada sem copiar o conteúdo original.

---

# 22. TREND LIFECYCLE

Estados oficiais:

```text
UNKNOWN
EMERGING
GROWING
MAINSTREAM
SATURATED
DECLINING
EXPIRED
```

Transições deverão ser determinadas por evidências e regras versionadas.

---

# 23. TEMPORAL INTELLIGENCE

O sistema deverá registrar séries temporais sempre que os dados permitirem.

Exemplos:

```text
content_count(t)
creator_count(t)
engagement(t)
adoption(t)
cross_niche_count(t)
```

O Trend Engine deverá conseguir calcular:

```text
growth
velocity
acceleration
```

quando houver dados suficientes.

---

# 24. TREND VS VIRAL

O sistema deverá distinguir:

### Viral isolado

```text
alto alcance
baixa replicação
baixa diversidade
```

### Tendência

```text
replicação
múltiplos conteúdos
múltiplos criadores
crescimento
padrão reconhecível
```

A classificação deverá ser testável.

---

# 25. TREND SCORE

Versão inicial:

```text
Growth Velocity       25%
Adoption              20%
Recency               15%
Cross-Niche Spread    10%
Engagement            10%
Similarity             10%
Adaptability           10%
```

Os pesos deverão ser configuráveis.

Nenhum peso deverá ficar hardcoded em múltiplos pontos do código.

---

# 26. CONFIDENCE SCORE

Confidence deverá representar confiança na conclusão.

Exemplo:

```text
Trend Score: 91
Confidence: 86%
```

Trend Score e Confidence são conceitos distintos.

---

# 27. SCORE VERSIONING

Toda pontuação deverá possuir versão.

Exemplo:

```text
trend-score-v1
```

Se o algoritmo mudar:

```text
trend-score-v2
```

Resultados históricos não deverão ser silenciosamente reescritos.

---

# 28. CROSS-NICHE DETECTION

O sistema deverá identificar expansão entre nichos.

Exemplo:

```text
Fitness
   ↓
Lifestyle
   ↓
Beauty
   ↓
Education
```

A expansão deverá ser registrada como sinal.

---

# 29. CLIENT DNA

O Client DNA deverá conter:

```text
business
niche
audience
positioning
objectives
tone
topics
preferred_formats
forbidden_topics
brand_rules
competitors
historical_preferences
```

---

# 30. CLIENT MATCHING

Uma trend deverá poder ser avaliada contra um cliente:

```text
Trend
   ↓
Client Matcher
   ↓
Match Score
```

O resultado deverá possuir:

```text
score
positive_factors
negative_factors
explanation
confidence
```

---

# 31. MATCH EXPLANATION

Nunca retornar apenas:

```text
match = 92
```

Deverá retornar algo equivalente a:

```text
MATCH: 92

WHY:
- formato compatível;
- tema relacionado ao nicho;
- público potencialmente compatível;
- baixa saturação no nicho.

RISKS:
- tendência em crescimento rápido;
- janela de oportunidade possivelmente curta.
```

---

# 32. AI GATEWAY

O AI Gateway deverá abstrair:

```text
LLM provider
model selection
fallback
retry
timeout
structured output
token usage
cost
prompt version
request ID
```

---

# 33. AI REQUEST CONTRACT

Cada chamada de IA deverá possuir:

```text
request_id
model
provider
prompt_version
input_tokens
output_tokens
latency
status
cost
```

Quando disponível.

---

# 34. STRUCTURED AI OUTPUT

A aplicação não deverá depender de parsing frágil de texto livre quando o resultado puder ser estruturado.

Preferência:

```text
JSON Schema
Pydantic
structured output
```

---

# 35. AI RESPONSIBILITIES

A IA poderá:

* interpretar padrões;
* abstrair mecanismos;
* classificar;
* explicar;
* sugerir adaptações;
* resumir evidências;
* auxiliar ranking.

A IA não poderá:

* inventar evidências;
* inventar métricas;
* afirmar uma trend sem dados;
* substituir integralmente os sinais objetivos.

---

# 36. AI ADAPTATION ENGINE

Entrada:

```text
Trend
+
Client DNA
```

Saída:

```text
Original Concept
+
Hook
+
Creative Direction
+
Suggested Format
+
Adaptation Rationale
```

A adaptação deverá representar o mecanismo da trend, não uma cópia do conteúdo de referência.

---

# 37. AUTONOMOUS SCOUT JOB

O job deverá executar:

```text
schedule
 ↓
discover
 ↓
collect
 ↓
normalize
 ↓
analyze
 ↓
cluster
 ↓
detect
 ↓
validate
 ↓
score
 ↓
match
 ↓
curate
```

Cada etapa deverá ser observável.

---

# 38. JOB IDEMPOTENCY

Executar o mesmo job duas vezes não deverá criar duplicações indevidas.

Deverão existir mecanismos de:

```text
deduplication
idempotency key
external_id
source identity
```

---

# 39. ATTENTION BUDGET

O sistema deverá permitir:

```text
Top 5
Top 10
Top 20
```

O padrão inicial deverá ser pequeno o suficiente para preservar a atenção humana.

---

# 40. RADAR

A interface principal deverá apresentar:

```text
Today's Radar

New
Growing
High Opportunity
Needs Attention
```

Cada card deverá permitir acesso às evidências.

---

# 41. TREND CARD

Informações mínimas:

```text
name
lifecycle
trend score
confidence
growth
first seen
evidence count
why now
why relevant
mechanism
adaptation
risk
```

---

# 42. EXPLAINABILITY CONTRACT

Toda recomendação deverá responder:

```text
O que foi detectado?
Por que é uma trend?
Por que agora?
Por que este cliente?
Quais evidências existem?
Qual é o risco?
```

Se alguma resposta não puder ser determinada:

```text
insufficient evidence
```

---

# 43. FEEDBACK

Feedback mínimo:

```text
EXCELLENT
INTERESTING
NOT_SURE
NOT_RELEVANT
NEVER_SHOW
```

Feedback deverá ser persistido.

---

# 44. LEARNING LOOP

Fluxo:

```text
Feedback
   ↓
Preference Signals
   ↓
Preference Profile
   ↓
Ranking Adjustment
```

O aprendizado não deverá alterar silenciosamente o score objetivo da trend.

Deverá existir separação:

```text
Objective Trend Score
+
Personalized Ranking
```

---

# 45. OBSERVABILIDADE

Todo processamento deverá permitir rastrear:

```text
job_id
source_id
content_id
trend_id
client_id
ai_request_id
correlation_id
```

---

# 46. LOGGING

Logs deverão ser:

* estruturados;
* pesquisáveis;
* sem secrets;
* sem tokens;
* sem senhas;
* sem dados pessoais desnecessários.

---

# 47. MÉTRICAS OBRIGATÓRIAS

Mínimo:

```text
discovery_jobs_total
discovery_jobs_failed
source_health
contents_discovered
contents_normalized
contents_analyzed
clusters_created
trend_candidates
validated_trends
false_positive_feedback
trend_processing_latency
ai_requests
ai_cost
recommendations_generated
recommendations_accepted
```

---

# 48. SEGURANÇA

Obrigatório:

```text
secret management
HTTPS
authentication
authorization
rate limiting
audit logs
input validation
dependency scanning
```

Nunca armazenar senha de redes sociais.

---

# 49. LGPD

Deverá existir capacidade arquitetural para:

```text
data minimization
retention policy
deletion
access control
auditability
```

---

# 50. TESTING CONTRACT

O projeto deverá possuir:

```text
unit tests
integration tests
contract tests
e2e tests
```

Cada fase deverá especificar seus próprios critérios.

---

# 51. DETERMINISMO

Componentes algorítmicos deverão ser determinísticos sempre que possível.

Quando IA generativa for utilizada:

```text
temperature
model
prompt
schema
version
```

deverão ser controláveis ou registráveis.

---

# 52. TEST DATA

Nenhum teste crítico deverá depender exclusivamente de dados externos em tempo real.

Deverão existir:

```text
fixtures
snapshots
mock connectors
synthetic datasets
recorded responses
```

---

# 53. PHASE -1

# DISCOVERY FEASIBILITY

Esta é a fase mais importante do projeto.

Objetivo:

> Determinar se conseguimos realizar Discovery autônomo de forma tecnicamente sustentável antes de construir o produto inteiro.

---

## 53.1 O que deve ser testado

Para cada abordagem candidata:

```text
coverage
reliability
freshness
metadata
metrics
rate limits
cost
stability
legal/terms compatibility
operational complexity
```

---

## 53.2 Não escolher tecnologia por preferência

O agente deverá testar alternativas reais.

A decisão deverá ser baseada em evidência.

---

## 53.3 Discovery Matrix

Deverá ser produzido:

```text
Source
Method
Coverage
Freshness
Metadata
Metrics
Reliability
Cost
Risk
Recommendation
```

---

## 53.4 Acceptance Criteria — PHASE -1

PASS somente se:

* [ ] Existe pelo menos um mecanismo funcional de discovery.
* [ ] O mecanismo pode ser executado sem pesquisa manual da usuária.
* [ ] Conteúdo real ou dataset representativo pode ser coletado.
* [ ] Os dados podem ser normalizados.
* [ ] Existe identificação de duplicidade.
* [ ] Existe timestamp.
* [ ] É possível executar discovery repetidamente.
* [ ] O método possui comportamento observável.
* [ ] Os limites operacionais foram documentados.
* [ ] Custos foram estimados.
* [ ] Riscos foram documentados.
* [ ] Existe plano de fallback.
* [ ] A abordagem escolhida não exige armazenar senha da usuária.
* [ ] O resultado foi reproduzível em mais de uma execução.
* [ ] Existe evidência suficiente para iniciar o MVP.

### BLOCKER

Se nenhum mecanismo sustentável de discovery for comprovado:

```text
PHASE -1 = BLOCKER
```

Nenhuma fase posterior de produto deverá avançar.

---

# 54. PHASE 0

# FOUNDATION

Implementar:

```text
repository
project structure
Docker
configuration
database
migrations
CI
logging
observability
test framework
```

### Acceptance Criteria

* [ ] Projeto inicia em ambiente limpo.
* [ ] Docker sobe todos os serviços obrigatórios.
* [ ] Database conecta.
* [ ] Migration funciona.
* [ ] Test suite executa.
* [ ] CI executa.
* [ ] Health endpoint funciona.
* [ ] Logging estruturado funciona.
* [ ] Configuração não contém secrets hardcoded.
* [ ] README permite reproduzir ambiente.

---

# 55. PHASE 1

# DISCOVERY INFRASTRUCTURE

Implementar:

```text
TrendSource
SourceRegistry
DiscoveryQuery
DiscoveryJob
job execution
idempotency
```

### Acceptance Criteria

* [ ] Connector pode ser registrado.
* [ ] Connector pode ser substituído.
* [ ] Discovery Job pode ser criado.
* [ ] Job possui ID.
* [ ] Job possui status.
* [ ] Job pode falhar sem derrubar aplicação.
* [ ] Job pode ser reexecutado.
* [ ] Duplicação é controlada.
* [ ] Health check funciona.
* [ ] Capabilities são expostas.
* [ ] Nenhum domínio depende do connector concreto.

---

# 56. PHASE 2

# SOURCE + EVIDENCE

Implementar:

```text
RawContent
NormalizedContent
Evidence
deduplication
source metadata
```

### Acceptance Criteria

* [ ] Conteúdo bruto é preservado.
* [ ] Conteúdo normalizado possui schema estável.
* [ ] IDs externos são preservados.
* [ ] Timestamp é preservado.
* [ ] Duplicatas são detectadas.
* [ ] Evidências podem ser associadas ao conteúdo.
* [ ] Dados ausentes são tratados.
* [ ] Não existe corrupção silenciosa de dados.

---

# 57. PHASE 3

# CONTENT INTELLIGENCE

Implementar:

```text
classification
metadata extraction
embeddings
multimodal abstraction
```

### Acceptance Criteria

* [ ] Conteúdo recebe classificação.
* [ ] Embedding pode ser gerado.
* [ ] Provider pode ser substituído.
* [ ] Falha de IA não perde RawContent.
* [ ] Resultados possuem versão.
* [ ] Structured output é validado.
* [ ] Custos de IA são rastreáveis.
* [ ] Testes cobrem falhas de provider.

---

# 58. PHASE 4

# TEMPORAL INTELLIGENCE

Implementar:

```text
time series
growth
velocity
acceleration
adoption
```

### Acceptance Criteria

* [ ] Métricas possuem timestamp.
* [ ] Sistema consegue comparar períodos.
* [ ] Crescimento pode ser calculado.
* [ ] Dados insuficientes não geram falsa confiança.
* [ ] Cálculos possuem testes.
* [ ] Algoritmos são versionados.
* [ ] Resultados históricos permanecem auditáveis.

---

# 59. PHASE 5

# TREND ENGINE

Implementar:

```text
clustering
pattern detection
candidate generation
trend validation
viral vs trend
lifecycle
```

### Acceptance Criteria

* [ ] Conteúdos podem formar clusters.
* [ ] Cluster não é automaticamente trend.
* [ ] Candidate Trend é gerado.
* [ ] Evidence Engine valida candidatos.
* [ ] Viral isolado pode ser classificado separadamente.
* [ ] Lifecycle é calculado.
* [ ] Trend possui evidências.
* [ ] Trend possui timestamps.
* [ ] Trend pode evoluir.
* [ ] Trend expirada não permanece como emergente sem evidência.

---

# 60. PHASE 6

# SCORING + CONFIDENCE

Implementar:

```text
Trend Score
Confidence
score version
ranking
explanations
```

### Acceptance Criteria

* [ ] Pesos são configuráveis.
* [ ] Score é reproduzível.
* [ ] Confidence é separada do Score.
* [ ] Score possui versão.
* [ ] Componentes do Score são observáveis.
* [ ] Sistema explica a pontuação.
* [ ] Dados insuficientes reduzem confidence.
* [ ] Nenhuma métrica inexistente é inventada.

---

# 61. PHASE 7

# CLIENT DNA

Implementar:

```text
Client
ClientDNA
preferences
brand rules
```

### Acceptance Criteria

* [ ] Cliente pode ser criado.
* [ ] Client DNA pode ser configurado.
* [ ] Preferências são persistidas.
* [ ] Regras proibitivas são respeitadas.
* [ ] Dados de um cliente não vazam para outro.
* [ ] Histórico pode ser associado ao cliente.

---

# 62. PHASE 8

# CLIENT MATCHING

Implementar:

```text
Trend Match
Match Score
explanation
```

### Acceptance Criteria

* [ ] Trend pode ser avaliada para cliente.
* [ ] Match Score é calculado.
* [ ] Fatores positivos são explicados.
* [ ] Fatores negativos são explicados.
* [ ] Confidence é apresentada.
* [ ] Ranking por cliente funciona.
* [ ] Tendências incompatíveis podem ser filtradas.

---

# 63. PHASE 9

# AI ADAPTATION

Implementar:

```text
concept generation
hook generation
creative direction
format adaptation
```

### Acceptance Criteria

* [ ] Trend pode gerar adaptação.
* [ ] Cliente influencia adaptação.
* [ ] Resultado é estruturado.
* [ ] Conteúdo original não é simplesmente copiado.
* [ ] Fonte da inspiração é identificável.
* [ ] IA não pode inventar dados da trend.
* [ ] Prompt possui versão.
* [ ] Resultado possui rastreabilidade.

---

# 64. PHASE 10

# RADAR

Implementar:

```text
dashboard
trend cards
filters
evidence view
```

### Acceptance Criteria

* [ ] Usuária consegue abrir Radar.
* [ ] Radar apresenta tendências priorizadas.
* [ ] Attention Budget funciona.
* [ ] Trend Card mostra Score.
* [ ] Confidence aparece.
* [ ] Evidências podem ser consultadas.
* [ ] "Why now?" existe.
* [ ] "Why relevant?" existe.
* [ ] Riscos aparecem.
* [ ] Nenhuma recomendação é apresentada sem evidência mínima.

---

# 65. PHASE 11

# FEEDBACK

Implementar:

```text
feedback
negative signals
preference capture
```

### Acceptance Criteria

* [ ] Feedback pode ser registrado.
* [ ] Feedback possui timestamp.
* [ ] Feedback está associado à trend.
* [ ] Feedback está associado ao cliente.
* [ ] Feedback negativo influencia futuras recomendações.
* [ ] "Never show" é respeitado.
* [ ] Feedback não altera retroativamente a evidência histórica.

---

# 66. PHASE 12

# LEARNING ENGINE

Implementar:

```text
Preference Profile
Personalized Ranking
historical signals
```

### Acceptance Criteria

* [ ] Preferências podem ser inferidas.
* [ ] Ranking personalizado funciona.
* [ ] Score objetivo permanece separado.
* [ ] Personalização é explicável.
* [ ] Mudanças podem ser auditadas.
* [ ] Cold start funciona.
* [ ] Pouco feedback não gera overfitting.

---

# 67. PHASE 13

# AUTONOMOUS SCOUT

Implementar:

```text
scheduled jobs
continuous discovery
early signals
automatic ranking
```

### Acceptance Criteria

* [ ] Scout executa sem intervenção humana.
* [ ] Jobs são agendáveis.
* [ ] Falhas possuem retry.
* [ ] Falhas persistentes geram alerta.
* [ ] Discovery pode rodar continuamente.
* [ ] Early signals são detectados.
* [ ] Radar é atualizado automaticamente.
* [ ] Nenhuma etapa exige intervenção manual.

---

# 68. PHASE 14

# NOTIFICATIONS

Implementar inicialmente infraestrutura preparada para:

```text
email
push
future messaging
```

### Acceptance Criteria

* [ ] Notificação é disparada por regra.
* [ ] Usuária pode configurar preferências.
* [ ] Duplicação é controlada.
* [ ] Falha de notificação não interrompe discovery.
* [ ] Eventos são auditáveis.

---

# 69. PHASE 15

# ADDITIONAL SOURCES + PRODUCTION HARDENING

Possíveis fontes:

```text
TikTok
Reddit
Google Trends
Pinterest
Web expansion
```

### Acceptance Criteria

* [ ] Nova fonte pode ser adicionada sem alterar Trend Domain.
* [ ] Source Capabilities funcionam.
* [ ] Evidence Engine aceita múltiplas fontes.
* [ ] Cross-source validation funciona.
* [ ] Rate limiting funciona.
* [ ] Observabilidade está completa.
* [ ] Segurança foi auditada.
* [ ] Recovery foi testado.
* [ ] Custos são mensuráveis.
* [ ] Performance possui baseline.

---

# 70. API CONTRACT

Endpoints iniciais:

```text
GET    /api/v1/health

GET    /api/v1/trends
GET    /api/v1/trends/{id}

GET    /api/v1/trends/{id}/evidence
GET    /api/v1/trends/{id}/adaptations

POST   /api/v1/clients
GET    /api/v1/clients
GET    /api/v1/clients/{id}
PATCH  /api/v1/clients/{id}

GET    /api/v1/clients/{id}/radar

POST   /api/v1/trends/{id}/feedback

GET    /api/v1/sources
GET    /api/v1/sources/{id}/health
```

Os contratos finais deverão possuir schemas versionados.

---

# 71. JOB STATES

Jobs deverão utilizar estados explícitos:

```text
PENDING
RUNNING
COMPLETED
FAILED
RETRYING
CANCELLED
BLOCKED
```

---

# 72. TREND STATES

```text
UNKNOWN
EMERGING
GROWING
MAINSTREAM
SATURATED
DECLINING
EXPIRED
```

---

# 73. AUDIT STATES

Toda fase será classificada como:

```text
PASS
FAIL
BLOCKER
```

---

# 74. PASS

Uma fase recebe PASS quando:

* todos os acceptance criteria obrigatórios passam;
* testes passam;
* comportamento esperado foi demonstrado;
* não existem blockers conhecidos;
* documentação está atualizada.

---

# 75. FAIL

Uma fase recebe FAIL quando:

* existe requisito não implementado;
* teste obrigatório falha;
* comportamento diverge do contrato;
* qualidade insuficiente impede aceitação.

FAIL significa:

```text
corrigir antes de avançar
```

---

# 76. BLOCKER

BLOCKER significa:

> O problema compromete a viabilidade, segurança, arquitetura ou premissa fundamental do produto.

Exemplos:

```text
discovery não funciona
dados não podem ser coletados
fonte é operacionalmente inviável
trend engine não consegue distinguir sinal de ruído
arquitetura ficou acoplada ao provider
dados podem ser falsificados/inventados
falha grave de segurança
```

BLOCKER impede avanço.

---

# 77. DEFINITION OF DONE

Uma fase só está DONE quando:

* [ ] Código implementado.
* [ ] Testes implementados.
* [ ] Testes passam.
* [ ] Acceptance Criteria verificados.
* [ ] Logs disponíveis.
* [ ] Erros tratados.
* [ ] Documentação atualizada.
* [ ] Migration criada quando necessária.
* [ ] API documentada quando aplicável.
* [ ] Observabilidade implementada.
* [ ] Nenhuma regra crítica ficou hardcoded indevidamente.
* [ ] Não existem TODOs críticos.
* [ ] Auditoria executada.
* [ ] Resultado classificado PASS/FAIL/BLOCKER.

---

# 78. REGRA DO AGENTE DE CÓDIGO

O agente deverá trabalhar:

```text
ONE PHASE AT A TIME
```

Não deverá implementar várias fases simultaneamente sem autorização.

Fluxo:

```text
READ CONTRACT
      ↓
INSPECT REPOSITORY
      ↓
IMPLEMENT
      ↓
TEST
      ↓
AUDIT
      ↓
REPORT
```

---

# 79. FORMATO OBRIGATÓRIO DE REPORT

Ao concluir cada fase, o agente deverá responder:

```text
PHASE: X
STATUS: PASS / FAIL / BLOCKER

IMPLEMENTED:
- ...

TESTS:
- ...

ACCEPTANCE CRITERIA:
- PASS: ...
- PASS: ...
- FAIL: ...

FILES CHANGED:
- ...

MIGRATIONS:
- ...

RISKS:
- ...

KNOWN LIMITATIONS:
- ...

NEXT PHASE:
- ...
```

Não deverá responder apenas:

```text
Done.
```

---

# 80. PROIBIÇÕES DO AGENTE

O agente não deverá:

* alterar requisitos silenciosamente;
* remover testes para obter PASS;
* reduzir acceptance criteria;
* ignorar falhas;
* mascarar exceções;
* inventar integração funcional;
* declarar provider funcional sem teste;
* criar credenciais fictícias como se fossem reais;
* substituir requisitos por mocks permanentes;
* considerar TODO como implementação;
* considerar endpoint criado como feature concluída;
* considerar código compilando como fase concluída.

---

# 81. MOCKS

Mocks são permitidos para:

```text
unit tests
integration isolation
local development
provider simulation
```

Mocks não podem ser utilizados para declarar uma integração real como concluída.

---

# 82. EXTERNAL DEPENDENCY RULE

Quando uma dependência externa não estiver disponível:

```text
STATUS = BLOCKED
```

ou:

```text
PARTIAL IMPLEMENTATION
```

Nunca:

```text
PASS
```

sem evidência real.

---

# 83. MIGRATIONS

Toda alteração estrutural de banco deverá possuir migration.

Nunca modificar schema de produção manualmente sem migration correspondente.

---

# 84. CONFIGURATION

Configuração deverá ser centralizada.

Exemplos:

```text
database
redis
AI provider
embedding provider
source credentials
feature flags
scoring weights
scheduler
```

Pesos e limites importantes não deverão estar espalhados pelo código.

---

# 85. FEATURE FLAGS

Funcionalidades potencialmente arriscadas deverão poder ser desabilitadas.

Exemplos:

```text
ENABLE_INSTAGRAM
ENABLE_WEB
ENABLE_AUTONOMOUS_SCOUT
ENABLE_AI_ADAPTATION
ENABLE_LEARNING
```

---

# 86. SOURCE HEALTH

Cada source deverá possuir:

```text
UP
DEGRADED
DOWN
BLOCKED
UNKNOWN
```

O Scout não deverá continuar enviando chamadas indiscriminadamente a uma fonte conhecida como DOWN.

---

# 87. RETRY POLICY

Retries deverão:

* possuir limite;
* utilizar backoff;
* distinguir erros permanentes de temporários;
* gerar logs;
* gerar métricas.

---

# 88. RATE LIMITING

Cada connector deverá respeitar seus limites conhecidos.

O sistema deverá registrar:

```text
requests
success
failure
rate limit
retry
```

---

# 89. DATA QUALITY

Deverá existir validação para:

```text
missing IDs
invalid timestamps
duplicate content
corrupted metadata
invalid metrics
```

Dados inválidos não deverão contaminar silenciosamente o Trend Engine.

---

# 90. EVIDENCE INTEGRITY

Toda evidência deverá poder responder:

```text
De onde veio?
Quando foi observada?
Qual conteúdo originou?
Qual métrica existia naquele momento?
```

---

# 91. NO HALLUCINATED METRICS RULE

A IA nunca poderá preencher:

```text
views
likes
shares
growth
creator count
adoption
```

com valores estimados apresentados como dados reais.

Se o valor não existir:

```text
UNKNOWN
```

---

# 92. TREND CONFIDENCE RULE

Confidence alta exige evidência suficiente.

Exemplo conceitual:

```text
1 conteúdo
→ baixa confidence

3 conteúdos
→ ainda baixa

múltiplos criadores
+
crescimento
+
repetição
+
tempo
→ confidence maior
```

Os thresholds deverão ser definidos e testados durante implementação.

---

# 93. EARLY SIGNAL RULE

O produto deverá privilegiar sinais que apresentem:

```text
growth
+
replication
+
recency
```

em vez de simplesmente:

```text
highest views
```

---

# 94. ATTENTION QUALITY RULE

Uma recomendação não será considerada boa simplesmente por ter alto Trend Score.

Ela deverá possuir:

```text
relevance
+
actionability
+
confidence
```

---

# 95. PRODUCT SUCCESS METRICS

Métricas fundamentais:

```text
Discovery Precision
Discovery Recall
False Positive Rate
Useful Opportunities
Time Saved
Recommendation Adoption
Feedback Quality
```

---

# 96. NORTH STAR METRIC

# Useful Opportunities per Hour Saved

Definição operacional:

> Quantidade de oportunidades consideradas úteis em relação ao tempo de pesquisa manual eliminado pelo sistema.

---

# 97. GO / NO-GO GATES

## Gate 1 — Discovery

Pergunta:

> Conseguimos descobrir conteúdo automaticamente?

Não:

```text
NO-GO
```

---

## Gate 2 — Evidence

Pergunta:

> Conseguimos sustentar uma trend com evidências?

Não:

```text
NO-GO
```

---

## Gate 3 — Trend Detection

Pergunta:

> Conseguimos distinguir tendência de viral isolado/ruído?

Não:

```text
NO-GO
```

---

## Gate 4 — Personalization

Pergunta:

> Conseguimos determinar se uma trend é relevante para um cliente?

Não:

```text
NO-GO
```

---

## Gate 5 — Actionability

Pergunta:

> Conseguimos transformar a trend em uma oportunidade acionável?

Não:

```text
FAIL
```

---

# 98. MVP DE VERDADE

O MVP não será:

```text
dashboard bonito
+
cards
+
LLM
```

O MVP será:

```text
AUTONOMOUS DISCOVERY
+
EVIDENCE
+
TREND DETECTION
+
SCORING
+
CLIENT MATCHING
```

A interface será construída para expor essas capacidades.

---

# 99. CRITÉRIO MÁXIMO DE VALIDAÇÃO

Uma Social Media deverá conseguir executar o seguinte fluxo:

```text
ABRIR O AI TREND SCOUT
        ↓
VER O RADAR
        ↓
ENCONTRAR UMA TREND QUE ELA NÃO PROCUROU
        ↓
ENTENDER POR QUE É UMA TREND
        ↓
VER AS EVIDÊNCIAS
        ↓
ENTENDER POR QUE SERVE PARA SEU CLIENTE
        ↓
GERAR UMA ADAPTAÇÃO ORIGINAL
```

Se esse fluxo funcionar, o produto estará resolvendo a dor central.

---

# 100. TESTE DE REALIDADE

Antes de declarar o MVP pronto, executar:

## Teste A — Zero Input

Usuária não fornece nenhuma trend.

Resultado esperado:

```text
sistema encontra oportunidades sozinho
```

---

## Teste B — Noise

Dataset contém:

```text
virais isolados
spam
conteúdo antigo
duplicatas
```

Resultado esperado:

```text
não transformar tudo em trend
```

---

## Teste C — Emerging Trend

Dataset contém uma tendência pequena, porém crescente.

Resultado esperado:

```text
EMERGING / GROWING
```

e não:

```text
UNKNOWN
```

---

## Teste D — Saturated Trend

Dataset contém trend amplamente utilizada.

Resultado esperado:

```text
MAINSTREAM / SATURATED
```

---

## Teste E — Cross-Niche

Trend nasce em um nicho e começa a aparecer em outros.

Resultado esperado:

```text
CROSS_NICHE SIGNAL
```

---

## Teste F — Client Fit

Trend relevante para Cliente A e irrelevante para Cliente B.

Resultado esperado:

```text
A → alto match
B → baixo match
```

---

## Teste G — Evidence Failure

Trend possui evidência insuficiente.

Resultado esperado:

```text
LOW CONFIDENCE
```

e nunca:

```text
TREND CONFIRMED
```

---

# 101. AUDITORIA FINAL

Antes do release do MVP:

```text
ARCHITECTURE
DATA
DISCOVERY
EVIDENCE
AI
TREND ENGINE
SCORING
CLIENT MATCHING
SECURITY
OBSERVABILITY
TESTING
COST
```

deverão ser auditados.

---

# 102. AUDIT RESULT

Formato:

```text
AI TREND SCOUT
MVP AUDIT

DISCOVERY: PASS
EVIDENCE: PASS
TREND ENGINE: PASS
SCORING: PASS
CLIENT MATCHING: PASS
AI: PASS
SECURITY: PASS
OBSERVABILITY: PASS

FINAL STATUS:
PASS
```

Qualquer componente crítico em:

```text
FAIL
```

impede release.

Qualquer componente fundamental em:

```text
BLOCKER
```

impede avanço.

---

# 103. O QUE NÃO É MVP

Não é obrigatório inicialmente:

```text
TikTok
Reddit
WhatsApp
mobile app
advanced notifications
complex billing
multi-tenant enterprise
automatic publishing
```

Esses itens podem ser posteriores.

---

# 104. O QUE É INEGOCIÁVEL

É obrigatório:

```text
AUTONOMOUS DISCOVERY
EVIDENCE
TREND DETECTION
TEMPORAL INTELLIGENCE
SCORING
CONFIDENCE
CLIENT MATCHING
EXPLAINABILITY
FEEDBACK
OBSERVABILITY
TESTING
```

---

# 105. DECISÃO ARQUITETURAL CENTRAL

O produto não será:

```text
Content Analyzer
```

Nem:

```text
Trend Dashboard
```

Nem:

```text
LLM Wrapper
```

Nem:

```text
Social Media Search Tool
```

O produto será:

# AUTONOMOUS TREND DISCOVERY ENGINE

com uma camada de inteligência específica para Social Media.

---

# 106. DEFINIÇÃO FINAL DO SISTEMA

```text
                    AI TREND SCOUT

                         │
                         ▼

                 AUTONOMOUS SCOUT
                         │
                         ▼
                    DISCOVERY
                         │
                         ▼
                     CONTENT
                         │
                         ▼
                  INTELLIGENCE
                         │
                         ▼
                     SIGNALS
                         │
                         ▼
                     CLUSTERS
                         │
                         ▼
                  TREND CANDIDATE
                         │
                         ▼
                     EVIDENCE
                         │
                         ▼
                  TEMPORAL ENGINE
                         │
                         ▼
                  TREND VALIDATION
                         │
                         ▼
                  SCORE + CONFIDENCE
                         │
                         ▼
                    CLIENT DNA
                         │
                         ▼
                    MATCHING
                         │
                         ▼
                     CURATOR
                         │
                         ▼
                    AI ADAPTATION
                         │
                         ▼
                       RADAR
                         │
                         ▼
                     FEEDBACK
                         │
                         ▼
                     LEARNING
                         │
                         └──────────────► DISCOVERY
```

---

# 107. REGRA FINAL DO CONTRATO

> **O AI Trend Scout só estará cumprindo sua missão quando conseguir encontrar, validar, priorizar e explicar oportunidades que a usuária não procurou manualmente.**

A existência de um dashboard não prova o produto.

A existência de uma integração com Instagram não prova o produto.

A existência de um LLM não prova o produto.

A existência de centenas de trends no banco não prova o produto.

O que prova o produto é:

```text
A IA encontrou.
A IA validou.
A IA entendeu.
A IA priorizou.
A IA explicou.
A IA adaptou.
```

sem exigir que a Social Media faça novamente o trabalho que o produto foi criado para eliminar.

---

# STATUS DO IMPLEMENTATION CONTRACT

```text
DOCUMENT: AI Trend Scout — Implementation Contract V1.0

BLUEPRINT BASE: V1.2

ARCHITECTURE: DEFINED
DOMAIN: DEFINED
DISCOVERY CONTRACT: DEFINED
EVIDENCE CONTRACT: DEFINED
TREND ENGINE: DEFINED
TEMPORAL INTELLIGENCE: DEFINED
SCORING: DEFINED
CLIENT DNA: DEFINED
AI GATEWAY: DEFINED
FEEDBACK: DEFINED
OBSERVABILITY: DEFINED
SECURITY: DEFINED
TESTING: DEFINED
PHASES: DEFINED
ACCEPTANCE CRITERIA: DEFINED
AUDIT PROTOCOL: DEFINED
GO/NO-GO: DEFINED

CURRENT STATUS:
READY FOR PHASE -1

NEXT ACTION:
IMPLEMENT PHASE -1 ONLY
```

**Regra operacional a partir deste ponto:** o agente de desenvolvimento não deve começar pelas telas, pelo dashboard ou pelo LLM. Deve começar pela **Fase -1 — Discovery Feasibility**, produzir a matriz de viabilidade das fontes/métodos e somente avançar se o resultado for **PASS**.
