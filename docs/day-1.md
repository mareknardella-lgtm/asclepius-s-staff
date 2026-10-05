# Asclepius — Day 1: Prompt → Product

**Decisione del 4 ottobre 2026: AI + Healthcare.** Prodotto scelto: un assistente di comprensione delle istruzioni di dimissione, con riferimenti al testo originale, verifica in parole proprie (*teach-back*) e scheda di azioni/domande da rivedere con il personale sanitario.

**Scheda di decisione Day 1, preservata come specifica.** Il testo dei sei prompt è stato confrontato con il sito ufficiale. In seguito sono stati implementati contratto Healthcare v1 e journey locale con mock, test e corpus sintetico. Le misure semantiche/AI live e di usabilità restano obiettivi, non risultati. Stato corrente in [status.md](status.md); [blueprint](../ForgeHacks_2026_Project_Blueprint.md) invariato.

## 1. Fonti e requisiti esatti

Consultazione delle fonti: **4 ottobre 2026**.

| Fonte | Riscontro / limite |
| --- | --- |
| Prompt incollati dall'utente + [sito ufficiale](https://www.forgehacks.dev/) | Testo dei sei prompt coincidente; sito indica 3–10 ottobre 2026 e rilascio dei prompt il 3 ottobre alle 12:00, senza timezone esplicita nella schedule. |
| [Regole Devpost](https://forgehacks-2026.devpost.com/rules) | Studenti, team di 1–4 persone, età minima 13 anni o consenso previsto dalla giurisdizione; minorenni con permesso del tutore. Elegibilità del team da confermare, non assunta. |
| Regole: lavoro pre-esistente | Il progetto deve essere sostanzialmente creato durante l'evento; per lavoro pre-esistente dichiarare chiaramente cosa è stato aggiunto. Conservare la distinzione foundation/prodotto e verificare con gli organizzatori eventuali dubbi; non assumere ammissibilità automaticamente. |
| Regole: AI e codice | Librerie open-source, dataset pubblici, modelli pre-addestrati e AI coding tools consentiti. Codice visibile pubblicamente o condiviso privatamente con organizzatori se richiesto. Il nostro blueprint punta a un repository pubblico. Nessuno stack/provider obbligatorio rilevato nel testo letto. |
| Regole: giudizio | Real-World Impact & Relevance; Technical Implementation & AI Use; Innovation & Creativity; Execution & Completeness; Presentation & Communication. Non sono pubblicati pesi numerici nella pagina letta. |
| Deadline: discordanza da risolvere | Banner Devpost: **10 ottobre 2026, 12:00 EDT** (=16:00 UTC, 18:00 Europe/Rome). Corpo delle regole: **12:00 EST** (=17:00 UTC, 19:00 Europe/Rome). Il sito conferma il giorno/ora ma non la timezone. Pianificare rispetto all'orario più anticipato del banner e chiedere conferma; non presentare la discordanza come risolta. |
| [AHRQ, Use the Teach-Back Method: Tool 5](https://www.ahrq.gov/health-literacy/improve/precautions/tool5.html) | Supporta il problema della comprensione e il metodo: far spiegare con parole proprie, chiarire e ricontrollare, senza mettere alla prova o colpevolizzare il paziente. **Non** dimostra l'efficacia o la validità clinica di Asclepius. |

### Sei prompt, trascrizione e requisiti

I requisiti sotto derivano dal testo, non da nuove condizioni inventate. Ogni track richiede una soluzione AI; le alternative nella frase del prompt non impongono di coprirle tutte.

| Track | Prompt esatto | Requisito operativo |
| --- | --- | --- |
| AI + Healthcare | Build an AI-powered solution that makes healthcare information and interactions clearer, more accessible, or easier to act on. | Rendere informazioni/interazioni sanitarie più chiare, accessibili **o** azionabili. |
| AI + Education | Build an AI-powered solution that helps learners move beyond memorization to understand concepts, make connections, and apply what they learn. | Mostrare comprensione, connessioni e applicazione, non soltanto flashcard o risposte. |
| AI + Climate | Build an AI-powered solution that helps people understand environmental changes, prepare for climate impacts, use resources wisely, or create resilient systems. | Un workflow ambientale con dati/scenario pertinenti e un esito osservabile; non sole raccomandazioni verdi generiche. |
| AI + Business | Build an AI-powered solution that turns business data into clear insights, predictions, or recommendations that help people make better decisions. | Dati aziendali → insight/previsioni/raccomandazioni → decisione riconoscibile. |
| AI + Cybersecurity | Build an AI-powered solution that helps people recognize, prevent, verify, or respond to scams, impersonation, and fraud enabled by AI or modern technologies. | Riconoscimento/prevenzione/verifica/risposta a frodi o impersonificazione; distinguere indizi da prove di autenticità. |
| AI + Creativity | Build an AI-powered experience that introduces a new way for people to create, collaborate, express ideas, or experience art and media. | Un'esperienza creativa distintiva e utilizzabile, non sola generazione di contenuti. |

Climate richiederebbe dati ambientali e una baseline credibile; Business dati e una decisione non generica; Creativity un'interazione creativa da validare. Non sono esclusi per scarso valore: concentriamo il confronto su tre percorsi realizzabili con lo stack disponibile senza ulteriori integrazioni obbligatorie.

## 2. Tre soluzioni confrontate sui sei criteri

Giudizi progettuali, non punteggi della giuria né probabilità di vittoria. Stime in giornate di lavoro focalizzate a partire dalla foundation esistente; non includono attese per credenziali, autorizzazioni o feedback esterno.

| Criterio | A — Healthcare: istruzioni → teach-back → scheda d'azione | B — Cybersecurity: messaggio sospetto → indizi → piano di verifica | C — Education: spiegazione dello studente → misconcezione → problema di trasferimento |
| --- | --- | --- | --- |
| Relevance | Copre “clearer” con linguaggio semplice ed “easier to act on” con passi e domande verificabili. | Copre “recognize” e “respond” con indizi citati e verifica fuori dal canale sospetto. | Copre comprensione e applicazione con confronto semantico e un nuovo problema, non memorizzazione. |
| AI necessity | Comprende formulazioni diverse e confronta la parafrasi dell'utente con il testo. Regole sole non gestiscono negazioni/parafrasi liberamente formulate. | Interpreta pressione, impersonificazione e contesto; regole su URL bastano per alcuni casi, non per tutti. | Individua una concezione errata espressa liberamente e adatta l'esercizio; un quiz fisso non lo fa. |
| Feasibility | 1 giorno schema/grounding, 1 teach-back, 1 UI/export, 1–2 test/misure/polish. Nessun OCR/EHR o corpus esterno. Rischio: errore clinico; MVP limitato a esempi sintetici e comprensione, non decisioni mediche. | 1 giorno parsing/indizi, 1 piano di verifica, 1 UI, 1–2 test/polish. Non possiamo dimostrare identità o autenticità con il solo testo incollato; integrazioni email fuori scope. | 1 giorno fonti/esercizi di un solo argomento, 1 valutazione, 1 UI, 1–2 benchmark/polish. Serve una rubrica corretta per errori concettuali. |
| Demoability | In 30–60 s: fonte complessa → passi citati → risposta che inverte una condizione → spiegazione ancorata alla fonte → scheda rivista. | In 30–60 s: messaggio sintetico → indizi → procedura di verifica; senza contatto esterno il risultato resta un piano, non verifica conclusa. | In 30–60 s: ragionamento errato → misconcezione → esercizio nuovo; il tempo dello studente può allungare la demo. |
| Real-world value | Pazienti/caregiver che devono capire istruzioni; AHRQ documenta il metodo. Bisogno specifico e usabilità di Asclepius ancora da validare con utenti; nessun esito clinico misurato. | Destinatari di richieste urgenti di denaro/accesso; scenario plausibile, nessuna intervista o riduzione frodi misurata. | Studenti con difficoltà a trasferire concetti; scenario plausibile, nessun miglioramento di apprendimento misurato. |
| Technical depth | Output strutturato, validazione citazioni, astensione, confronto semantico, revisione ed export con provenienza; test su contraddizioni e omissioni. | Separazione indizi/verifica, URL non visitati automaticamente, input ostile e output strutturato; test avversariali. | Rubrica ancorata a fonti, valutazione del ragionamento ed esercizi controllati; benchmark correttezza/pedagogia. |

### Decisione

**Scegliamo A, AI + Healthcare.** Combina due parti esplicite del prompt in una sola journey osservabile; consente un'azione locale reale senza integrazioni ospedaliere; offre un confronto AI testabile su parafrasi, omissioni e negazioni. La foundation già include validazione, adapter ed export, quindi il lavoro nuovo si concentra sul valore del prodotto.

Il nome Asclepius è coerente, ma non è il criterio di scelta. Il trade-off accettato è il rischio di interpretazioni sanitarie errate: restringiamo il prototipo a informazioni fornite, esempi sintetici, nessuna diagnosi/prescrizione, astensione e revisione. Non promettiamo originalità globale, efficacia clinica o vittoria.

## 3. Intake eseguibile

Una riga per chiave; i dettagli verificabili sono nelle sezioni successive.

```text intake
TRACK: AI + Healthcare — Asclepius, comprensione delle istruzioni di dimissione con teach-back e scheda d'azione.
PROMPT_SOURCE: Testo fornito dall'utente, confrontato il 4 ottobre 2026 con https://www.forgehacks.dev/; regole lette su https://forgehacks-2026.devpost.com/rules; discordanza EDT/EST non risolta.
PROMPT_SUMMARY: “Build an AI-powered solution that makes healthcare information and interactions clearer, more accessible, or easier to act on.” Asclepius rende comprensibili istruzioni esistenti e aiuta a rivedere passi e domande senza prendere decisioni mediche.
PROBLEM: Dopo una dimissione un paziente o caregiver deve trasformare formulazioni sanitarie complesse in passi corretti; una lettura o un riassunto non mostrano se una condizione o una scadenza è stata fraintesa. Scenario supportato dal metodo AHRQ, non da interviste già svolte.
TARGET_USER: Paziente adulto o caregiver che legge istruzioni già emesse dal team sanitario; nel prototipo soltanto partecipanti che usano esempi sintetici, senza dati personali.
CURRENT_WORKFLOW: Leggere il documento, annotare passi e scadenze, chiedere chiarimenti al team sanitario; la comprensione non è verificata dal solo fatto di aver letto. Descrizione del caso d'uso, non workflow osservato sul campo.
PAIN_POINT: Jargon, condizioni e scadenze possono essere fraintesi; un output fluente può nascondere un'omissione. Rendere visibili fonte, ambiguità e ciò che l'utente ha capito.
INPUT_DATA: Testo sintetico in inglese, 20–4000 caratteri dopo normalizzazione, più parafrasi volontaria 1–1000; nessuna cartella clinica, OCR o file reale. Esempi scritti dal progetto, chiaramente etichettati.
AI_ROLE: Estrarre passi espliciti e renderli semplici preservando condizioni e scadenze; citare la fonte; segnalare ambiguità; confrontare semanticamente il teach-back con le istruzioni selezionate e spiegare eventuali differenze.
WHY_AI: Le regole possono verificare che una citazione esista, ma non interpretare tutte le parafrasi libere, negazioni e condizioni implicite nel linguaggio. Il modello affronta questo confronto; il codice controlla forma/provenienza e impedisce azioni automatiche, senza certificare verità clinica.
OUTPUT: CarePlan v1 con fonte segmentata, sintesi, fino a sei passi citati, ambiguità e domande; TeachBackResult con feedback ancorato alla fonte e stato matched, needs_clarification oppure unable_to_assess; scheda JSON locale dopo revisione.
DECISION_OR_ACTION: Rivedere passi e punti da chiarire, marcare localmente letti/da chiedere, confermare revisione ed esportare una scheda da discutere con il team sanitario. Download e stato locale sono l'esito, non appuntamento prenotato o cura eseguita.
IMPACT_MEASURED: Non misurato. Misurare fedeltà/completamento su 20 documenti sintetici con baseline riassunto singolo, classificazione su 30 teach-back con rubriche e tempo del workflow con volontari consenzienti; protocollo e denominatori in sezione 8.
MVP_SCOPE: Sette criteri verificabili in sezione 5: input sintetico, piano strutturato, citazioni, astensione, un confronto teach-back, revisione/export, gestione errori con mock dichiarato. Una lingua e una journey; niente diagnosi, dosaggi generati, EHR o persistenza server.
WOW_MOMENT: Una risposta apparentemente plausibile “prenoto solo se sto ancora male” contraddice “entro sette giorni anche se stai meglio”: Asclepius evidenzia il passaggio originale e propone un chiarimento non colpevolizzante prima dell'export.
REQUISITES_TRACE: clearer → piano semplice + citazioni → T02/T03; easier to act on → passi/domande/revisione/export → T06; AI-powered interactions → confronto parafrasi-fonte → T05 e prova live; nessuna promessa di coprire tutte le alternative del prompt.
DATA_PERMISSION: Solo esempi sintetici privi di identificatori e contenuti scritti dal progetto. Conferma prima dell'invio al provider; non abilita dati sanitari reali. Credenziali/policy/provider live ancora da configurare; nessuna certificazione GDPR/HIPAA dichiarata.
ALTERNATIVES: A Healthcare: aderenza a chiarezza/azione, AI per semantica, 4–5 giorni stimati, demo con fraintendimento, bisogno supportato da AHRQ, profondità grounding/astensione/teach-back. B Cybersecurity: riconoscimento/risposta, AI per indizi contestuali, 4–5 giorni, demo di messaggio sospetto, bisogno plausibile non validato, profondità input ostile ma autenticità non provabile dal testo. C Education: comprensione/applicazione, AI per misconcezioni, 4–5 giorni, demo di trasferimento, bisogno plausibile non validato, profondità rubrica/esercizi con corpus di un solo argomento. Confronto completo sui sei criteri in sezione 2.
SELECTION_RATIONALE: Healthcare consente una journey riconoscibile con due requisiti espliciti del prompt, output verificabile rispetto alla fonte e azione locale senza integrazioni esterne. Riusa la foundation e concentra la profondità sul confronto semantico; rischio sanitario contenuto restringendo dati e funzione, non eliminato da un disclaimer.
API_CONTRACT: Healthcare v1 ora implementato e verificato con mock: GET /health invariato; POST /analyze con text e synthetic_data_confirmed=true produce CarePlan; POST /teach-back con text, focus citato e answer produce TeachBackResult. Errori 422/429/502/504. Schema, limiti ed export asclepius-<request_id>.json in architecture.md.
DATA_MODEL: SourceSegment id/text generato dal backend; Evidence segment_id/quote validata; CareItem id/instruction/evidence; CarePlan summary/items/clarifications/questions; TeachBackResult status/feedback/evidence; stato revisione/checkbox solo browser; nessuna sessione o tabella server.
TEST_STRATEGY: Unit su schema, citazioni, segmenti e parsing; API input/output e guasti provider; UI invalidazione, teach-back e blocco export; browser percorso reale con mock dichiarato e poi provider live; benchmark separato con rubriche sintetiche prima di claim sull'AI.
RISKS: Allucinazione o falsa rassicurazione: owner ruolo backend/AI, nessuna identità inventata; astensione, citazioni e review obbligatorie, test semantici; piano B restringere a istruzioni amministrative. Credenziali mancanti: fixture visibile, non AI simulata come live. Deadline/elegibilità e riuso da confermare con organizzatori.
```

Il preflight controlla struttura/completezza ed esegue una scansione euristica: **non** verifica i contenuti, la sicurezza clinica o l'assenza di segreti. Non usarlo come autorizzazione a pubblicare; la scansione non sostituisce l'audit dei file effettivamente condivisi.

## 4. Unica user journey e wireframe

1. L'utente apre Asclepius, vede lo scopo e il limite del prototipo; carica un esempio sintetico o incolla un testo senza dati reali e conferma l'invio al provider configurato.
2. Richiede un piano. Il backend segmenta la fonte, chiama il modello e valida JSON/citazioni prima della risposta.
3. Legge testo originale e passi semplici affiancati. Ogni passo mostra il riferimento; ambiguità e informazioni mancanti restano visibili, non completate automaticamente.
4. Seleziona un passo e descrive con parole proprie cosa farà. Un invio esplicito confronta la risposta con la **fonte**, non con la sola sintesi generata.
5. Legge un feedback non colpevolizzante; se necessario rivede l'istruzione e annota una domanda per il personale sanitario. “Matched” indica corrispondenza testuale stimata, non comprensione certificata o assenza di rischio.
6. Rivede il piano e conferma la revisione, quindi esporta la scheda JSON. UI mostra download richiesto e cosa resta da chiarire. Il file include fonte, provenienza, stato mock/live e feedback; nessuna azione sanitaria viene eseguita.
7. Cambiare la fonte invalida piano, teach-back e revisione; cambiare la risposta invalida il precedente feedback. Chiudere la pagina elimina lo stato locale, non un file già scaricato.

Wireframe della specifica, ora realizzato dalla UI inglese:

```text
ASCLEPIUS | Help understanding written instructions | MOCK / LIVE
[synthetic-data notice + limits + consent]
[Original instructions]       [Plain-language steps + source references]
[Create plan / loading]       [Unclear / not specified / ask care team]
                             [Explain this step in your own words]
                             [Compare with source → feedback + quote]
                             [Review checkbox → export reviewed plan]
```

UI e output MVP in **inglese**, una sola lingua, per demo alla giuria. La foundation era in italiano; conversione al prodotto completata senza i18n, traduzione clinica o seconda interfaccia.

## 5. Smallest viable MVP: sette criteri di accettazione

T01–T07 sono acceptance criteria: copertura strutturale/API/UI implementata; le verifiche semantiche su AI reale e i guasti live non si considerano passati tramite fixture. Esiti specifici in [status.md](status.md).

| # | Requisito verificabile | Test previsto |
| --- | --- | --- |
| 1 | Testo sintetico 20–4000 caratteri, conferma obbligatoria, fonte modificabile; input invalido non chiama il modello. | T01: limiti/blank/extra/consenso, normalizzazione e contatore chiamate. |
| 2 | Piano strutturato, massimo sei passi e tre domande, istruzioni fedeli senza nuovi consigli clinici. | T02: schema unit/API + rubrica semantica su corpus; uno schema valido da solo non prova fedeltà. |
| 3 | Ogni passo ha almeno una citazione esatta di un segmento della fonte; citazione inesistente/ID ignoto fa fallire la risposta. | T03: testo inventato, segmento sbagliato, Unicode e output senza evidence → errore esplicito. |
| 4 | Ambiguità/informazione assente → chiarimento o astensione, non scelta di scadenza/terapia. Nessun passo operativo di dosaggio generato dal MVP. | T04: fonti contraddittorie, scadenza assente, testo solo farmacologico, fuori dominio e prompt injection; benchmark semantico e stati UI. |
| 5 | Un passo selezionato → risposta libera → feedback fondato sul testo; il confronto non riceve la sintesi client come verità. | T05: parafrasi corretta, condizione invertita, omissione, risposta irrilevante/incerta; focus falsificato rifiutato. |
| 6 | Review obbligatoria prima dell'export JSON; cambiamenti invalidano review/risultati; il file mantiene fonte, provenance e mock flag. | T06: UI e browser con ispezione del file esportato e nome asclepius-<request_id>.json. |
| 7 | Loading, empty, timeout, errori e mock/live espliciti; niente fallback invisibile e niente invio automatico delle risposte. | T07: API/provider/UI + browser su desktop/mobile, console/rete, failure path. |

### Fuori scope

- Diagnosi, triage, valutazione di emergenze, prescrizioni, suggerimenti di dosi o modifiche a farmaci. Se il documento include farmaci, mostrare l'originale senza crearne un piano operativo; indirizzare le domande al personale sanitario.
- Registrazione di utenti, dati reali identificabili, EHR, upload PDF/OCR, dettatura, chatbot libero, traduzione, notifiche, prenotazioni o invio automatico.
- Database, RAG/vector store, agenti, browsing, tool execution, dashboard e seconda lingua.
- Percentuali di confidence come certificazione clinica. Il contratto di prodotto usa stati descrittivi e incertezza esplicita.

## 6. Workflow AI e controlli

**Fonte sintetica → normalizzazione/segmenti → AI di estrazione/spiegazione → parsing rigido → citazioni validate → piano → AI di confronto con fonte → validazione → revisione → export locale.**

Una chiamata per creare il piano e una per ogni teach-back richiesto esplicitamente; nessun loop, retry automatico o agente. Mantenere limiti di timeout/input/output della foundation; misurare se il budget token basta per il nuovo schema prima di modificarlo. Errori di schema/provenienza non producono un piano parziale presentato come validato.

Il modello deve preservare condizioni, scadenze e negazioni, segnalare assenze/contraddizioni e astenersi se non può confrontare. Dati inseriti e parafrasi sono contenuti non attendibili, non nuove istruzioni di sistema. Citazioni esistenti provano la provenienza, **non** implicazione logica, completezza, autenticità del documento o verità medica: serve un benchmark semantico separato e resta necessaria la revisione.

Il [contratto v1 e modello dati](architecture.md) specifica i campi, i limiti e la separazione dalla v0 ancora in esecuzione.

## 7. Rischi, owner e piano B

Owner indicati per **ruolo**, da assegnare alle persone reali del team.

| Rischio | Owner | Mitigazione / piano B |
| --- | --- | --- |
| Interpretazione clinica errata o falsa rassicurazione | Backend/AI | Citazioni, astensione, niente dosaggi/triage, T02/T04/T05 e review. Se emergono errori sistematici restringere la demo a follow-up, documenti e contatti amministrativi; non chiamare il sistema clinicamente validato. |
| Invio di dati sensibili | Product/privacy | Solo sintetici nella demo, conferma visibile, no log intenzionali/persistenza. Un checkbox non anonimizza: dati reali restano vietati nel prototipo; deployment richiede policy e controlli ulteriori. |
| Provider assente/instabile | Backend | Fixture deterministica dichiarata, errori sanitizzati. Nessun risultato mock descritto come AI live; la prova reale resta un gate necessario. |
| Fedeltà semantica non verificabile dal validatore | QA/AI | Rubriche manuali e casi avversariali. Senza revisore sanitario, benchmark di corrispondenza su sintetici, non audit clinico. |
| Tempo e scope | Product | Una lingua, una journey, sette criteri; ridurre feature opzionali, mai nascondere test falliti o cambiare i risultati per il video. |
| Elegibilità, lavoro pre-evento e timezone | Titolare/team | Conferma con organizzatori, registrazione e attribuzione trasparente delle parti pre-esistenti. Nessuna iscrizione/pubblicazione automatica. |

## 8. Protocollo di misura (nessun risultato ancora)

Versionare dataset e rubriche prima del benchmark. Tutti i documenti sono **sintetici**, etichettati come tali, senza identificatori. Il [corpus sintetico](../backend/tests/care_cases.json) è stato creato dopo questa scelta: 20 rubriche e 30 risposte etichettate, validate strutturalmente. Non è ancora stato misurato con un provider reale. Il runner iniziale fa una sola esecuzione; baseline, tre ripetizioni e studio volontari restano da completare.

| Misura | Dataset e metodo | Baseline / reporting |
| --- | --- | --- |
| Fedeltà e copertura dei passi | 20 documenti: 8 semplici, 4 jargon/condizioni, 4 assenze/contraddizioni, 4 fuori scope/input ostile. Annotare proposizioni richieste/vietate, poi contare omissioni, aggiunte non supportate e citazioni invalide. | Stesso provider/modello/parametri con riassunto singolo senza teach-back contro workflow Asclepius. Tre esecuzioni per documento; mostrare denominatori e variabilità, non confondere percentuale citazioni valide con correttezza clinica. Stato: non misurato. |
| Corrispondenza del teach-back | 30 risposte pre-annotate: 10 parafrasi corrispondenti, 10 errori/omissioni, 10 irrilevanti/ambigue. Rubrica matched / needs_clarification / unable_to_assess, fissata prima dell'esecuzione. | Matrice di confusione e soprattutto falsi matched; confronto con matching parole chiave. Valutazione linguistica interna, non prova di comprensione del paziente. Stato: non misurato. |
| Tempo/usabilità | Proporre a 5 volontari consenzienti compiti sintetici bilanciati: trovare passo/scadenza con documento solo e con Asclepius. Ordine controbilanciato; registrare successo e tempo, non salute personale. | Mediane e conteggi, campione e limiti dichiarati. Se volontari assenti, riportare soltanto tempi tecnici e non un miglioramento di usabilità. Stato: non misurato. |
| Latenza tecnica | Registrare solo request id, versione prompt, modello, esito e durata (senza testi) sul corpus consentito; includere cold start/errori e almeno 20 richieste live prima di p50/p95. | Separare piano/teach-back e mock/live; timing mock non è inference. Non promettere risposta in 30–60 s: quello è l'obiettivo di durata della demo, da verificare. Stato: non misurato. |

## 9. Gate e prossime milestone

Day 1 consegna: confronto, scelta, unica journey, wireframe, sette acceptance criteria, diagramma/contratto progettati, misure e piano B. La completezza dell'intake deve essere verificata via CLI e contenuti revisionati; le questioni di elegibilità/timezone restano esplicite, non risolte dal gate.

| Milestone | Consegna / gate |
| --- | --- |
| Day 0, già presente | Foundation neutrale con mock, adapter e test. |
| Day 1, scelta | Specifica Healthcare e documentazione completate. |
| Day 2 | Contratto CarePlan, segmenti/citazioni, fixture e UI implementati, test/browser mock verificati. Provider reale e prova su sintetico bloccati su credenziali. |
| Day 3 | Prompt di dominio, astensione, teach-back e corpus/rubriche implementati; prove e benchmark live non eseguiti. |
| Day 4 | Journey mock completa, review/export con file ispezionato; correttezza semantica e timing live ancora da misurare. |
| Day 5 | Errori/mobile/accessibilità, benchmark e limiti; pubblicazione solo dopo autorizzazione e hardening. |
| Day 6 | Freeze feature, README effettivo, screenshot e video 2–4 minuti; attribuzione delle parti pre-esistenti. |
| Day 7 | Bug critici, audit e submission autorizzata entro deadline confermata. |

Le etichette Day sono milestone del blueprint, non una promessa di sette nuovi giorni disponibili: l'evento è già iniziato. [Stato e blocchi](status.md) · [Demo progettata](demo-script.md) · [Audit submission](submission-checklist.md).
