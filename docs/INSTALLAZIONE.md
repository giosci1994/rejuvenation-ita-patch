# 📘 Guida all'installazione

Tutto si riduce a copiare tre file nella cartella giusta e selezionare una voce
di menu. Questa guida spiega come farlo su ogni piattaforma e cosa controllare
se qualcosa non torna.

---

## Prima di iniziare

Ti serve **Pokémon Rejuvenation già installato e funzionante**. Non lo trovi qui
e non lo distribuiamo: scaricalo gratuitamente dal sito del suo team di sviluppo.

La traduzione è fatta di tre file:

```
patch/
├── italiano.dat      il testo tradotto (circa 24 MB)
├── Init/intl.rb      aggiunge l'italiano al menu delle lingue
└── Mods/intl.rb      lo riaggiunge dopo che il gioco lo azzera (serve davvero)
```

Vanno messi dentro la **cartella del gioco**, che riconosci perché contiene
`Data`, `Graphics` e l'eseguibile.

> ⚠️ Servono tutti e tre. Il file in `Mods/` sembra un doppione ma non lo è:
> Rejuvenation carica le sue impostazioni due volte, e la seconda cancella quanto
> fatto da `Init/`. Senza il file in `Mods/`, **la voce Language non compare**.

---

## 🪟 Windows

### Con l'installer (consigliato)

1. Scarica `rejuvenation-ita-patch.zip` dalla
   [pagina delle Release](https://github.com/giosci1994/rejuvenation-ita-patch/releases/latest)
2. **Estrai lo zip.** Non aprirlo e basta: Windows mostra il contenuto senza
   estrarlo davvero, e l'installer non funzionerebbe
3. Tasto destro su `installa.ps1` → **Esegui con PowerShell**

L'installer cerca il gioco nelle posizioni più comuni. Se non lo trova te lo
chiede: puoi **trascinare la cartella dentro la finestra** e premere Invio.

Se Windows blocca lo script, apri PowerShell nella cartella estratta ed esegui:

```powershell
powershell -ExecutionPolicy Bypass -File .\installa.ps1
```

### A mano

Estrai lo zip e trascina la cartella `patch` dentro la cartella del gioco.
Se te ne esiste già una, scegli **Unisci le cartelle**: le altre mod restano.

Alla fine devi avere:

```
Rejuvenation/
├── Data/
├── Graphics/
├── Rejuvenation.exe
└── patch/
    ├── italiano.dat
    ├── Init/intl.rb
    └── Mods/intl.rb
```

---

## 🐧 Linux · 🍎 macOS

Identico alla procedura manuale di Windows. Da terminale, dalla cartella dove
hai estratto lo zip:

```bash
cp -r patch/ "/percorso/della/cartella/Rejuvenation/"
```

Su macOS, se il gioco è dentro un `.app`, la cartella da usare è quella che
contiene `Data` e `Graphics`: la raggiungi con **Mostra contenuto pacchetto**.

---

## 📱 Android

I port Android di Rejuvenation girano su mkxp-z o JoiPlay, cioè lo stesso motore
della versione PC: **la traduzione funziona esattamente allo stesso modo**.

1. Scarica lo zip sul telefono, o passalo via cavo
2. Estrailo con un gestore file che sappia farlo (Files di Google, Solid
   Explorer, ZArchiver: uno vale l'altro)
3. Trova la cartella del gioco — è **quella che contiene `Data` e `Graphics`**

   Il percorso cambia da port a port. Guarda in:
   - `Android/data/<nome del pacchetto>/files/`
   - `Documents/`, `Download/` o una cartella col nome del gioco nella memoria interna
   - la cartella che ti ha indicato chi ha pubblicato il port

4. Copiaci dentro la cartella `patch`, unendola a quella esistente se c'è

Il risultato deve essere `.../Data`, `.../Graphics` e `.../patch/italiano.dat`
allo stesso livello.

> Se il gestore file non ti fa scrivere in `Android/data`, usa il gestore file di
> sistema del telefono oppure collega il telefono al computer via USB: le
> restrizioni di Android alle app di terze parti non valgono per l'uno né per l'altro.

---

## 🍏 iOS

Stessa logica. I port iOS distribuiscono i dati del gioco in una cartella
accessibile dall'app **File**.

1. Scarica lo zip e toccalo nell'app File per estrarlo
2. Apri **Sul mio iPhone** → la cartella dell'app del gioco
3. Trova la cartella che contiene `Data` e `Graphics`
4. Copiaci dentro `patch`

Se l'app non compare in **Sul mio iPhone**, il port non espone i suoi file e
l'installazione va fatta col metodo indicato da chi lo ha pubblicato.

---

## ✅ Attivare la traduzione

Avvia il gioco. Nel **menu principale**, in fondo, sotto *Controls*, compare una
voce nuova:

```
New Game
Other Save Files
Options
Save Directory
Controls
Language          ←  questa
```

Selezionala e scegli **Italiano**. Il gioco torna al titolo e da quel momento è
in italiano. La scelta viene ricordata: non devi rifarla a ogni avvio.

Per tornare all'inglese, stessa voce e scegli **English**.

---

## 🔍 Se qualcosa non va

### La voce «Language» non compare nel menu

Nel 99% dei casi manca `patch/Mods/intl.rb` o è nel posto sbagliato.

Controlla che il percorso sia **esattamente** `patch/Mods/intl.rb` dentro la
cartella del gioco. Un errore frequente è estrarre lo zip creando un livello in
più, tipo `patch/patch/Mods/intl.rb`.

Verifica anche di aver scelto la cartella giusta: deve contenere `Data`, e dentro
`Data` deve esserci `messages.dat`.

### La voce c'è, ma il gioco resta in inglese

Controlla che `patch/italiano.dat` esista e pesi circa 24 MB. Se pesa pochi KB,
il download si è interrotto: riscaricalo.

Se il file c'è ed è integro, riavvia il gioco: la lingua viene applicata
all'avvio.

### Qualche frase è ancora in inglese

È previsto. Restano non tradotte alcune centinaia di righe brevissime, per lo più
interiezioni. Sono lunghe pochi caratteri e non ostacolano la lettura.

Se trovi invece un **dialogo lungo** ancora in inglese,
[segnalalo](https://github.com/giosci1994/rejuvenation-ita-patch/issues): è
un buco vero e si può colmare.

### Ho aggiornato Rejuvenation e ora?

La patch continua a funzionare: le traduzioni sono agganciate al testo inglese,
non alla sua posizione, quindi un aggiornamento non le sposta. Le frasi nuove o
riscritte appariranno in inglese finché non vengono tradotte.

### Voglio togliere tutto

```powershell
.\installa.ps1 -Rimuovi
```

Oppure cancella a mano i tre file. **Nessun file originale del gioco viene mai
modificato**, quindi non c'è nulla da ripristinare: il gioco torna esattamente
com'era.
