# BLUEPRINT V1.2

# AI Trend Scout

**Status:** Proposed / Implementation Candidate
**Versão:** 1.2
**Data:** 19/08/2026
**Objetivo:** Automatizar a descoberta, análise, priorização e adaptação de tendências para Social Media.

---

# 1. VISÃO DO PRODUTO

## 1.1 Problema

Social Medias gastam uma quantidade significativa de tempo:

* navegando pelo Instagram;
* procurando Reels;
* acompanhando criadores;
* observando concorrentes;
* procurando novos formatos;
* identificando áudios;
* monitorando hashtags;
* procurando referências;
* tentando descobrir o que está começando a viralizar;
* avaliando se algo é realmente uma tendência ou apenas um conteúdo isoladamente viral.

O problema não é falta de informação.

É **excesso de informação + necessidade de atenção humana**.

---

# 2. A SOLUÇÃO

O AI Trend Scout será um sistema de **descoberta autônoma de tendências**.

A aplicação deverá buscar sinais automaticamente, analisar grandes volumes de conteúdo, identificar padrões emergentes e apresentar somente as oportunidades consideradas relevantes.

### Princípio fundamental

> **A Social Media não deve procurar a tendência. A IA deve procurar por ela.**

---

# 3. OBJETIVO PRINCIPAL

Transformar:

```text
MILHÕES DE CONTEÚDOS
        ↓
SINAIS
        ↓
PADRÕES
        ↓
TRENDS
        ↓
OPORTUNIDADES
        ↓
CONTEÚDO ACIONÁVEL
```

A usuária deve receber:

> **"Encontrei isso para você."**

e não:

> "Procure isso."

---

# 4. PRINCÍPIO #1 — HUMAN ATTENTION IS EXPENSIVE

O sistema deve otimizar o tempo da Social Media.

Não é objetivo:

```text
mostrar 500 trends
```

É objetivo:

```text
encontrar 5–10 oportunidades realmente relevantes
```

A qualidade da curadoria é mais importante que quantidade.

---

# 5. PRINCÍPIO #2 — VIRAL ≠ TREND

Um conteúdo com milhões de visualizações não necessariamente representa uma tendência.

### Viral isolado

```text
1 criador
1 conteúdo
alto alcance
```

Resultado:

```text
VIRAL
```

### Trend

```text
múltiplos criadores
múltiplos conteúdos
crescimento temporal
padrão replicável
adoção crescente
```

Resultado:

```text
TREND
```

O sistema deverá tratar esses conceitos separadamente.

---

# 6. PRINCÍPIO #3 — DETECTAR O MECANISMO

A IA não deverá apenas identificar:

> "Este Reel está viralizando."

Ela deverá identificar:

```text
HOOK
FORMAT
STRUCTURE
AUDIO
EDITING
VISUAL PATTERN
CTA
EMOTION
TOPIC
BEHAVIOR
```

Porque o verdadeiro ativo é o **mecanismo criativo replicável**.

---

# 7. PRINCÍPIO #4 — NÃO DEPENDER DE UMA ÚNICA PLATAFORMA

Instagram é a prioridade do produto.

Porém:

**Instagram não deve ser o núcleo arquitetural.**

A arquitetura deverá permitir:

```text
Instagram
TikTok
Reddit
Google Trends
Web
Pinterest
YouTube
outros
```

sem modificar o Trend Engine.

---

# 8. PRIORIDADE DAS FONTES

## Tier 1 — MVP

### Instagram

Fonte prioritária.

Objetivo:

* Reels;
* posts;
* criadores;
* hashtags;
* formatos;
* sinais de crescimento;
* conteúdo público acessível;
* descoberta.

### Web

Fonte complementar.

Objetivo:

* notícias;
* artigos;
* páginas;
* blogs;
* tendências emergentes;
* referências externas.

---

## Tier 2

Posteriormente:

```text
TikTok
Reddit
Google Trends
Pinterest
YouTube
```

---

# 9. REQUISITO FUNDAMENTAL DE COLETA

O sistema **não poderá assumir acesso irrestrito ao Instagram**.

O Connector deverá trabalhar exclusivamente com mecanismos que sejam:

* tecnicamente viáveis;
* sustentáveis;
* autorizados para o uso pretendido;
* observáveis;
* substituíveis.

### Proibido arquiteturalmente

Criar dependência crítica de:

```text
login da usuária
+
senha
+
browser automation
+
scroll infinito
```

como mecanismo obrigatório do produto.

---

# 10. DISCOVERY LAYER

O sistema terá uma camada independente chamada:

# Discovery Layer

Responsável por descobrir candidatos.

```text
                   DISCOVERY
                       │
        ┌──────────────┼───────────────┐
        ↓              ↓               ↓
   Instagram        Web          Future Sources
        │              │
        └──────────────┼───────────────┘
                       ↓
                 Raw Content
```

---

# 11. SOURCE CONNECTOR CONTRACT

Todos os conectores deverão implementar uma interface comum.

```python
class TrendSource(Protocol):

    async def discover(
        self,
        query: DiscoveryQuery
    ) -> list[RawContent]:
        ...

    async def health_check(self) -> SourceHealth:
        ...

    async def capabilities(self) -> SourceCapabilities:
        ...
```

Nenhuma regra de negócio poderá depender diretamente de um provider.

---

# 12. RAW CONTENT

Todos os dados coletados serão normalizados.

```text
RawContent
├── id
├── source
├── external_id
├── url
├── author
├── published_at
├── text
├── media_type
├── media_reference
├── hashtags
├── audio_reference
├── metrics
├── metadata
└── collected_at
```

---

# 13. CONTENT INTELLIGENCE

Cada conteúdo passará por análise.

```text
RawContent
      ↓
Content Intelligence
      ↓
Structured Content
```

Extração:

```text
Topic
Niche
Hook
Format
Structure
Tone
Emotion
CTA
Visual Pattern
Audio
Keywords
Entities
Content Intent
```

---

# 14. MULTIMODAL AI

Quando houver disponibilidade de mídia, o sistema deverá ser capaz de analisar:

### Texto

* legenda;
* título;
* hashtags;
* OCR.

### Áudio

* transcrição;
* identificação de padrões;
* fala;
* potencial de reutilização.

### Vídeo

* cenas;
* estrutura;
* duração;
* cortes;
* elementos visuais;
* texto na tela.

### Imagem

* composição;
* estética;
* texto;
* objetos;
* estilo.

---

# 15. EMBEDDINGS

Conteúdos serão transformados em representações vetoriais.

Objetivo:

```text
Content A
       ↓
Embedding
       ↓
Similarity
       ↓
Content B
Content C
Content D
```

Isso permitirá detectar conteúdos semanticamente ou estruturalmente semelhantes.

---

# 16. TREND ENGINE

O Trend Engine será o coração do produto.

Entrada:

```text
milhares de conteúdos
```

Saída:

```text
clusters
+
patterns
+
candidate trends
```

---

# 17. CLUSTERING

Conteúdos semelhantes deverão ser agrupados.

Exemplo:

```text
Cluster #182

"3 coisas que ninguém te conta..."

├── Content A
├── Content B
├── Content C
├── Content D
├── Content E
└── Content F
```

A IA deverá identificar o padrão subjacente.

---

# 18. TREND LIFECYCLE

Cada trend terá um estado.

```text
UNKNOWN
    ↓
EMERGING
    ↓
GROWING
    ↓
MAINSTREAM
    ↓
SATURATED
    ↓
DECLINING
    ↓
EXPIRED
```

O sistema deverá priorizar principalmente:

```text
EMERGING
GROWING
```

---

# 19. TREND SCORE

Versão inicial:

```text
Trend Score =
    Growth Velocity      25%
  + Adoption             20%
  + Recency              15%
  + Cross-Niche Spread   10%
  + Engagement           10%
  + Similarity            10%
  + Adaptability          10%
```

Todos os componentes deverão ser normalizados.

O algoritmo deverá ser versionado:

```text
trend-score-v1
trend-score-v2
...
```

---

# 20. TREND CONFIDENCE

Além do Score:

```text
Trend Score
```

existirá:

```text
Confidence Score
```

Exemplo:

```text
Trend Score: 91
Confidence: 87%
```

Isso evita apresentar uma hipótese com a mesma confiança de uma tendência comprovada.

---

# 21. CROSS-NICHE DETECTION

Uma das funcionalidades mais importantes.

O sistema deverá identificar:

```text
Trend
 ↓
Niche A
 ↓
Niche B
 ↓
Niche C
```

Exemplo:

```text
Trend originalmente encontrada em:
Fitness

Posteriormente:
Moda
Lifestyle
Educação
```

O sistema deverá reconhecer:

> "Essa tendência está atravessando nichos."

Isso pode representar uma oportunidade antecipada.

---

# 22. EARLY SIGNAL ENGINE

O sistema deverá procurar **sinais precoces**, não apenas conteúdo já viral.

Sinais:

```text
repetição
crescimento
novos criadores
mudança de frequência
cross-niche adoption
format replication
audio adoption
hook replication
```

---

# 23. TREND VS NOISE

O sistema deverá eliminar:

```text
viral isolado
conteúdo duplicado
spam
bots
engagement artificial
picos anormais
conteúdo antigo
```

---

# 24. CLIENT DNA

Cada cliente terá um perfil de inteligência.

```text
Client DNA
├── Business
├── Niche
├── Audience
├── Positioning
├── Objectives
├── Tone
├── Topics
├── Preferred Formats
├── Forbidden Topics
├── Brand Rules
├── Competitors
└── Historical Performance
```

---

# 25. CLIENT MATCHING

Cada trend será comparada contra todos os clientes.

```text
Trend
 ↓
Client Matcher
 ↓
Client A → 92
Client B → 31
Client C → 87
Client D → 14
```

---

# 26. MATCH EXPLANATION

Nunca apresentar apenas:

> 92/100.

Deverá explicar:

```text
WHY

+ formato compatível
+ público semelhante
+ tema relacionado
+ timing favorável

RISKS

- tendência já saturada
- pouca adaptação possível
```

---

# 27. AI ADAPTATION ENGINE

A IA deverá transformar a trend em oportunidades.

Não copiar:

```text
❌ copiar legenda
❌ copiar roteiro
❌ copiar criativo
```

Mas abstrair:

```text
TREND MECHANISM
        ↓
CLIENT CONTEXT
        ↓
ORIGINAL CONCEPT
```

---

# 28. EXEMPLO

Trend:

> "3 coisas que ninguém te conta"

Cliente:

> Clínica odontológica.

IA:

```text
3 coisas que ninguém te conta antes
de colocar aparelho

3 erros que fazem seu clareamento
durar menos

3 coisas que todo paciente deveria
saber antes de um implante
```

---

# 29. AUTONOMOUS SCOUT

O sistema deverá executar pesquisas automaticamente.

Exemplo:

```text
06:00
 ↓
Scout Job
 ↓
Discover
 ↓
Collect
 ↓
Analyze
 ↓
Cluster
 ↓
Detect
 ↓
Score
 ↓
Match
 ↓
Rank
 ↓
Curate
```

---

# 30. AI CURATOR

O Curator recebe todas as possíveis trends e decide:

> **Isso merece a atenção humana?**

Critérios:

```text
Relevance
Novelty
Confidence
Actionability
Client Fit
Timing
```

---

# 31. ATTENTION BUDGET

Cada execução terá um limite.

Exemplo:

```text
Top 5
Top 10
Top 20
```

O sistema nunca deverá despejar centenas de resultados por padrão.

---

# 32. DAILY RADAR

Tela principal:

```text
━━━━━━━━━━━━━━━━━━━━━━
🔥 RADAR DE HOJE
━━━━━━━━━━━━━━━━━━━━━━

7 oportunidades encontradas

5 novas
2 em crescimento

━━━━━━━━━━━━━━━━━━━━━━
```

---

# 33. TREND CARD

Cada oportunidade deverá mostrar:

```text
Trend
Status
Score
Confidence
Growth
Sources
Examples
Why now?
Why relevant?
How to adapt?
Risk
```

---

# 34. "POR QUE ESTOU VENDO ISSO?"

Toda recomendação deverá ser explicável.

Exemplo:

> "Mostramos esta trend porque ela cresceu 240% em 48h, apareceu em 6 perfis independentes e ainda possui baixa adoção no nicho de estética."

---

# 35. FEEDBACK

A usuária poderá:

```text
🔥 Excelente
👍 Interessante
😐 Não sei
👎 Não serve
🚫 Nunca mostrar
```

---

# 36. LEARNING LOOP

Feedback:

```text
User Feedback
      ↓
Feedback Engine
      ↓
Preference Model
      ↓
Future Ranking
```

O sistema deverá aprender:

> "Essa Social Media gosta desse tipo de trend."

---

# 37. PERSONALIZAÇÃO

Com o tempo:

```text
Generic Trend Score
        ↓
Personalized Trend Score
```

Exemplo:

```text
Trend Score: 78

Para Rafael:
91

Para cliente X:
64
```

---

# 38. DASHBOARD

## Home

```text
Today's Radar
```

## Trends

```text
All Trends
Emerging
Growing
Mainstream
Declining
```

## Clients

```text
Client DNA
```

## Sources

```text
Instagram
Web
...
```

## Analytics

```text
Detection
Accuracy
Feedback
Performance
```

---

# 39. STACK

## Backend

```text
Python 3.12+
FastAPI
Pydantic
SQLAlchemy
Alembic
```

## Database

```text
PostgreSQL
```

## Vector Search

Inicialmente:

```text
pgvector
```

Evitar adicionar um vector database separado prematuramente.

---

## Queue

```text
Redis
```

com:

```text
Celery
```

ou alternativa equivalente definida na implementação.

---

# 40. AI

Arquitetura agnóstica de provider.

```text
LLM Provider
      ↓
AI Gateway
      ↓
Application
```

O código nunca deverá depender diretamente de um único fornecedor.

---

# 41. AI GATEWAY

Responsável por:

```text
model selection
fallback
retry
token tracking
cost tracking
prompt version
structured output
observability
```

---

# 42. EMBEDDING PROVIDER

Também deverá ser abstraído.

```python
class EmbeddingProvider:
    async def embed(text: str) -> list[float]:
        ...
```

---

# 43. FRONTEND

Sugestão:

```text
Next.js
TypeScript
React
Tailwind CSS
```

---

# 44. API

REST inicialmente.

```text
/api/v1/
```

Documentação:

```text
OpenAPI
Swagger
```

---

# 45. INFRA

Tudo containerizado.

```text
Docker
Docker Compose
```

Ambientes:

```text
development
staging
production
```

---

# 46. OBSERVABILIDADE

Obrigatório desde o início:

```text
OpenTelemetry
Structured Logging
Metrics
Tracing
Correlation ID
Job ID
Source ID
AI Request ID
```

---

# 47. SEGURANÇA

```text
Secrets Manager / environment secrets
OAuth quando aplicável
HTTPS
RBAC preparado
Rate limiting
Audit logs
```

Nunca armazenar senha de Instagram.

---

# 48. LGPD

Dados pessoais deverão ser minimizados.

O sistema deverá possuir:

```text
data retention
deletion
auditability
access control
```

---

# 49. ARQUITETURA

```text
                    ┌──────────────┐
                    │   FRONTEND   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │   API LAYER  │
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          ↓                ↓                ↓
     Client Engine    Trend Engine      AI Gateway
          │                │                │
          └────────────────┼────────────────┘
                           ↓
                   Intelligence Layer
                           │
                    ┌──────▼───────┐
                    │ DISCOVERY    │
                    │    LAYER     │
                    └──────┬───────┘
                           │
           ┌───────────────┼────────────────┐
           ↓               ↓                ↓
       Instagram          Web         Future Sources
```

---

# 50. PRINCÍPIO DE DESACOPLAMENTO

Nenhuma destas camadas deverá conhecer detalhes internos de outra:

```text
Connector
≠
Trend Engine

Trend Engine
≠
LLM Provider

Client Engine
≠
Instagram

Frontend
≠
Database
```

---

# 51. ROADMAP

## PHASE -1

### Autonomous Discovery Feasibility

Provar:

* descoberta automática;
* acesso às fontes;
* coleta;
* normalização;
* IA;
* clustering;
* trend detection;
* scoring;
* client matching.

---

## PHASE 0

### Foundation

* repository;
* Docker;
* CI;
* database;
* migrations;
* configuration;
* observability;
* testing.

---

## PHASE 1

### Identity & Clients

* users;
* clients;
* Client DNA;
* authentication.

---

## PHASE 2

### Discovery Infrastructure

* connector abstraction;
* source registry;
* discovery jobs;
* queue.

---

## PHASE 3

### Instagram Discovery

* Instagram connector;
* capabilities;
* collection;
* normalization;
* source health.

---

## PHASE 4

### Content Intelligence

* multimodal processing;
* embeddings;
* classification;
* metadata extraction.

---

## PHASE 5

### Trend Engine

* clustering;
* pattern detection;
* lifecycle;
* viral/trend differentiation.

---

## PHASE 6

### Trend Scoring

* Trend Score;
* Confidence;
* Growth;
* cross-niche;
* explainability.

---

## PHASE 7

### Dashboard

* Radar;
* Trend Cards;
* filters;
* search.

---

## PHASE 8

### Client Matching

* Client Score;
* recommendations;
* explanations.

---

## PHASE 9

### AI Adaptation

* concepts;
* hooks;
* scripts;
* creative directions.

---

## PHASE 10

### Feedback

* feedback;
* preferences;
* negative signals.

---

## PHASE 11

### Learning Engine

* personalization;
* ranking;
* historical performance.

---

## PHASE 12

### Autonomous Scout

* scheduled discovery;
* continuous monitoring;
* early signals.

---

## PHASE 13

### Notifications

```text
Email
Push
WhatsApp / future connector
```

---

## PHASE 14

### Additional Sources

```text
TikTok
Reddit
Google Trends
Web expansion
```

---

## PHASE 15

### Production Hardening

* security;
* scalability;
* cost optimization;
* reliability;
* disaster recovery.

---

# 52. FASE -1 — ACCEPTANCE CRITERIA

A Fase -1 só passa se:

### Discovery

* [ ] O sistema consegue executar discovery automaticamente.
* [ ] O sistema não depende de pesquisa manual da usuária.
* [ ] Existe pelo menos uma fonte funcional para validação.
* [ ] A arquitetura permite adicionar novas fontes.

### Intelligence

* [ ] Conteúdos são normalizados.
* [ ] Conteúdos são classificados.
* [ ] Embeddings funcionam.
* [ ] Clustering funciona.

### Trend

* [ ] Sistema identifica padrões.
* [ ] Sistema diferencia viral isolado de tendência.
* [ ] Sistema calcula Trend Score.
* [ ] Sistema calcula Confidence.
* [ ] Sistema identifica lifecycle.

### Personalization

* [ ] Client DNA funciona.
* [ ] Trends são ranqueadas por cliente.
* [ ] O sistema explica o motivo do ranking.

### AI

* [ ] Sistema consegue gerar adaptações.
* [ ] Não copia o conteúdo original.
* [ ] Saída é estruturada.

### Product

* [ ] Usuária consegue abrir o Radar.
* [ ] Radar apresenta oportunidades priorizadas.
* [ ] Cada oportunidade possui evidências.
* [ ] Usuária consegue fornecer feedback.

---

# 53. GO / NO-GO

## GO

Se:

```text
Discovery
+
Intelligence
+
Trend Detection
+
Personalization
```

funcionarem de maneira satisfatória.

## NO-GO

Se:

```text
não conseguimos descobrir conteúdo
```

sem exigir que a Social Media faça a pesquisa manualmente.

Nesse caso:

**não avançar para construir o produto inteiro.**

---

# 54. PRINCIPAIS RISCOS

## 🔴 Risco 1 — Acesso ao Instagram

Mitigação:

```text
Connector abstraction
+
provider independence
+
fallback sources
```

---

## 🔴 Risco 2 — Bloqueios / mudanças de plataforma

Mitigação:

```text
não depender de browser automation
não armazenar senha
provider abstraction
```

---

## 🔴 Risco 3 — Falsos positivos

Mitigação:

```text
confidence
multiple signals
cross-source validation
feedback loop
```

---

## 🔴 Risco 4 — IA "inventar" trends

Mitigação:

**nenhuma trend pode existir sem evidência.**

Toda trend deverá possuir:

```text
sources
signals
timestamp
metrics
confidence
```

---

## 🔴 Risco 5 — Excesso de recomendações

Mitigação:

```text
Attention Budget
AI Curator
ranking
```

---

## 🔴 Risco 6 — Custo de IA

Mitigação:

```text
cheap model → filtering
expensive model → final analysis
cache
batch processing
embeddings
```

---

# 55. MÉTRICAS DO PRODUTO

Não medir apenas:

```text
number of trends
```

Mediremos:

### Discovery Precision

Quantas recomendações realmente eram úteis?

### Discovery Recall

Quantas trends importantes conseguimos encontrar?

### False Positive Rate

Quantas recomendações eram ruído?

### Time Saved

Quanto tempo a Social Media deixou de gastar procurando?

### Adoption Rate

Quantas recomendações foram utilizadas?

### Feedback Score

Qualidade percebida.

---

# 56. NORTH STAR METRIC

A métrica principal será:

# **Useful Opportunities per Hour Saved**

Ou, de forma operacional:

> **Quantas oportunidades relevantes entregamos enquanto eliminamos horas de pesquisa manual.**

Porque esse é o problema que estamos resolvendo.

---

# 57. DEFINIÇÃO DE SUCESSO

O produto será considerado bem-sucedido quando a Social Media puder:

```text
abrir o sistema
      ↓
ver as oportunidades do dia
      ↓
entender por que elas importam
      ↓
escolher algumas
      ↓
adaptá-las para seus clientes
```

sem precisar passar horas procurando tendências.

---

# 58. O PRODUTO EM UMA FRASE

> **Uma IA que monitora continuamente o ecossistema de conteúdo, identifica tendências emergentes antes que fiquem saturadas e transforma essas tendências em oportunidades relevantes para cada cliente de uma Social Media.**

---

# 59. REGRA ABSOLUTA DO PROJETO

Esta frase passa a fazer parte do **Acceptance Contract**:

> **Se a solução exigir que a Social Media continue realizando manualmente a descoberta que pretendemos automatizar, a solução está incompleta.**

Isso evita que o projeto escorregue para simplesmente virar um "analisador de posts".

---

# 60. ESTADO DO BLUEPRINT V1.2

| Componente                | Status              |
| ------------------------- | ------------------- |
| Problema                  | ✅ FECHADO           |
| Proposta                  | ✅ FECHADA           |
| Discovery autônomo        | ✅ REQUISITO CENTRAL |
| Instagram como prioridade | ✅                   |
| Multi-source architecture | ✅                   |
| Trend Engine              | ✅                   |
| Client DNA                | ✅                   |
| AI Adaptation             | ✅                   |
| Feedback Loop             | ✅                   |
| Learning                  | ✅                   |
| Stack                     | ✅                   |
| Infraestrutura            | ✅                   |
| Segurança                 | ✅                   |
| LGPD                      | ✅                   |
| Observabilidade           | ✅                   |
| Roadmap                   | ✅                   |
| Acceptance Criteria       | ✅                   |
| GO/NO-GO                  | ✅                   |
| Métricas                  | ✅                   |
