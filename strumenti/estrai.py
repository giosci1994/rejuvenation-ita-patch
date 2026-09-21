# -*- coding: utf-8 -*-
"""
Estrae da Data/messages.dat l'elenco delle stringhe uniche da tradurre.

Produce lavoro/da_tradurre.jsonl, una riga JSON per stringa:
    {"id": 123, "prio": 1, "sez": "Map012", "n": 4, "en": "testo inglese"}
  id   identificativo stabile (indice progressivo)
  prio 1 = storia/dialoghi, 2 = interfaccia e dati, 3 = descrizioni lunghe
  sez  una sezione in cui compare (a titolo di contesto)
  n    in quante sezioni compare

I backend di traduzione scrivono lavoro/tradotte.jsonl:
    {"id": 123, "it": "testo italiano"}
"""
import hashlib
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rmarshal
from rmarshal import UserDef

import argparse
import percorsi

LAVORO = percorsi.LAVORO

# Sezioni da NON tradurre: nomi propri identici in italiano.
ESCLUSE = {
    "Species",                    # i nomi dei Pokemon non cambiano
    "TrainerNames",               # nomi propri
    "BattleTowerTrainerNames",    # nomi propri
}

# Dialoghi e testo di gioco: la priorita' per capire la storia.
# ScriptTexts NON sta qui: contiene le voci di menu (New Game, Options, Bag...)
# e i messaggi di lotta, cioe' l'interfaccia, quindi va in priorita' 2.
PRIO1 = {
    "MapNames", "QuestDataMessages", "FieldMessages",
    "PlaceNames", "PlaceDescriptions", "RegionNames",
}


def ident(testo):
    """
    Identificativo stabile, derivato dal testo inglese e non dalla posizione.
    Cosi' cambiare priorita' o aggiornare il gioco non sposta gli id e le
    traduzioni gia' pagate restano agganciate alla stringa giusta.
    """
    return hashlib.sha1(testo.encode("utf-8")).hexdigest()[:16]

# Descrizioni lunghe: utili ma non indispensabili per seguire la trama.
PRIO3 = {
    "Entries", "ItemDescriptions", "MoveDescriptions", "AbilityDescs",
    "AbilityDescsLong", "MovesLong", "AbilitiesLong", "ItemPlurals",
    "ItemUnits", "FieldNotes", "BattleTowerIntroSpeech",
    "BattleTowerWinSpeech", "BattleTowerLoseSpeech", "AceSpeech",
    "EndSpeechLose", "PasswordDescriptions", "BlessingDescriptions",
    "BlessingRules", "CurrencyDescriptions", "MartDescriptions",
}


def sezioni(msgs):
    """Genera (nome_sezione, lista_valori) per tutte le sezioni del file."""
    for k, v in msgs.items():
        if k == 0 or not isinstance(v, UserDef):
            continue
        _, valori = rmarshal.load(v.data)
        yield str(k), valori
    for i, m in enumerate(msgs.get(0) or []):
        if isinstance(m, UserDef):
            _, valori = rmarshal.load(m.data)
            yield "Map%03d" % i, valori


def priorita(nome):
    if nome.startswith("Map"):
        return 1
    if nome in PRIO1:
        return 1
    if nome in PRIO3:
        return 3
    return 2


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    percorsi.aggiungi_argomento(ap)
    args = ap.parse_args()

    gioco = percorsi.trova_gioco(args.gioco)
    print("gioco: %s\n" % gioco)

    percorsi.assicura_lavoro()
    msgs = rmarshal.load_file(os.path.join(gioco, "Data", "messages.dat"))

    prima_sez = {}
    conteggio = defaultdict(int)
    prio = {}
    ordine = []

    for nome, valori in sezioni(msgs):
        if nome in ESCLUSE:
            continue
        p = priorita(nome)
        for s in valori:
            if not isinstance(s, str) or not s.strip():
                continue
            if s not in prima_sez:
                prima_sez[s] = nome
                prio[s] = {p}
                ordine.append(s)
            else:
                # Una stringa puo' comparire in piu' sezioni: le teniamo tutte.
                # Tenere solo la minima faceva sparire dall'interfaccia parole
                # come "Fire", che sta nei tipi ma anche in qualche dialogo.
                prio[s].add(p)
            conteggio[s] += 1

    def chiave(s):
        """
        Ordine di lavorazione, pensato per chi traduce con un budget limitato.

        Dentro i dialoghi si va per lunghezza DECRESCENTE: le righe lunghe sono
        la trama, quelle corte sono interiezioni comprensibili anche in inglese.
        Ordinare per frequenza, come facevo prima, avrebbe tradotto per primi i
        "..." e lasciato la storia in inglese.
        Le sezioni di servizio (nomi delle mappe, missioni) vengono prima: sono
        poche e servono per orientarsi.
        """
        p = min(prio[s])
        if p == 1:
            e_mappa = 1 if prima_sez[s].startswith("Map") else 0
            return (p, e_mappa, -len(s))
        return (p, 0, -conteggio[s])

    ordine.sort(key=chiave)

    out = os.path.join(LAVORO, "da_tradurre.jsonl")
    per_prio = defaultdict(lambda: [0, 0])
    with open(out, "w", encoding="utf-8") as f:
        for i, s in enumerate(ordine):
            tutte = sorted(prio[s])
            p = tutte[0]
            per_prio[p][0] += 1
            per_prio[p][1] += len(s)
            f.write(json.dumps({
                "id": ident(s), "prio": p, "prios": tutte,
                "sez": prima_sez[s], "n": conteggio[s], "en": s,
            }, ensure_ascii=False) + "\n")

    print("scritto %s" % out)
    print("\nstringhe uniche da tradurre: %d\n" % len(ordine))
    etichette = {1: "storia e dialoghi", 2: "interfaccia e dati",
                 3: "descrizioni lunghe"}
    tot_car = 0
    for p in sorted(per_prio):
        n, car = per_prio[p]
        tot_car += car
        print("  priorita' %d (%-19s) %7d stringhe  %9d caratteri  ~%7d parole"
              % (p, etichette[p], n, car, car // 5.5))
    print("\n  TOTALE                          %7d stringhe  %9d caratteri  ~%7d parole"
          % (len(ordine), tot_car, tot_car // 5.5))
    print("\n  sezioni escluse (nomi propri): %s" % ", ".join(sorted(ESCLUSE)))


if __name__ == "__main__":
    main()
