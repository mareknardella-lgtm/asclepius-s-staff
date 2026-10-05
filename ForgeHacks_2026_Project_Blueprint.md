# ForgeHacks 2026 — Project Blueprint & Hackathon Workflow

> **Obiettivo:** usare questo documento come guida operativa per passare dal prompt ufficiale di ForgeHacks a un progetto AI funzionante, testabile e presentabile in 7 giorni.
>
> **Evento:** ForgeHacks 2026 — 3/10 ottobre 2026, online.
>
> **Nota importante:** i prompt specifici dei sei track vengono rilasciati all'inizio dell'hackathon. Quindi il progetto non va "deciso" in anticipo in modo rigido: bisogna preparare l'architettura e scegliere l'idea definitiva appena esce il prompt.

---

# 1. Obiettivo del progetto

Il progetto deve soddisfare contemporaneamente queste condizioni:

1. Risolvere un problema reale.
2. Essere chiaramente collegato a uno dei sei track:
   - AI + Healthcare
   - AI + Education
   - AI + Climate
   - AI + Business
   - AI + Cybersecurity
   - AI + Creativity
3. Usare realmente AI/ML, non solo una UI che chiama un LLM.
4. Avere un MVP funzionante.
5. Essere dimostrabile in pochi minuti.
6. Avere codice pubblico e README comprensibile.
7. Poter essere testato da un giudice senza dover configurare mezzo progetto.
8. Avere una storia semplice:

```text
PROBLEMA → INPUT → AI → DECISIONE/AZIONE → RISULTATO → IMPATTO
```

Il progetto deve essere pensato come un piccolo prodotto, non come una semplice demo tecnica.

---

# 2. Strategia generale

## Regola principale

Non partire da:

> "Quale AI possiamo usare?"

Partire da:

> "Quale problema concreto ci chiede di risolvere il prompt?"

Poi:

```text
Prompt ForgeHacks
      ↓
Problema concreto
      ↓
Utente target
      ↓
Workflow attuale / pain point
      ↓
Soluzione AI
      ↓
MVP minimo
      ↓
Architettura
      ↓
Implementazione
      ↓
Test
      ↓
Demo
      ↓
Submission
```

---

# 3. Prima del Day 1 — Preparazione

I prompt dei track sono bloccati prima dell'inizio. Questo significa che prima del kickoff conviene preparare **l'infrastruttura**, non una soluzione specifica.

## Preparare il repository

Struttura consigliata:

```text
forgehacks-project/
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── services/
│   │   ├── ai/
│   │   ├── models/
│   │   └── security/
│   ├── tests/
│   └── requirements.txt
│
├── docs/
│   ├── architecture.md
│   ├── decisions.md
│   └── demo-script.md
│
├── .env.example
├── .gitignore
├── README.md
└── LICENSE
```

## Stack consigliato

### Frontend

- React
- Vite
- TypeScript
- Tailwind CSS

### Backend

- Python
- FastAPI
- Pydantic
- HTTPX

### AI

Usare un provider che permetta di cambiare modello senza modificare tutta l'applicazione.

Interfaccia consigliata:

```text
Application
    ↓
AI Service Interface
    ↓
Provider Adapter
    ↓
LLM/API
```

In questo modo è possibile cambiare modello rapidamente.

### Database

Per un MVP:

- SQLite se basta un database locale
- PostgreSQL se serve deployment/cloud
- eventualmente un vector store solo se il problema richiede RAG

Non aggiungere database o infrastruttura solo perché "fa AI".

---

# 4. Architettura AI riutilizzabile

Una buona architettura di base:

```text
                    ┌──────────────┐
                    │    USER      │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   FRONTEND   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    API       │
                    └──────┬───────┘
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
        Validation     AI Service    Data Service
             │             │             │
             │       ┌─────┴─────┐       │
             │       ▼           ▼       │
             │    Retrieval     LLM      │
             │       │           │       │
             │       └─────┬─────┘       │
             │             ▼             │
             │       AI Decision         │
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                    ┌──────────────┐
                    │   RESULT     │
                    └──────────────┘
```

## Principio importante

L'LLM non deve necessariamente controllare tutto.

Meglio separare:

```text
Deterministic Logic
        +
AI Reasoning
        +
Validation
        +
Human/User Confirmation
```

Questo rende il progetto più affidabile e più facile da spiegare.

---

# 5. Come scegliere l'idea quando esce il prompt

Quando viene pubblicato il prompt, non iniziare immediatamente a programmare.

Prima compilare questa scheda:

```text
TRACK:
PROMPT:

PROBLEMA:
Chi ha questo problema?

UTENTE TARGET:
Chi utilizzerà il prodotto?

SITUAZIONE ATTUALE:
Come risolve oggi il problema?

PAIN POINT:
Perché il metodo attuale è lento, costoso, difficile o inefficiente?

INPUT:
Quali dati riceve il sistema?

AI:
Cosa deve fare realmente l'AI?

OUTPUT:
Quale risultato produce?

AZIONE:
Cosa può fare l'utente grazie al risultato?

IMPATTO:
Cosa migliora concretamente?

MVP:
Qual è la versione minima funzionante?

WOW MOMENT:
Qual è la parte che deve impressionare durante la demo?
```

---

# 6. Il filtro delle idee

Per ogni idea candidata, controllare:

### A. Relevance

```text
Risponde direttamente al prompt?
```

### B. AI necessity

```text
L'AI è realmente necessaria?
```

Se togliendo l'AI il prodotto funziona quasi allo stesso modo, l'idea è debole.

### C. Feasibility

```text
Possiamo costruire un MVP in 7 giorni?
```

### D. Demoability

```text
Possiamo mostrarne il valore in 30–60 secondi?
```

### E. Real-world value

```text
Qualcuno potrebbe realmente usarlo?
```

### F. Technical depth

```text
C'è abbastanza tecnologia da dimostrare competenza?
```

L'obiettivo non è creare il prodotto più grande.

L'obiettivo è creare il prodotto più convincente che possa essere **realmente completato**.

---

# 7. Pattern di progetto consigliato

Un pattern molto riutilizzabile per ForgeHacks è:

## AI Decision & Action System

```text
User Input
    ↓
Context Extraction
    ↓
AI Analysis
    ↓
Structured Output
    ↓
Validation
    ↓
Recommendation / Action
    ↓
User Confirmation
    ↓
Execution
    ↓
Feedback
```

Esempio astratto:

```json
{
  "problem": "...",
  "analysis": "...",
  "risk": "...",
  "recommendation": "...",
  "actions": [
    {
      "type": "...",
      "description": "...",
      "priority": "high"
    }
  ],
  "confidence": 0.87
}
```

Questo schema può essere adattato a diversi track.

---

# 8. AI layer

Creare un modulo isolato:

```text
backend/app/ai/
├── __init__.py
├── provider.py
├── prompts.py
├── schemas.py
└── service.py
```

## provider.py

Responsabilità:

- chiamare il modello
- gestire timeout
- gestire errori
- normalizzare la risposta

## prompts.py

Contiene:

- system prompt
- task prompt
- eventuali prompt specializzati

## schemas.py

Definisce l'output strutturato.

Esempio:

```python
class AIResult(BaseModel):
    summary: str
    reasoning: str
    recommendation: str
    confidence: float
    actions: list[str]
```

## service.py

Coordina:

```text
Input
 ↓
Prompt
 ↓
Model
 ↓
Parse
 ↓
Validate
 ↓
Return AIResult
```

---

# 9. Evitare la "AI wrapper trap"

Una semplice app:

```text
Input → LLM → Text
```

è generalmente troppo debole come progetto hackathon.

Aggiungere almeno un vero workflow:

```text
Input
 ↓
Structured extraction
 ↓
Context/data retrieval
 ↓
AI reasoning
 ↓
Validation
 ↓
Action/recommendation
 ↓
User feedback
```

La differenza deve essere visibile nella demo.

---

# 10. RAG — usarlo solo se serve

Se il progetto richiede conoscenza specifica:

```text
Documents
   ↓
Chunking
   ↓
Embeddings
   ↓
Vector Search
   ↓
Relevant Context
   ↓
LLM
   ↓
Answer
```

Non implementare RAG solo per poter dire "abbiamo usato RAG".

Usarlo quando il progetto deve ragionare su:

- documenti
- regolamenti
- knowledge base
- dati aziendali
- materiale didattico
- documentazione tecnica
- dataset specifici

---

# 11. Agent — usarlo solo quando c'è un workflow reale

Se il problema richiede più passaggi:

```text
Planner
   ↓
Tool selection
   ↓
Tool execution
   ↓
Observation
   ↓
Decision
   ↓
Next action
```

Esempio:

```text
User
 ↓
AI Agent
 ├── Search
 ├── Database
 ├── Calculator
 ├── External API
 └── File analysis
 ↓
Final result
```

Non creare un "multi-agent system" solo per renderlo più complesso.

Un singolo agent ben progettato è spesso sufficiente.

---

# 12. Security e reliability

Ogni progetto deve prevedere almeno:

## Secrets

Mai:

```text
API_KEY=...
```

nel repository.

Usare:

```text
.env
```

e fornire:

```text
.env.example
```

## Input validation

Validare:

- lunghezza
- tipo
- formato
- valori ammessi

## AI output validation

Non fidarsi ciecamente del testo prodotto dal modello.

Preferire:

```text
LLM
 ↓
Structured JSON
 ↓
Pydantic validation
 ↓
Business rules
 ↓
Application
```

## Error handling

Gestire:

```text
timeout
rate limit
invalid response
provider failure
missing data
```

---

# 13. Frontend

La UI deve mostrare immediatamente:

1. cosa fa il prodotto
2. dove inserire l'input
3. cosa sta facendo l'AI
4. quale risultato produce
5. quale azione può compiere l'utente

Evitate dashboard enormi.

Per il MVP:

```text
┌─────────────────────────────────────┐
│              PROJECT                │
│                                     │
│  Problema / input                   │
│  ┌───────────────────────────────┐  │
│  │                               │  │
│  └───────────────────────────────┘  │
│                                     │
│          [ Analyze ]                 │
│                                     │
├─────────────────────────────────────┤
│ AI RESULT                           │
│                                     │
│ Summary                             │
│ Recommendation                      │
│ Confidence                          │
│ Suggested actions                  │
│                                     │
│ [ Execute / Save / Export ]         │
└─────────────────────────────────────┘
```

---

# 14. Il vero MVP

Definire una sola user journey principale.

Esempio:

```text
1. User opens app
2. User enters data
3. AI analyzes it
4. AI produces structured result
5. User reviews result
6. User executes suggested action
7. App shows outcome
```

Se questa sequenza funziona dall'inizio alla fine, avete un MVP.

Tutto il resto è secondario.

---

# 15. Roadmap dei 7 giorni

## DAY 1 — Prompt → Product

Obiettivo:

```text
Prompt → idea → architecture → MVP specification
```

### Task

- leggere tutti i prompt
- scegliere il track
- definire il problema
- definire target user
- scrivere user journey
- decidere stack
- creare repository
- creare architecture diagram
- definire MVP

### Output

```text
README draft
Architecture
API contract
UI wireframe
MVP checklist
```

---

# DAY 2 — Foundation

Costruire:

```text
Frontend shell
Backend
Database
API
AI provider adapter
Environment configuration
```

Testare subito:

```text
Frontend → Backend → AI → Response
```

Non aspettare il giorno 5 per verificare che l'architettura funzioni.

---

# DAY 3 — AI Core

Implementare il cuore:

```text
Input
 ↓
Preprocessing
 ↓
AI
 ↓
Structured output
 ↓
Validation
```

Creare test per casi:

```text
normal input
empty input
invalid input
edge case
AI failure
```

---

# DAY 4 — Product Workflow

Collegare AI e prodotto:

```text
AI output
 ↓
Business logic
 ↓
User action
 ↓
Persist result
 ↓
Feedback
```

A questo punto deve esistere una demo end-to-end.

---

# DAY 5 — UX + Reliability

Migliorare:

- UI
- loading states
- error states
- empty states
- validation
- performance
- mobile/desktop layout
- logging
- deployment

Eliminare le feature non necessarie.

---

# DAY 6 — Demo + Documentation

Congelare le feature.

Non aggiungere grandi funzionalità.

Preparare:

```text
README
Architecture diagram
Screenshots
Demo environment
Demo script
Video
Devpost description
```

Fare una prova completa.

---

# DAY 7 — Submission Lock

Ultime verifiche:

```text
[ ] App funzionante
[ ] Repository pubblico
[ ] README completo
[ ] .env.example presente
[ ] Secrets rimossi
[ ] Demo video 2–4 min
[ ] Screenshots
[ ] Architecture diagram
[ ] Track corretto
[ ] Problem statement
[ ] Technical approach
[ ] Real-world impact
[ ] Deployment/demo link
[ ] Submission compilata
```

Poi:

**STOP FEATURE DEVELOPMENT.**

Da quel momento correggere solo bug critici.

---

# 16. Testing strategy

Non serve una suite gigantesca.

Servono tre livelli.

## Unit tests

Testare:

```text
validation
business logic
AI response parsing
utility functions
```

## API tests

Testare:

```text
POST /analyze
GET /result
POST /action
```

## End-to-end

Testare:

```text
User
 ↓
Frontend
 ↓
Backend
 ↓
AI
 ↓
Result
```

Il percorso principale deve funzionare senza interventi manuali.

---

# 17. Demo video — 2–4 minuti

La demo non deve essere un tour del codice.

Struttura:

## 0:00–0:20 — Problem

```text
"Today, [target user] struggles with [problem].
Current solutions are [problem]."
```

## 0:20–0:40 — Solution

```text
"We built [project], an AI-powered system that..."
```

## 0:40–2:30 — Live demo

Mostrare una singola user journey.

```text
Input
 ↓
AI processing
 ↓
Result
 ↓
Action
 ↓
Impact
```

## 2:30–3:15 — Technology

Mostrare brevemente:

```text
Frontend
Backend
AI model
RAG / tools / agent
Database
Deployment
```

## 3:15–3:45 — Impact

```text
Who uses it?
What changes?
Why does AI make the solution possible?
How could it scale?
```

## Ultimi secondi

Mostrare:

```text
GitHub
Live demo
Project name
```

---

# 18. README

Il README deve permettere a un giudice di capire il progetto in meno di 2 minuti.

Struttura:

```markdown
# Project Name

One sentence explaining the product.

## Problem

What real-world problem are we solving?

## Solution

What does the product do?

## Demo

[Live Demo]
[Demo Video]

## How It Works

Architecture diagram.

## AI

Explain exactly where and why AI is used.

## Tech Stack

- Frontend
- Backend
- AI
- Database
- Deployment

## Getting Started

Installation commands.

## Environment Variables

List required variables.

## Project Structure

Explain important folders.

## Impact

Who benefits and how?

## Future Work

What could be added after the hackathon?

## Team

Team members.
```

---

# 19. Architecture diagram da includere nella submission

Schema base:

```text
                    ┌─────────────┐
                    │    USER     │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  FRONTEND   │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  FASTAPI    │
                    └──────┬──────┘
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
        Data Layer     AI Service     Tools/APIs
                           │
                    ┌──────┴──────┐
                    ▼             ▼
                 LLM/API       Retrieval
                    │             │
                    └──────┬──────┘
                           ▼
                    Validation
                           │
                           ▼
                    AI Result
                           │
                           ▼
                    User Action
```

Adattare il diagramma al progetto reale.

---

# 20. Uso degli sponsor e delle API

ForgeHacks offre diversi perk e crediti.

Usarli quando hanno un ruolo reale nel prodotto.

Possibili categorie:

```text
LLM/API
Hosting
Workflow automation
Visual AI
App builders
Developer tools
Growth/analytics
```

Regola:

> Non aggiungere uno sponsor al progetto solo per poterlo nominare.

Se un servizio migliora davvero il workflow, integrarlo e documentarlo.

---

# 21. AI provider abstraction

Per poter cambiare modello rapidamente:

```python
class AIProvider:
    async def generate(self, prompt: str) -> str:
        raise NotImplementedError
```

Poi:

```text
AIProvider
├── FeatherlessProvider
├── OtherProvider
└── MockProvider
```

Il resto dell'applicazione non deve sapere quale provider viene utilizzato.

Questo permette di cambiare modello durante il development senza riscrivere il progetto.

---

# 22. Cost control

Durante l'hackathon:

- usare modelli piccoli per sviluppo/test
- usare modelli più potenti per i passaggi realmente importanti
- cache delle richieste ripetitive
- non inviare contesto inutile
- limitare output token
- evitare loop agentici infiniti
- usare mock AI nei test

Schema:

```text
Development
    ↓
Cheap/Fast model
    ↓
Testing
    ↓
Production demo model
```

---

# 23. Prompt engineering

I prompt devono essere versionati nel repository.

Esempio:

```text
backend/app/ai/prompts.py
```

Un buon prompt specifica:

```text
ROLE
TASK
CONTEXT
INPUT
CONSTRAINTS
OUTPUT FORMAT
SAFETY RULES
```

Per output strutturati:

```text
Return ONLY valid JSON matching the specified schema.
```

Ma il JSON deve comunque essere validato lato backend.

---

# 24. Human-in-the-loop

Per azioni importanti:

```text
AI recommendation
       ↓
User review
       ↓
Confirm
       ↓
Action
```

Questo è particolarmente utile quando il progetto tratta dati sensibili, decisioni importanti o azioni irreversibili.

L'AI dovrebbe assistere l'utente, non nascondere cosa sta facendo.

---

# 25. Metriche da mostrare

Se possibile, definire almeno 2–3 metriche.

Esempi:

```text
Time saved
Accuracy
Completion rate
Response latency
Cost per task
Number of manual steps
User satisfaction
Error rate
```

Esempio:

```text
Before:
12 manual steps
~8 minutes

After:
3 steps
~45 seconds
```

Non inventare numeri.

Se non avete dati reali, dichiarare che si tratta di una stima o di un test interno.

---

# 26. Come trasformare il progetto in una storia

La submission deve raccontare:

```text
BEFORE

User has a problem
        ↓
Manual / inefficient workflow
        ↓
Pain

AFTER

User opens our app
        ↓
AI understands the context
        ↓
AI generates useful result
        ↓
User takes action
        ↓
Problem is reduced
```

Questa storia deve essere coerente in:

- UI
- README
- video
- Devpost
- pitch

---

# 27. Anti-pattern da evitare

## ❌ Troppe feature

```text
Chat
Dashboard
Agents
RAG
Voice
Mobile
Analytics
Marketplace
Social network
```

Meglio:

```text
1 problema
1 workflow
1 AI core
1 risultato
```

## ❌ AI senza valore

```text
"Abbiamo aggiunto ChatGPT."
```

Non basta.

Bisogna spiegare:

```text
Why AI?
What does AI understand?
What decision does it enable?
What action does it automate?
```

## ❌ Demo preparata artificialmente

Se possibile, usare un workflow reale e ripetibile.

## ❌ UI prima del core

Prima:

```text
backend + AI + workflow
```

Poi:

```text
visual polish
```

## ❌ Overengineering

Non costruire infrastruttura enterprise per un MVP di 7 giorni.

---

# 28. Git workflow

Branch:

```text
main
develop
feature/*
fix/*
```

Commit chiari:

```text
feat: add AI analysis endpoint
feat: add result dashboard
fix: validate malformed AI output
docs: update architecture
```

Prima della submission:

```bash
git status
git diff
git log
```

Controllare che non siano presenti:

```text
.env
API keys
password
tokens
personal data
temporary files
```

---

# 29. Workflow consigliato con AI coding agents

Se si utilizzano coding agent/CLI:

## Fase 1 — Planning

Chiedere all'agent di:

```text
analyze repository
understand requirements
propose architecture
identify risks
create implementation plan
```

Non farlo iniziare subito a scrivere centinaia di file.

## Fase 2 — Foundation

```text
implement backend
implement frontend shell
implement AI adapter
add tests
```

## Fase 3 — Core

```text
implement primary user journey
```

## Fase 4 — Verification

```text
run tests
inspect failures
fix regressions
run full verification
```

## Fase 5 — Polish

```text
UX
loading
errors
documentation
deployment
```

L'agent deve lavorare per piccoli milestone verificabili.

---

# 30. Prompt master per il coding agent

Dopo aver ricevuto il prompt ufficiale, usare una richiesta simile:

```text
You are the lead engineer for a 7-day AI hackathon project.

Read the official ForgeHacks prompt below and treat it as the source of truth.

OFFICIAL PROMPT:
[PASTE PROMPT]

PROJECT GOAL:
Build a real-world AI solution that directly addresses the prompt.

Constraints:
- 7-day hackathon
- working MVP is more important than feature count
- AI must have a meaningful role
- architecture must be explainable
- project must be demoable in 2–4 minutes
- code must be public
- secrets must never be committed
- prioritize reliability and a complete end-to-end flow

Before coding:
1. Extract the exact requirements.
2. Define the target user.
3. Define the core problem.
4. Propose 3 possible solutions.
5. Compare them on feasibility, AI relevance, demoability and real-world usefulness.
6. Select one architecture without using subjective ranking language in the final project materials.
7. Define the smallest viable MVP.
8. Define the primary user journey.
9. Define the API contract.
10. Define the data model.
11. Define the AI workflow.
12. Define the test strategy.

Then implement the project incrementally.

For every milestone:
- make the smallest coherent change
- run relevant tests
- inspect failures
- fix regressions
- keep documentation updated
- do not add unrelated features

Never expose API keys or secrets.
Never invent external data.
Do not claim metrics that have not been measured.

At the end of each milestone report:
- completed work
- files changed
- tests run
- remaining blockers
- next milestone
```

---

# 31. Prompt per audit finale

Prima della submission:

```text
Perform a complete pre-submission audit of this ForgeHacks project.

Check:

1. Official prompt compliance
2. Track compliance
3. Real-world problem clarity
4. Meaningful AI usage
5. End-to-end functionality
6. Frontend/backend integration
7. AI error handling
8. Input validation
9. Output validation
10. Security and secrets
11. Test coverage of the critical path
12. README completeness
13. Deployment/demo reliability
14. Screenshots
15. Architecture diagram
16. Demo flow
17. Submission requirements

Do not add unnecessary features.

For every issue:
- severity
- exact location
- why it matters
- minimal fix

Then fix the critical issues and rerun the relevant verification.
```

---

# 32. Submission checklist

## Project

```text
[ ] Project name
[ ] Short description
[ ] Correct track
[ ] Clear real-world problem
[ ] Clear target user
[ ] Working MVP
[ ] Meaningful AI component
```

## Technical

```text
[ ] Frontend works
[ ] Backend works
[ ] AI provider works
[ ] Error handling works
[ ] Input validation
[ ] AI output validation
[ ] Secrets protected
[ ] Tests pass
```

## Repository

```text
[ ] Public GitHub repository
[ ] README
[ ] Setup instructions
[ ] .env.example
[ ] Architecture diagram
[ ] Project structure
[ ] No secrets
```

## Demo

```text
[ ] 2–4 minutes
[ ] Problem explained
[ ] Product shown
[ ] AI shown
[ ] Main workflow shown
[ ] Impact explained
[ ] Video publicly accessible
```

## Devpost

```text
[ ] Project title
[ ] Short description
[ ] Track
[ ] Problem statement
[ ] Target users
[ ] Technical approach
[ ] AI components
[ ] Real-world impact
[ ] Screenshots
[ ] Architecture
[ ] Deployment link
[ ] GitHub link
[ ] Demo video
```

---

# 33. Definition of Done

Il progetto è "done" quando un nuovo utente può:

```text
Open app
   ↓
Understand what it does
   ↓
Provide input
   ↓
Trigger AI
   ↓
Receive useful result
   ↓
Take the intended action
   ↓
Understand the benefit
```

senza che il team debba intervenire manualmente.

---

# 34. Piano finale sintetico

```text
DAY 0
Prepare repository + tools

DAY 1
Prompt → problem → product → architecture

DAY 2
Foundation + API + AI connection

DAY 3
AI core

DAY 4
End-to-end workflow

DAY 5
UX + reliability + deployment

DAY 6
README + architecture + video + submission

DAY 7
Testing + bug fixing + final submission
```

---

# 35. Principio finale

Il progetto non deve dimostrare quante tecnologie conosciamo.

Deve dimostrare:

```text
REAL PROBLEM
     +
GOOD PRODUCT
     +
MEANINGFUL AI
     +
WORKING MVP
     +
CLEAR IMPACT
```

La domanda da porsi durante tutto l'hackathon è:

> **"Se tolgo questa feature, il progetto perde valore per l'utente?"**

Se la risposta è no, probabilmente quella feature può aspettare.

---

# 36. Fonti ufficiali

- ForgeHacks: https://www.forgehacks.dev/
- Devpost: https://forgehacks-2026.devpost.com/
- Discord: https://discord.gg/HmS3CHYAv6

**Stato al 1 ottobre 2026:** ForgeHacks indica il periodo 3–10 ottobre 2026 e specifica che i prompt dei track vengono rivelati il Day 1. I sei track sono Healthcare, Education, Climate, Business, Cybersecurity e Creativity.
