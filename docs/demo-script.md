# Demo script

## Day 0 — Verifica tecnica, circa 60 secondi

**Storico: UI Day 0 ritirata dopo la migrazione Healthcare.** I passi sotto documentano la vecchia prova, non l'interfaccia corrente.

1. Aprire la pagina. Mostrare il badge Day 0 e l'avviso «nessuna AI reale».
2. Verificare che input vuoto o troppo corto non consenta invio.
3. Usare l'esempio sintetico, inviare e osservare loading.
4. Mostrare sintesi, motivazione, raccomandazione, confidence non disponibile e azione proposta.
5. Mostrare che export è bloccato finché l'utente non conferma la revisione.
6. Confermare ed esportare JSON. Spiegare che è solo un download: nessuna raccomandazione è eseguita.
7. Cambiare l'input: il risultato precedente viene invalidato.

Questa prova non dimostra la necessità AI, il valore di un prodotto o la conformità al track. È un gate dell'infrastruttura.

## Healthcare — Demo verificata nel browser, 30–60 secondi

Interfaccia editoriale, due schermate, percorso cliccabile con il caso sintetico precaricato (Amira Patel, finzione). Avviare [scripts/dev.py](../scripts/dev.py).

**Percorso B, testo libero (consigliato per la live):** premere “Edit the note”, incollare una nota sintetica propria, spuntare la conferma e premere “Show me my steps”. La frase iniziale passa da «Written by a prepared demo example. No AI looked at this note» a «Written by simple rules that copy words from your own text. No AI model was used»: è questo passaggio che dimostra che il prodotto non è un template. I passi sono ordinati per priorità clinica (prima la febbre), ogni passo cita la propria riga, e una riga che menziona un farmaco diventa una limitazione, non un’istruzione di somministrazione.

Testo usato nella verifica reale (sintetico, non nota clinica):

```
Take your blood pressure tablet once daily in the morning.
Call the ward on 555 0100 if you have a fever above 38 C.
Book the clinic review within seven days, even if you feel better.
Do not lift anything heavier than 5 kg for two weeks.
Bring your discharge letter to the review.
```

Con «I will call the ward on Friday if I still feel unwell» il confronto risponde che il venerdì non compare nelle istruzioni e cita S2. Con il solo numero di telefono cambiato il confronto lo ignora di proposito.1. **Leggere** — mostrare la nota originale con righe numerate e il riquadro del paziente finzionale (62 anni, documento emesso 04 ott 2026 09:20 UTC). Espandere «The medicine and test results written in the note» per mostrare atorvastatin 20 mg registrato senza schema di somministrazione e i valori con unità e intervallo di riferimento.

2. **Capire** — spuntare la conferma e premere “Show me my steps”: il primo passo appare con la sua formulazione originale (S4) e i controlli Accetta/Modifica/Metti da parte.

3. **Rispiegare** — scegliere lo step nei radio e premere “Example that misses something” («I only need to arrange the follow-up if I still feel unwell»), poi “Check what I said”: il feedback evidenzia «even if you feel better» con la fonte S4 e resta descrittivo, non accusatorio.

4. **Rivedere** — “Check it and save”: ogni passaggio, limitazione, domanda e confronto richiede una decisione. Provare Modifica su un passo e poi Reset per mostrare che l'evidenza resta invariata.

5. **Portare via** — spuntare la conferma e scaricare: il JSON contiene fonte, piano, feedback, decisioni umane e limiti. Dire ad alta voce che è un documento da discutere, non una cura eseguita.

Casi limite già verificati nella stessa interfaccia: sorgente vuota, errore provider con testo originale intatto, «I could not check this one» senza prove, zero passi accettati.

**Prova anti-demo-artificiale:** modificare la fonte o la spiegazione invalida risultati e revisione. Con il motore offline il testo libero non viene più respinto: viene elaborato e dichiarato come regole deterministiche. Non presentare l’etichetta `DEMO FIXTURE` come generazione dal vivo e non presentare `LOCAL RULES` come AI: sono due motori diversi, dichiarati nell’interfaccia e nel JSON esportato.

## Video finale — Struttura proposta, 2–4 minuti

- **0:00–0:20 / Problema:** un paziente/caregiver può leggere un'istruzione senza capirne una condizione. Scenario sintetico; citare il metodo teach-back senza attribuire efficacia misurata ad Asclepius.
- **0:20–0:40 / Soluzione:** Asclepius rende visibili fonte, passi e possibili fraintendimenti, prima di creare una scheda da rivedere.
- **0:40–2:30 / Live demo:** input → piano citato → spiegazione a parole proprie → confronto → revisione → export. **Fare due prove:** prima il caso precaricato, poi un testo incollato al volo che mostri il cambio della frase sul motore. Usare dati consentiti; non mascherare il motore usato.
- **2:30–3:15 / Tecnologia:** i tre motori dichiarati, segmentazione deterministica, validazione stretta delle citazioni, regole offline misurate sul corpus (20/20 ancorate, 25/30 etichette, **0 falsi `matched`**).
- **3:15–3:45 / Impatto:** misure raccolte, limiti, destinatari e possibilità di estensione. Dichiarare che non esiste validazione clinica né studio utenti.
- **Chiusura:** nome progetto, URL repository, live demo e video verificati.

Prima della registrazione: provider funzionante, limiti/budget, nessun segreto sullo schermo, demo ripetibile, fallback spiegato e non spacciato per AI live.
