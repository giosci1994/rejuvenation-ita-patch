# -*- coding: utf-8 -*-
"""
Traduce subito, senza API, le voci che il glossario copre in modo esatto:
le sezioni Types e Natures. Serve anche da collaudo della catena completa.

Uso:
    python semina_glossario.py
"""
import json
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
import percorsi
LAVORO = percorsi.LAVORO

# Sezione di origine -> voce del glossario da usare
SEZIONI = {"Types": "tipi", "Natures": "nature"}


def main():
    with open(os.path.join(QUI, "glossario.json"), encoding="utf-8") as f:
        g = json.load(f)

    fatte = set()
    out = percorsi.TRADUZIONI
    if os.path.exists(out):
        with open(out, encoding="utf-8") as f:
            for line in f:
                try:
                    fatte.add(json.loads(line)["id"])
                except Exception:
                    pass

    nuove = []
    with open(percorsi.DA_TRADURRE, encoding="utf-8") as f:
        for line in f:
            o = json.loads(line)
            chiave = SEZIONI.get(o["sez"])
            if not chiave or o["id"] in fatte:
                continue
            it = g[chiave].get(o["en"])
            if it:
                # "sez" limita la traduzione a quella sezione: "Hardy" e' una
                # natura qui, ma altrove e' il nome di un allenatore.
                nuove.append({"id": o["id"], "it": it, "sez": o["sez"]})

    with open(out, "a", encoding="utf-8") as f:
        for n in nuove:
            f.write(json.dumps(n, ensure_ascii=False) + "\n")

    print("aggiunte %d traduzioni dal glossario -> %s" % (len(nuove), out))


if __name__ == "__main__":
    main()
