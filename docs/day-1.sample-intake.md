# Esempio di intake (NON usare per la submission)

Documento di riferimento che mostra la forma attesa da `scripts/day1_preflight.py`.
I valori qui sotto sono segnaposto: dimostrano che il gate diventa verde solo quando
ogni campo è compilato con lunghezza e profondità sufficienti. **Non sono il Day 1 di Asclepius.**

```text intake
TRACK: Track Healthcare (da confermare sul prompt rilasciato: questo e' un segnaposto di prova, non una scelta).
PROMPT_SOURCE: https://esempio.invalid/prompt-ufficiale (segnaposto, URL fittizio: va sostituito con la fonte reale verificata)
PROMPT_SUMMARY: Segnaposto di prova. Il prompt di esempio chiede di ridurre il tempo di triage dei documenti clinici mantenendo il giudizio umano in ogni decisione.
PROBLEM: Segnaposto: il triage documentale manuale richiede piu' passaggi e piu' tempo del necessario per lo stesso risultato.
TARGET_USER: Segnaposto: coordinatore di reparto che riceve la documentazione iniziale del paziente.
CURRENT_WORKFLOW: Segnaposto: lettura sequenziale, estrazione manuale dei dati, compilazione del modulo, doppio controllo.
PAIN_POINT: Segnaposto: lavoro ripetitivo, errori di trascrizione, ritardo nella presa in carico.
INPUT_DATA: Segnaposto: documenti caricati dall'utente su base di consenso informato, senza dati di terzi non necessari.
AI_ROLE: Segnaposto: estrarre entita strutturate e segnalare incoerenze interne, senza formulare diagnosi.
WHY_AI: Segnaposto: il lavoro richiede di interpretare linguaggio clinico variabile e di collegare affermazioni a documenti diversi; regole fisse falliscono sulla varieta' dei casi.
OUTPUT: Segnaposto: JSON strutturato con sintesi, campi estratti, incongruenze e passi richiesti alla revisione umana.
DECISION_OR_ACTION: Segnaposto: l'operatore revisiona il risultato e decide se procedere, senza esecuzione automatica.
IMPACT_MEASURED: non misurato. Da misurare su dataset di prova autorizzato: tempo di triage per documento, errori di trascrizione, percentuale di output accettati senza correzioni.
MVP_SCOPE: Segnaposto: un percorso solo: caricamento documento, analisi, revisione, export del risultato.
WOW_MOMENT: Segnaposto: le incongruenze tra documenti vengono evidenziate con il rimando al punto esatto del testo.
REQUISITES_TRACE: Requisito 1 strutturato -> POST /analyze -> test API sul provider finto; Requisito 2 revisione umana -> export disabilitato senza conferma -> test UI; Requisito 3 validazione output -> schema Pydantic rigido -> test unitari.
DATA_PERMISSION: Segnaposto: consapevolezza del consenso, minimizzazione, dati sintetici in sviluppo, nessun dato reale nei repository.
ALTERNATIVES: A: estrazione strutturata con contesto limitato; B: pipeline retrieval su knowledge base e poi sintesi; C: agente multi-step con strumenti. Valutate sulle sei dimensioni del blueprint, con una riga di prova per criterio.
SELECTION_RATIONALE: A soddisfa i requisiti con un solo passaggio inference ed e' dimostrabile in trenta secondi; B aggiunge costo e dipendenza da un corpus che al Day 1 non e' disponibile; C introduce loop e costo non controllabile entro i giorni rimanenti.
API_CONTRACT: Segnaposto: POST /analyze input e output gia' definiti in docs/architecture.md; da estendere solo con quanto richiesto dal prompt reale.
DATA_MODEL: Segnaposto: nessuna persistenza nel MVP; da definire se il prompt richiede di conservare lo storico.
TEST_STRATEGY: Segnaposto: unita' su validazione e parsing, API con provider finto, UI sul percorso completo, piu' il caso di output malformato dal modello.
RISKS: Segnaposto: uso clinico vietato ai sensi del regolamento del track, dati non autorizzati, output non verificabile; owner e piano B da assegnare al Day 1 reale.
```