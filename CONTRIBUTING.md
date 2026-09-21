# 🤝 Contribuire

La cosa più utile che puoi fare è **segnalare una frase tradotta male**. Su
135.000 righe qualche scivolone c'è di sicuro, e chi gioca lo nota molto prima di
chi ha costruito la patch.

---

## Segnalare e basta

[Apri una issue](https://github.com/giosci1994/rejuvenation-ita-patch/issues/new)
con:

- la frase come appare **in italiano** nel gioco
- la frase **inglese** originale, se riesci a recuperarla (basta rimettere
  English dal menu e rileggere il punto)
- dove l'hai vista, anche solo all'incirca

Non serve altro. Se non sai qual era l'inglese, segnala lo stesso: si trova.

---

## Correggerla da solo

Ti servono Python 3.9 o superiore e la tua copia di Rejuvenation.

### 1. Genera l'indice delle stringhe

```bash
cd strumenti
python estrai.py --gioco "C:\percorso\del\gioco"
```

Questo crea `lavoro/da_tradurre.jsonl` dalla **tua** copia del gioco. Non è nel
repository di proposito: conterrebbe il copione inglese integrale di
Rejuvenation, che è materiale del suo team di sviluppo e non va ridistribuito.

Il percorso del gioco viene ricordato in `gioco.txt`: lo indichi una volta sola.

### 2. Trova la riga da correggere

Ogni stringa ha un identificativo stabile, ricavato dal testo inglese:

```bash
python -c "import hashlib; print(hashlib.sha1('Testo inglese esatto'.encode()).hexdigest()[:16])"
```

Cerca quell'identificativo in `dati/traduzioni.jsonl` e correggi il campo `it`.

Se preferisci cercare per contenuto, `da_tradurre.jsonl` associa ogni
identificativo alla frase inglese: apri i due file affiancati.

### 3. Ricostruisci e prova

```bash
python costruisci.py
```

Copia `patch/` nel gioco e verifica in partita che la frase sia giusta.

### 4. Proponi la modifica

Una pull request con il solo `dati/traduzioni.jsonl` modificato. Nella
descrizione metti la frase inglese, la vecchia resa e la nuova.

---

## Regole di traduzione

Sono codificate in [`strumenti/glossario.json`](strumenti/glossario.json), che
contiene la terminologia ufficiale italiana per tipi, nature, statistiche,
interfaccia e stati.

- **Nomi dei Pokémon invariati** (Bulbasaur, Charizard...), come nelle edizioni
  italiane ufficiali
- **Nomi propri invariati** per persone, luoghi e istituzioni
- **Del tu, sempre**, anche in cartelli e avvisi pubblici
- **Terminologia ufficiale**: Lanciafiamme, Pozione, Capopalestra, PS, MT
- **Tono preservato**: Rejuvenation ha registri adulti, sarcasmo e volgarità.
  Vanno resi, non addolciti
- **Accenti veri**: è, à, ì, ò, ù, é. Mai `e'` o `gia'`

### I codici di controllo

Alcune stringhe contengono codici che il gioco interpreta: `\PN` è il nome del
giocatore, `\c[6]` cambia colore, `<icon=fieldUp>` disegna un'icona, `{1}` è un
segnaposto. **Vanno riportati identici**, nello stesso numero. Puoi spostarli se
la sintassi italiana lo richiede, ma non aggiungerne, toglierne o rinumerarli.

`costruisci.py` non ha modo di accorgersene, ma `traduci_api.py` sì: scarta ogni
riga che non li conserva tutti. Se correggi a mano, controlla tu.

---

## Tradurre in un'altra lingua

Gli strumenti non hanno nulla di specifico per l'italiano. Per un'altra lingua:

1. Riscrivi `strumenti/glossario.json` con la terminologia della tua lingua
2. Adatta il prompt in `strumenti/traduci_api.py` (funzione `costruisci_sistema`)
3. Cambia il nome del file in `costruisci.py` (`DEFINIZIONE` e `italiano.dat`)

Funzionano con qualunque gioco RPG Maker XP basato su Pokémon Essentials, non
solo con Rejuvenation.

---

## Cosa non accettiamo

- File del gioco, risorse, grafica, audio
- Il copione inglese, in qualunque forma
- Link per scaricare Rejuvenation
- Qualunque forma di monetizzazione

Le ragioni sono in [NOTICE.md](NOTICE.md).
