# Audit / checklist submission

## Day 0

- [x] Stack frontend/backend del blueprint preparato.
- [x] Provider sostituibile, mock dichiarato, prompt versionato.
- [x] Input, JSON e output validati.
- [x] Timeout, rate limit, invalid response e provider failure gestiti.
- [x] Nessuna chiave reale aggiunta; `.env` escluso, `.env.example` presente.
- [x] Revisione umana prima dell'export; nessuna azione esterna.
- [x] Unit/API/UI test, typecheck e build: risultati in [status](status.md).
- [x] README, diagramma, decisioni, scheda Day 1 e script demo.
- [x] Licenza MIT autorizzata dal titolare.

## Prodotto — funzionante in locale, AI live ancora da verificare

- [x] Sei prompt confrontati con il sito ufficiale; track Healthcare scelto e criteri/regole consultati il 4 ottobre 2026.
- [ ] Elegibilità del team, attribuzione/ammissibilità del lavoro pre-esistente e discordanza deadline EDT/EST confermate.
- [x] Tre soluzioni confrontate sui sei criteri del blueprint, senza punteggi inventati.
- [x] Nome, descrizione, problema e target definiti; bisogno specifico di Asclepius ancora da validare con utenti.
- [x] MVP di sette criteri e unica journey specificati, non soltanto input → LLM → testo.
- [x] Diagramma, contratto v1 e modello dati documentati come **progettati**, distinti dalla v0 attiva.
- [ ] AI reale con ruolo necessario e dati consentiti. **Il motore offline rende il prodotto completo senza chiave**: regole deterministiche con citazioni verificate, dichiarate come non-AI nell’interfaccia e nel JSON. La chiave resta necessaria solo per la configurazione `model`.
- [x] Testo libero funzionante end-to-end: 4 passi citati, farmaco dirottato su limitazione, priorità clinica, confronto su risposta libera. Verificato nel browser con testo digitato, non solo con fixture.
- [x] Contratto v1 implementato e client/test migrati; piano citato, teach-back, revisione ed export mock con file ispezionato.
- [x] Test critical path con mock, browser, runtime/source validation e ispezione export.
- [ ] Prova live esplicita e verifica semantica: fixture non conta come AI.
- [ ] Frontend/backend/provider reali integrati e dimostrabili.
- [x] Protocollo di misure/baseline e corpus sintetico versionato (20 documenti, 30 risposte); evaluator offline passa, risultati live assenti.
- [x] Metriche misurate con denominatori: 20/20 documenti ancorati, 20/20 senza farmaco nei passi, 25/30 etichette corrette, **0 falsi `matched`** su 30. Limiti del campione dichiarati; i 5 scarti sono elencati per id.
- [x] Copione Devpost e script video di 3 minuti in [devpost.md](devpost.md), basati solo su fatti verificati.
- [ ] Privacy/consenso e human-in-the-loop adeguati al track.

## Repository / deployment

- [ ] Repository Git pubblico verificato e URL reale nel README.
- [ ] Nessun segreto, dato personale o file temporaneo nei file da pubblicare.
- [ ] Configurazione riproducibile e dipendenze rivalutate per il freeze.
- [ ] README del prodotto completo, team reale, diagramma adattato.
- [ ] HTTPS, auth, rate limiting, body limits, budget/concorrenza e proxy API.
- [ ] Live demo con percorso principale testato senza assistenza manuale.

## Demo / Devpost

- [x] Ispezione screenshot desktop/mobile nel browser, senza chiavi o dati personali.
- [ ] Screenshot salvati come artefatti submission e video registrato.
- [ ] Video pubblico 2–4 minuti: problema → input → AI → azione → impatto.
- [ ] Titolo, descrizione breve, track, problema, destinatari.
- [ ] Approccio tecnico e componenti AI realmente usati.
- [ ] Impatto senza numeri inventati o ranking soggettivi.
- [ ] Link reali a deployment, GitHub e video.
- [ ] Submission compilata e confermata dal titolare.
- [ ] Freeze feature e audit finale: solo bug critici dopo submission lock.

## Protocollo audit finale

Per ogni voce fallita annotare **severity, posizione, motivo, correzione minima**. Risolvere i problemi critici e rieseguire i test pertinenti. Non dichiarare conformità del prompt o submission completa basandosi sulla foundation.

Gate attuale: credenziali/provider live, valutazione semantica e URL/accesso GitHub per push autorizzato. Regole/elegibilità/timezone, deployment/video e submission restano separati. Nessun deployment pubblico o submission effettuato.
