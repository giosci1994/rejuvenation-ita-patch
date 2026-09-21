# -*- coding: utf-8 -*-
"""
Prove sul cuore della catena: il formato Ruby Marshal e la protezione dei
codici di controllo.

Non serve il gioco, quindi girano anche su GitHub Actions. Se una di queste
cede, la patch non si carica o arriva in gioco con i codici rotti.

    python test_formato.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import protezione
import rmarshal
from rmarshal import Sym, UserDef

esiti = []


def prova(nome, condizione, dettaglio=""):
    esiti.append((nome, bool(condizione), dettaglio))


def test_marshal():
    """Il file che produciamo deve essere rileggibile e stabile."""
    chiavi = ["Ciao", "Mondo", "Frase con accenti"]
    valori = ["Salve", "Terra", "è perché già così"]

    blob = rmarshal.dump([chiavi, valori])
    oh = UserDef(Sym("OrderedHash"), blob, {Sym("@keys"): list(chiavi)})
    radice = {0: [None, oh], Sym("Moves"): oh}

    grezzo = rmarshal.dump(radice)
    riletto = rmarshal.load(grezzo)

    k, v = rmarshal.load(riletto[Sym("Moves")].data)
    prova("le chiavi sopravvivono al giro", k == chiavi)
    prova("i valori sopravvivono, accenti compresi", v == valori)
    prova("la riscrittura e' stabile", rmarshal.dump(riletto) == grezzo)
    prova("le mappe vuote restano vuote", riletto[0][0] is None)
    prova("l'ivar @keys viene conservata",
          riletto[Sym("Moves")].ivars.get(Sym("@keys")) == chiavi)


def test_protezione():
    """I codici del gioco devono tornare identici dopo la traduzione."""
    casi = [
        "\\PN ha trovato {1}!",
        "<c=green>Attenzione</c> \\c[6]rosso\\c[0]",
        "Sei pront\\gg[o|a] per la sfida?",
        "Due \\gg[un padre|una madre|un genitore] e \\gg[o|a]",
        "Riga uno\nRiga due",
        "Niente codici qui dentro",
    ]
    for originale in casi:
        mascherato, codici = protezione.maschera(originale)
        prova("ripristino di %r" % originale[:28],
              protezione.ripristina(mascherato, codici) == originale)
        prova("verifica di %r" % originale[:28],
              protezione.verifica(originale, originale) is None)

    # una traduzione che perde un codice deve essere respinta
    rotta = "Ha trovato {1}!"
    prova("una traduzione che perde \\PN viene respinta",
          protezione.verifica("\\PN ha trovato {1}!", rotta) is not None)


def test_accordo_genere():
    """Espandere al maschile deve restituire il testo di partenza."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from accordo_genere import al_maschile

    coppie = [
        ("Sei pront\\gg[o|a]!", "Sei pronto!"),
        ("Sei stat\\gg[o|a] \\gg[un padre|una madre|un genitore].",
         "Sei stato un padre."),
        ("Nessun codice.", "Nessun codice."),
    ]
    for marcato, atteso in coppie:
        prova("espansione al maschile di %r" % marcato[:26],
              al_maschile(marcato) == atteso,
              "ottenuto %r" % al_maschile(marcato))


def main():
    test_marshal()
    test_protezione()
    test_accordo_genere()

    falliti = [e for e in esiti if not e[1]]
    for nome, ok, dettaglio in esiti:
        print("  %s  %s%s" % ("ok  " if ok else "FALLITO", nome,
                              ("  -> " + dettaglio) if (not ok and dettaglio) else ""))
    print("\n%d prove, %d fallite" % (len(esiti), len(falliti)))
    if falliti:
        sys.exit(1)


if __name__ == "__main__":
    main()
