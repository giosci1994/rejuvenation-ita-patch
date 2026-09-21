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

## 📱 Android e 🍏 iOS

### La regola, identica su ogni dispositivo

Rejuvenation legge i propri file **relativamente alla cartella in cui si trova**,
su telefono esattamente come su computer. Non esiste quindi un percorso speciale
per il mobile: la cartella `patch` va messa **accanto a `Data` e `Graphics`**, e
basta.

Tutta la difficoltà sta nel trovare quella cartella sul telefono, perché dipende
dal programma con cui fai girare il gioco.

### Come essere certo di aver trovato la cartella giusta

Deve contenere `Data` e `Graphics`. Ma c'è un modo per non sbagliare:

> 💡 Su telefono Rejuvenation 14.0 gira sempre in **modalità portable**, cioè
> scrive i salvataggi dentro la propria cartella invece che nel sistema.
> **Se hai già giocato almeno una volta, nella cartella giusta trovi anche
> `Save Data`.**

Se vedi `Data`, `Graphics` e `Save Data` uno accanto all'altro, sei nel posto
giusto senza alcun dubbio. È il controllo più affidabile che esista, perché non
dipende dall'app che usi.

### Dove cercarla

Rejuvenation riconosce quattro modi di girare su mobile: **JoiPlay**, **Kirin**,
**Empo** e **RPG Player**. In tutti e quattro la cartella del gioco è una normale
cartella nella memoria del dispositivo, non nascosta dentro l'app.

**Con JoiPlay (Android)** — è la cartella che hai scelto tu quando hai estratto il
gioco e l'hai aggiunto a JoiPlay. Se non ricordi dove sia, il percorso è indicato
nelle impostazioni di quel gioco dentro JoiPlay. Le posizioni più comuni sono
`Download/`, `Documents/` o una cartella col nome del gioco nella memoria interna.

**Con Kirin, Empo o RPG Player** — questi lettori tengono i giochi in una propria
cartella, raggiungibile dall'app **File** su iOS e dal gestore file sulla memoria
interna su Android. Cerca la cartella col nome del gioco e verifica che dentro ci
siano `Data` e `Graphics`.

### La procedura

1. **Porta lo zip sul dispositivo** — scaricandolo direttamente, via cavo, o con
   un servizio cloud
2. **Estrailo.** Su Android va bene qualunque gestore file che sappia farlo
   (Files di Google, ZArchiver, Solid Explorer); su iOS basta toccare lo zip
   nell'app **File**
3. **Copia la cartella `patch`** dentro la cartella del gioco, accanto a `Data`

Se esiste già una cartella `patch` con altre mod, **uniscila** invece di
sostituirla: non c'è motivo di cancellare nulla.

Il risultato deve essere:

```
<cartella del gioco>/
├── Data/
├── Graphics/
├── Save Data/          (se hai gia' giocato)
└── patch/
    ├── italiano.dat
    ├── Init/intl.rb
    └── Mods/intl.rb
```

### Se Android non ti fa scrivere nella cartella

Da Android 11 in poi il sistema impedisce ai gestori file di terze parti di
scrivere dentro `Android/data`. Se il gioco sta lì, hai tre strade, in ordine di
comodità:

1. **Il gestore file di sistema** del telefono (quello preinstallato): le
   restrizioni non valgono per lui
2. **Il collegamento USB a un computer**: da PC vedi e scrivi tutto senza limiti
3. **La funzione di importazione del lettore**, se il programma che usi ne ha una

### Una nota sui salvataggi

Installare o togliere la traduzione **non tocca i salvataggi**: stanno in
`Save Data`, che questa patch non sfiora nemmeno. Puoi passare da italiano a
inglese e viceversa a partita in corso, senza perdere nulla.

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
