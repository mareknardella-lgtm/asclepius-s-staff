# Decisioni tecniche

## D001 — Non fissare il prodotto prima del prompt

Il blueprint richiede problema → utente → soluzione, non tecnologia → problema. Il Day 0 prepara soltanto un percorso di verifica neutrale. Al Day 1 confrontare tre soluzioni su aderenza, necessità AI, fattibilità, demo e utilità, senza etichette soggettive nei materiali finali.

## D002 — Stack del blueprint

React, Vite, TypeScript e Tailwind CSS; Python, FastAPI, Pydantic e HTTPX. npm per il nuovo frontend (nessun package manager preesistente); venv locale per Python. Pytest, mypy, Vitest e Testing Library per test e controllo statico. Nessuna dipendenza già presente nel workspace.

## D003 — Adapter AI sostituibile

Interfaccia async `generate(system_prompt, user_prompt) -> str`. Mock deterministico esplicitamente identificato oppure endpoint chat-completions compatibile OpenAI. Cambiare provider/modello via configurazione backend; JSON sempre validato fuori dall'adapter. Nessuna dipendenza SDK specifica. Un provider non compatibile richiederà un nuovo adapter, non cambiamenti al workflow.

## D004 — Nessuna persistenza iniziale

Il Day 0 non richiede salvataggio server, retrieval, agenti o azioni esterne. Nessun SQLite/vector store ornamentale. Decidere il modello dati del prodotto al Day 1; per ora contratti input/output e request id bastano.

## D005 — Conferma umana e trasparenza

Output strutturato, revisione obbligatoria prima dell'export, mock sempre visibile. L'esportazione non significa che una raccomandazione è stata eseguita. Confidence non calibrata; nessuna accuratezza dichiarata.

## D006 — Costi e privacy

Limiti per testo, contesto, token e timeout. Nessun retry automatico, cache o logging di contenuti sensibili. Se un track richiede dati sanitari/personali, stabilire consenso, minimizzazione e policy prima delle chiamate reali.

## D008 — Nome del progetto: Asclepius

Il progetto si chiama **Asclepius**. Il rinominaggio ha toccato titolo API, logger, package npm, lockfile, `index.html`, brand della UI, footer, prefisso dei file esportati, README e documentazione; verificato con test, typecheck e build.

Il nome dell'evento **ForgeHacks 2026** resta invariato dove indica il fatto reale: nome dell'hackathon, URL ufficiali, nome e contenuto del blueprint ricevuto. Non rinominare l'evento: un giudice deve poter collegare il progetto all'iniziativa.

Il nome è un impegno di branding, non la motivazione della scelta. Il 4 ottobre 2026, ricevuti i sei prompt, è stato scelto Healthcare tramite confronto documentato; vedi D010 e [Day 1](day-1.md).

## D009 — Il Day 1 è un gate eseguibile, non un documento

Il blueprint chiede di definire il prodotto prima di programmarlo. [day1_preflight.py](../scripts/day1_preflight.py) controlla che l'intake in [day-1.md](day-1.md) abbia tutti i campi richiesti e svolge una scansione euristica di possibili segreti. Nessuna dipendenza, nessuna rete. Non certifica assenza di segreti e non sostituisce un audit dei file pubblicati.

Il gate verifica completezza e forma, **non** la correttezza delle risposte: un intake pieno di affermazioni plausibili ma false passa lo stesso. La revisione resta umana. Ironicamente, il primo bug trovato è stato nel gate stesso (il rilevamento dei segreti mancava di `AI_API_KEY`), quindi il gate va trattato come codice da testare, non come garanzia.

## D010 — Healthcare: fonte → comprensione → azione rivista

Decisione del 4 ottobre 2026, delegata dall'utente. Prompt confermati sul sito ufficiale, criteri/regole letti su Devpost. Confrontate Healthcare (istruzioni/teach-back), Cybersecurity (messaggio/piano di verifica) ed Education (misconcezione/applicazione) su sei criteri del blueprint, senza punteggi inventati. Healthcare unisce chiarezza e azionabilità con una journey locale; il nome non determina la selezione. Non si stima la probabilità di vittoria.

MVP: esempi sintetici di istruzioni di dimissione, passi in linguaggio semplice con citazioni, punti mancanti/ambigui, un teach-back esplicito, revisione ed export locale con provenienza. Una sola lingua (inglese nella UI di prodotto), una schermata. Nessuna diagnosi, triage, terapia/dosaggio generato, EHR, OCR, RAG, agente o database. Dati reali vietati nel prototipo. L'azione è una scheda da rivedere, non una cura eseguita.

Le citazioni dimostrano provenienza testuale, non verità clinica o implicazione semantica. Il confronto usa fonte e citazioni selezionate, non una sintesi client come verità; stati descrittivi al posto di confidence numerica. Test e benchmark separati devono controllare omissioni, condizioni invertite e falsi matched. AHRQ supporta il metodo teach-back, non l'efficacia di questa app.

[Architettura v1](architecture.md) e [criteri/test/misure](day-1.md) hanno guidato l'implementazione locale Healthcare; v0 ritirata. Provider reale/credenziali, prove semantiche live, elegibilità del team, gestione del lavoro pre-esistente e discordanza EDT/EST restano aperti.

## D011 — Mock limitato, corpus sintetico e avvio locale

Mock solo per due documenti esatti e due risposte preset: qualsiasi altro input riceve zero passi o unable_to_assess. Non usare matching generico per simulare inference AI. Fixture e badge sono visibili in API/UI/export.

Corpus di venti documenti con rubriche e trenta teach-back pre-annotati, senza pazienti reali. Evaluator offline controlla struttura; --run richiede provider reale, fa cinquanta richieste esplicite e conserva errori/risultati. Plan semantics restano non revisionate automaticamente; runner singolo non soddisfa l'intero protocollo comparativo.

Launcher stdlib multipiattaforma, senza nuove dipendenze, controlla porte e chiude soltanto i processi creati. Server sviluppo su loopback; nessun deployment pubblico autorizzato dal solo push GitHub.

## D012 — Pubblicazione GitHub richiesta dal titolare

L'utente ha autorizzato continuazione, commit e push al repository che sta creando (asclepius's-staff). URL e accesso devono essere verificati prima del push. Non pubblicare cache, venv, .env, log, export locali o report non revisionati; non inizializzare una storia remota divergente senza ispezione. Non inventare GitHub username o URL, non forzare push e non creare account senza consenso.

## D013 — Direzione visiva: editoriale clinico, due schermate

Scelta deliberata di design system, non estetica incidentale. Fondo carta calda, inchiostro profondo, un solo verde petrolio, un rosso riservato all'urgenza clinica e mai usato in questa versione. Tre famiglie tipografiche auto-ospitate con licenza OFL in `frontend/public/fonts`: Source Serif 4 per i titoli, Public Sans per l'interfaccia, IBM Plex Mono per valori, identificativi e tempi. Scala tipografica e spazi in un unico blocco `:root`; niente valori sparsi.

Griglia asimmetrica: documento originale a sinistra con righe numerate, colonna di lavoro a destra con un solo passo prioritario, poi gli altri, l'incertezza e la domanda teach-back. Seconda schermata di revisione obbligatoria. Nessun hero centrato, nessuna riga di tre card, nessuna chat di default, nessun gradiente o effetto vetro.

Ogni affermazione porta la fonte cliccabile, ogni suggerimento può essere accettato, modificato o messo da parte con motivazione, e il download si sblocca solo quando tutte le decisioni sono registrate. L'esportazione separa evidenza AI e decisioni umane. Stati progettati: skeleton, sorgente vuota, errore neutro che preserva il testo, incertezza dichiarata senza prove inventate, passaggio da rivedere. Contrasto, dimensioni dei target e focus sono misurati nel browser, non dichiarati: risultati in [status.md](status.md).

Dati sintetici realistici (persona fittizia etichettata, timestamp, farmaco, analisi con unità e intervalli di riferimento) sono riportati come dati della fonte e non interpretati. Nessun valore clinico viene dedotto, calcolato o consigliato.

## D014 — Il testo libero funziona offline con un motore dichiarato, non con un rifiuto

Problema: il mock rispondeva solo ai tre documenti dimostrativi. In una demo, chi incolla una nota propria riceveva un piano vuoto: il prodotto appariva un template.

Scelta: un motore deterministico in [rules.py](../backend/app/ai/rules.py) tratta qualsiasi testo sintetico, e ogni risultato dichiara il proprio `origin` nell'interfaccia e nel JSON esportato. Non viene spacciato per AI: sullo schermo la frase è in parole semplici («simple rules that copy words from your own text. No AI model was used»), mentre il codice esatto `LOCAL RULES ON YOUR TEXT · NOT AI` resta nel riquadro «How this was made» e nel file esportato.

Vincoli di sicurezza applicati per costruzione: una riga che menziona un farmaco non diventa mai un passo operativo ma una limitazione; le righe con esami e intervalli di riferimento restano dati; i metadati del documento non diventano passi; una riga che non si rivolge al lettore e non dà un comando non viene trattata come istruzione; le classi di indizi (scadenza, condizione, negazione, giorno, numero clinico) vengono confrontate come classi, così una parafrasi valida non viene scambiata per un'omissione, e i numeri di telefono non vengono richiesti al paziente.

La polarità viene controllata prima di ogni altro segnale: un'affermazione che inverte l'istruzione non può mai risultare `matched`. Il confronto sbaglia conservando la direzione sicura: **0 falsi `matched` su 30 casi**, con 5 paraphrasi valide che il motore rimanda alla revisione umana. Il corpus è stato usato per trovare difetti, non per gonfiare il punteggio: i difetti corretti erano classi semantiche generali, non casi nominali.

Limite dichiarato: senza un modello il motore non risolve significato, contraddizioni o ambiguità, e si astiene invece di indovinare. Configurare `AI_PROVIDER=openai` cambia la frase dell'interfaccia in «an AI model, then checked against the original wording» senza modificare contratto, validazione o interfaccia.

## D015 — Linguaggio semplice a schermo, codici tecnici sotto la piega

Problema: la schermata principale era scritta per chi valuta un progetto, non per chi sta uscendo dall'ospedale. Etichette in maiuscolo (`UNDERSTAND & EXPLAIN`, `START HERE / STEP 01`, `IN YOUR OWN WORDS`), un menu a tendina per scegliere il passo da ripetere, un badge di provenienza in codice e frasi come «Not marked as read or performed».

Scelta: la schermata principale parla come un paziente. Una domanda sola in alto («What should I do at home?»), un'azione sola («Show me my steps»), niente etichette maiuscole, e la scelta del passo diventa una lista di radio con la frase intera visibile invece di una tendina da ricordare. Anche il testo di risposta del backend è stato riscritto in parole quotidiane: il feedback della fixture non dice più «Scripted mock feedback».

La provenienza non è stata ridotta, solo spostata: sullo schermo resta una frase che dice chi ha scritto il testo, e i codici esatti (`origin`, `prompt_version`, `request_id`, tempi) si trovano nel riquadro «How this was made» in fondo alla colonna e nel JSON esportato. Lo stesso vale per «matched»: non viene chiamato comprensione, resta confronto di parole. Le garanzie intatte: link alla fonte cliccabile, Accetta/Modifica/Metti da parte, download bloccato fino a tutte le decisioni, stati skeleton/vuoto/errore/incertezza, target da 44px, contrasto AA.

Limite dichiarato: semplificare il linguaggio non rende l'interfaccia piùsicura. La verifica di comprensione resta un confronto testuale dichiarato come tale, e nessuna frase della UI promette che l'errore clinico sia stato prevenuto.

## D007 — Pubblicazione autorizzata separatamente

Licenza MIT scelta esplicitamente dal titolare e aggiunta in [LICENSE](../LICENSE). Nessun commit, push, deployment pubblico, creazione di account o submission automatica. Avvio locale dei due server e verifica browser autorizzati separatamente; nessun processo preesistente viene fermato.
