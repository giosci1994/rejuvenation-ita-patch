# ⚖️ Diritti e attribuzioni · Rights and attribution

**🇮🇹 Italiano** · [🇬🇧 English](#english)

---

## Cos'è questo progetto

Una **traduzione amatoriale** in italiano di *Pokémon Rejuvenation*, distribuita
gratuitamente come patch. Non è un gioco, non contiene un gioco, e da sola non
serve a nulla: funziona solo insieme a una copia di Rejuvenation che devi
procurarti per conto tuo, gratuitamente, dal sito ufficiale del suo team.

Questo progetto **non è affiliato né approvato** da Nintendo, Game Freak,
Creatures Inc., The Pokémon Company o dal team di sviluppo di Rejuvenation.

## Cosa contiene, e cosa no

**Contiene:**

- il testo tradotto in italiano (`dati/traduzioni.jsonl` e il file `italiano.dat`
  che ne deriva)
- strumenti scritti da zero per estrarre, tradurre e ricompilare il testo
- due brevi script Ruby che aggiungono l'italiano al menu delle lingue

**Non contiene, e non conterrà mai:**

- il gioco, il suo eseguibile o una sua parte qualsiasi
- grafica, musiche, sprite, mappe o qualunque altra risorsa
- **il copione inglese del gioco.** È materiale del team di sviluppo. Il file
  `lavoro/da_tradurre.jsonl`, che lo conterrebbe, è escluso da git: chi vuole
  contribuire lo rigenera in locale dalla propria copia del gioco.

## Perché questa traduzione può esistere

Rejuvenation include un file, `Scripts/.translation.txt`, scritto dal suo team di
sviluppo, che spiega passo per passo come tradurre il gioco in un'altra lingua e
indica di impacchettare la cartella `patch` in uno zip e distribuirla ai propri
giocatori.

Questo progetto segue esattamente quella procedura. La possibilità di creare e
distribuire una traduzione è quindi prevista e incoraggiata da chi ha scritto il
testo originale.

## Licenze

| | |
|---|---|
| **Strumenti** (`strumenti/`, `installa.ps1`) | GPL-3.0, vedi [LICENSE](LICENSE) |
| **Testo tradotto** (`dati/`, `patch/italiano.dat`) | opera derivata, vedi sotto |

Gli strumenti sono opera originale e sono liberamente riutilizzabili: il lettore
del formato Ruby Marshal e la catena di traduzione funzionano con qualunque gioco
RPG Maker XP che usi Pokémon Essentials.

Il **testo tradotto** è invece un'opera derivata dal copione di Rejuvenation, di
cui non deteniamo i diritti: non possiamo concedere su di esso una licenza piena,
e non lo facciamo. È distribuito gratuitamente ai giocatori, per uso personale,
nei termini previsti dalla guida alla traduzione del gioco stesso. Ogni diritto
sull'opera originale resta ai rispettivi titolari.

Pokémon e i nomi dei Pokémon sono marchi di Nintendo, Creatures Inc. e Game Freak.

## Impegni

- **Nessuna monetizzazione.** Niente vendita, donazioni, pubblicità, link
  affiliati o contenuti a pagamento, ora o in futuro.
- **Nessuna ridistribuzione del gioco.** Non trovi qui link per scaricare
  Rejuvenation: rivolgiti al sito ufficiale del suo team.
- **Rimozione su richiesta.** Se fai parte del team di Rejuvenation, o
  rappresenti un titolare di diritti, e vuoi che questo progetto venga ritirato,
  apri una issue o scrivi: verrà rimosso senza discussioni e senza ritardi.

> Nota: questo documento descrive l'impostazione del progetto e le ragioni delle
> scelte fatte. Non è un parere legale.

---

<a name="english"></a>

# ⚖️ Rights and attribution

[🇮🇹 Italiano](#️-diritti-e-attribuzioni--rights-and-attribution) · **🇬🇧 English**

## What this is

An **unofficial fan translation** of *Pokémon Rejuvenation* into Italian,
distributed free of charge as a patch. It is not a game and contains no game. On
its own it does nothing: it only works alongside a copy of Rejuvenation that you
obtain yourself, free of charge, from its team's official site.

This project is **not affiliated with or endorsed by** Nintendo, Game Freak,
Creatures Inc., The Pokémon Company, or the Rejuvenation development team.

## What it contains, and what it does not

**It contains:** the Italian translated text, purpose-built tools to extract,
translate and recompile it, and two short Ruby snippets that add Italian to the
language menu.

**It does not contain, and never will:** the game or any part of it, any
graphics, music, sprites or other assets, or **the game's English script**, which
belongs to its developers. The file that would hold it is excluded from git;
contributors regenerate it locally from their own copy of the game.

## Why this translation may exist

Rejuvenation ships `Scripts/.translation.txt`, written by its development team,
explaining how to translate the game into another language and instructing
translators to pack the `patch` folder into a zip and distribute it to their
players. This project follows exactly that procedure.

## Licensing

The **tools** are original work under GPL-3.0 (see [LICENSE](LICENSE)) and can be
reused with any RPG Maker XP game built on Pokémon Essentials.

The **translated text** is a derivative work of Rejuvenation's script. We hold no
rights to the underlying work and therefore grant no licence over it. It is
provided free of charge for personal use, under the terms set out by the game's
own translation guide. All rights in the original work remain with their owners.

Pokémon and Pokémon character names are trademarks of Nintendo, Creatures Inc.
and Game Freak.

## Commitments

No monetisation of any kind, ever. No redistribution of the game. **Immediate
takedown on request** from the Rejuvenation team or any rights holder — open an
issue or get in touch, and this comes down without argument or delay.

> This document explains how the project is set up and why. It is not legal advice.
