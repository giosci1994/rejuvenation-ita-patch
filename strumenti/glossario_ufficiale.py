# -*- coding: utf-8 -*-
"""
Scarica i nomi ufficiali italiani di mosse, strumenti, abilita', tipi e nature
e li salva in dati/glossario_ufficiale.json.

I dati vengono dai CSV del progetto PokeAPI, che sono la trascrizione dei nomi
delle edizioni ufficiali. Si scaricano cinque file invece di interrogare l'API
migliaia di volte.

    python glossario_ufficiale.py
"""
import csv
import io
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import percorsi

BASE = "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/"
UA = {"User-Agent": "rejuvenation-ita-patch (glossario terminologia ufficiale)"}

IT, EN = "8", "9"          # identificativi di lingua usati da PokeAPI

# file CSV -> (nome della colonna con l'id, etichetta nel glossario)
FONTI = [
    ("move_names.csv", "move_id", "mosse"),
    ("item_names.csv", "item_id", "strumenti"),
    ("ability_names.csv", "ability_id", "abilita"),
    ("type_names.csv", "type_id", "tipi"),
    ("nature_names.csv", "nature_id", "nature"),
]

USCITA = os.path.join(percorsi.DATI, "glossario_ufficiale.json")


def scarica(nome):
    req = urllib.request.Request(BASE + nome, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def coppie(testo, colonna_id):
    """Ricava inglese -> italiano appaiando le righe con lo stesso id."""
    righe = list(csv.DictReader(io.StringIO(testo)))
    inglese, italiano = {}, {}
    for r in righe:
        chiave = r.get(colonna_id)
        lingua = r.get("local_language_id")
        nome = (r.get("name") or "").strip()
        if not chiave or not nome:
            continue
        if lingua == EN:
            inglese[chiave] = nome
        elif lingua == IT:
            italiano[chiave] = nome

    fuori = {}
    for chiave, en in inglese.items():
        it = italiano.get(chiave)
        if it:
            fuori[en] = it
    return fuori


def main():
    os.makedirs(percorsi.DATI, exist_ok=True)
    glossario = {}
    print("Scarico i nomi ufficiali dai dati di PokeAPI.\n")

    for nome, colonna, etichetta in FONTI:
        try:
            testo = scarica(nome)
        except Exception as e:
            print("  %-12s non scaricato: %s" % (etichetta, e))
            continue
        d = coppie(testo, colonna)
        glossario[etichetta] = d
        uguali = sum(1 for k, v in d.items() if k == v)
        print("  %-12s %5d nomi  (%d identici all'inglese)" % (etichetta, len(d), uguali))

    if not glossario:
        print("\nNessun dato scaricato: controlla la connessione.")
        sys.exit(1)

    with open(USCITA, "w", encoding="utf-8") as f:
        json.dump(glossario, f, ensure_ascii=False, indent=1, sort_keys=True)

    tot = sum(len(v) for v in glossario.values())
    print("\nscritto %s" % USCITA)
    print("  %d nomi ufficiali in totale, %.0f KB"
          % (tot, os.path.getsize(USCITA) / 1024))


if __name__ == "__main__":
    main()
