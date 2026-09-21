# -*- coding: utf-8 -*-
"""
Sostituisce i nomi di mosse, strumenti, abilita', tipi e nature con quelli
ufficiali italiani presi da dati/glossario_ufficiale.json.

Serve perche' il traduttore automatico, non conoscendo la terminologia
ufficiale, inventa nomi plausibili ma sbagliati: "Dream Eater" era diventato
"Sogniverno" invece di "Mangiasogni", e "Hyper Beam" era "Idrocannone", che in
italiano e' il nome di un'altra mossa.

Le correzioni sono limitate alla sezione di competenza: la mossa Thunderbolt
diventa Fulmine fra le mosse, ma altrove la stringa resta come sta.

    python correggi_termini.py            mostra cosa cambierebbe
    python correggi_termini.py --applica  scrive le correzioni
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import percorsi
import rmarshal
from rmarshal import UserDef
from estrai import ident

# categoria del glossario -> sezioni del gioco in cui applicarla
DESTINAZIONI = {
    "mosse": ["Moves", "MovesLong"],
    "strumenti": ["Items"],
    "abilita": ["Abilities", "AbilitiesLong"],
    "tipi": ["Types"],
    "nature": ["Natures"],
}


def valori_per_sezione(gioco):
    """Legge da messages.dat quali stringhe inglesi stanno in quali sezioni."""
    msgs = rmarshal.load_file(os.path.join(gioco, "Data", "messages.dat"))
    fuori = {}
    for k, v in msgs.items():
        if k == 0 or not isinstance(v, UserDef):
            continue
        _, valori = rmarshal.load(v.data)
        fuori[str(k)] = {s for s in valori if isinstance(s, str) and s}
    return fuori


def carica_attuali():
    globali, per_sezione = {}, {}
    if not os.path.exists(percorsi.TRADUZIONI):
        return globali, per_sezione
    with open(percorsi.TRADUZIONI, encoding="utf-8") as f:
        for line in f:
            try:
                o = json.loads(line)
            except Exception:
                continue
            if o.get("sez"):
                per_sezione[(o["id"], o["sez"])] = o["it"]
            else:
                globali[o["id"]] = o["it"]
    return globali, per_sezione


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    percorsi.aggiungi_argomento(ap)
    ap.add_argument("--applica", action="store_true",
                    help="scrive le correzioni invece di limitarsi a mostrarle")
    ap.add_argument("--mostra", type=int, default=12,
                    help="quanti esempi stampare per categoria")
    args = ap.parse_args()

    gioco = percorsi.trova_gioco(args.gioco)

    p = os.path.join(percorsi.DATI, "glossario_ufficiale.json")
    if not os.path.exists(p):
        print("Manca %s: generalo con  python glossario_ufficiale.py" % p)
        sys.exit(1)
    with open(p, encoding="utf-8") as f:
        ufficiale = json.load(f)

    sezioni = valori_per_sezione(gioco)
    globali, per_sezione = carica_attuali()

    nuove = []
    totale_cambi = 0

    for categoria, bersagli in DESTINAZIONI.items():
        nomi = ufficiale.get(categoria, {})
        cambi, gia_ok, assenti = [], 0, 0

        for sez in bersagli:
            presenti = sezioni.get(sez, set())
            for en, it in nomi.items():
                if en not in presenti:
                    continue
                i = ident(en)
                attuale = per_sezione.get((i, sez), globali.get(i))
                if attuale == it:
                    gia_ok += 1
                    continue
                cambi.append((sez, en, attuale, it))
                nuove.append({"id": i, "it": it, "sez": sez})

        totale_cambi += len(cambi)
        print("%-12s %4d da correggere, %4d gia' giusti" % (categoria, len(cambi), gia_ok))
        for sez, en, prima, dopo in cambi[:args.mostra]:
            print("    %-22s %-22s -> %s" % (en, (prima or "(nessuna)")[:22], dopo))
        if len(cambi) > args.mostra:
            print("    ... e altri %d" % (len(cambi) - args.mostra))
        print()

    print("correzioni totali: %d" % totale_cambi)

    if not args.applica:
        print("\nAnteprima soltanto. Per scriverle davvero:")
        print("    python correggi_termini.py --applica")
        return

    with open(percorsi.TRADUZIONI, "a", encoding="utf-8") as f:
        for n in nuove:
            f.write(json.dumps(n, ensure_ascii=False) + "\n")
    print("\nscritte in %s" % percorsi.TRADUZIONI)
    print("Ora ricostruisci la patch:  python costruisci.py")


if __name__ == "__main__":
    main()
