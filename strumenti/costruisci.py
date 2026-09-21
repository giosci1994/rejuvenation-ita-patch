# -*- coding: utf-8 -*-
"""
Assembla patch/italiano.dat a partire da lavoro/tradotte.jsonl.

Ricrea la stessa struttura di Data/messages.dat tenendo le chiavi inglesi
originali e sostituendo i valori con la traduzione. Le stringhe non ancora
tradotte vengono omesse: a runtime il gioco ricade automaticamente sull'inglese,
quindi la patch e' utilizzabile anche a traduzione parziale.

Scrive anche patch/Init/intl.rb, che aggiunge l'italiano al menu delle lingue.

Uso:
    python costruisci.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rmarshal
from rmarshal import Sym, UserDef
from estrai import ESCLUSE          # stesse sezioni saltate in estrazione

import argparse
import percorsi

LAVORO = percorsi.LAVORO
PATCH = percorsi.PATCH

DEFINIZIONE = """LANGUAGES = {
  "English"  => nil,
  "Italiano" => "patch/italiano.dat",
}
"""

INIT_RB = """# Aggiunge l'italiano alle lingue disponibili.
# Generato da _traduzione/tools/costruisci.py - non modificare a mano.
%s""" % DEFINIZIONE

# Rejuv/Settings compare DUE volte in Scripts/Rejuv/Bootstrap.rb: in INIT e poi
# di nuovo in SCRIPTS. Il secondo caricamento rimette LANGUAGES a vuoto e
# cancella quanto fatto da patch/Init. I file in patch/Mods vengono caricati
# dopo (ScriptLoader.rb riga 165) con lo stesso eval, quindi qui la definizione
# regge fino al menu principale.
MODS_RB = """# Ridefinisce le lingue DOPO il secondo caricamento di Rejuv/Settings,
# che altrimenti azzererebbe LANGUAGES. Vedi ScriptLoader.rb riga 165.
# Generato da _traduzione/tools/costruisci.py - non modificare a mano.
%s""" % DEFINIZIONE


def carica_traduzioni():
    """
    Ritorna (globali, per_sezione).

    globali[inglese] = italiano             vale ovunque
    per_sezione[(sezione, inglese)] = it    vale solo in quella sezione

    Le traduzioni limitate a una sezione servono per le parole ambigue: "Hardy"
    e' una natura, ma anche il nome di un allenatore.
    """
    per_id = {}
    p = percorsi.TRADUZIONI
    if not os.path.exists(p):
        print("Non trovo la traduzione in %s" % p)
        print("Dovrebbe arrivare col repository: prova a riscaricarlo.")
        sys.exit(1)
    if not os.path.exists(percorsi.DA_TRADURRE):
        print("Manca l'indice delle stringhe del gioco.")
        print("Generalo dalla tua copia di Rejuvenation con:")
        print("    python estrai.py")
        sys.exit(1)
    # Una stringa puo' avere sia una traduzione valida ovunque sia una diversa
    # limitata a una sezione: "Thunderbolt" e' la mossa Fulmine fra le mosse, ma
    # altrove puo' voler dire altro. Le due cose convivono.
    per_sezione_id = {}
    with open(p, encoding="utf-8") as f:
        for line in f:
            try:
                o = json.loads(line)
            except Exception:
                continue
            if o.get("sez"):
                per_sezione_id[(o["id"], o["sez"])] = o["it"]
            else:
                per_id[o["id"]] = o["it"]

    globali, per_sezione = {}, {}
    inglese_di = {}
    with open(percorsi.DA_TRADURRE, encoding="utf-8") as f:
        for line in f:
            o = json.loads(line)
            inglese_di[o["id"]] = o["en"]
            it = per_id.get(o["id"])
            if it:
                globali[o["en"]] = it

    for (ident, sez), it in per_sezione_id.items():
        en = inglese_di.get(ident)
        if en and it:
            per_sezione[(sez, en)] = it

    return globali, per_sezione


def ordered_hash(coppie):
    """Costruisce un UserDef OrderedHash come lo scriverebbe Ruby."""
    chiavi = [k for k, _ in coppie]
    valori = [v for _, v in coppie]
    blob = rmarshal.dump([chiavi, valori])
    # @keys viaggia in una lista distinta: nel file Ruby e' un oggetto a se'
    return UserDef(Sym("OrderedHash"), blob, {Sym("@keys"): list(chiavi)})


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    percorsi.aggiungi_argomento(ap)
    args = ap.parse_args()

    gioco = percorsi.trova_gioco(args.gioco)
    print("gioco: %s" % gioco)

    globali, per_sezione = carica_traduzioni()
    print("traduzioni: %d globali, %d limitate a una sezione\n"
          % (len(globali), len(per_sezione)))

    def traduci(sezione, valore):
        if not isinstance(valore, str):
            return None
        return per_sezione.get((sezione, valore)) or globali.get(valore)

    msgs = rmarshal.load_file(os.path.join(gioco, "Data", "messages.dat"))
    fuori = {}
    tot_voci = tot_tradotte = 0
    sezioni_piene = 0

    # sezioni con chiave simbolica
    for k, v in msgs.items():
        if k == 0 or not isinstance(v, UserDef):
            continue
        if str(k) in ESCLUSE:          # nomi propri: restano in inglese
            continue
        chiavi, valori = rmarshal.load(v.data)
        coppie = []
        for ch, va in zip(chiavi, valori):
            tot_voci += 1
            it = traduci(str(k), va)
            if it:
                coppie.append((ch, it))
                tot_tradotte += 1
        if coppie:
            fuori[k] = ordered_hash(coppie)
            sezioni_piene += 1

    # sezione 0: array indicizzato per id mappa
    mappe = msgs.get(0) or []
    nuove = []
    mappe_piene = 0
    for idx, m in enumerate(mappe):
        if not isinstance(m, UserDef):
            nuove.append(None)
            continue
        nome = "Map%03d" % idx
        chiavi, valori = rmarshal.load(m.data)
        coppie = []
        for ch, va in zip(chiavi, valori):
            tot_voci += 1
            it = traduci(nome, va)
            if it:
                coppie.append((ch, it))
                tot_tradotte += 1
        if coppie:
            nuove.append(ordered_hash(coppie))
            mappe_piene += 1
        else:
            nuove.append(None)
    if any(n is not None for n in nuove):
        fuori[0] = nuove

    if not fuori:
        print("Nessuna voce tradotta: non scrivo nulla.")
        return

    os.makedirs(os.path.join(PATCH, "Init"), exist_ok=True)
    os.makedirs(os.path.join(PATCH, "Mods"), exist_ok=True)
    dest = os.path.join(PATCH, "italiano.dat")
    rmarshal.dump_file(dest, fuori)

    with open(os.path.join(PATCH, "Init", "intl.rb"), "w", encoding="utf-8") as f:
        f.write(INIT_RB)
    with open(os.path.join(PATCH, "Mods", "intl.rb"), "w", encoding="utf-8") as f:
        f.write(MODS_RB)

    # rilettura di controllo
    ricarico = rmarshal.load_file(dest)
    campione = None
    for k, v in ricarico.items():
        if k != 0 and isinstance(v, UserDef):
            ch, va = rmarshal.load(v.data)
            if ch:
                campione = (str(k), ch[0], va[0])
                break

    perc = 100.0 * tot_tradotte / max(tot_voci, 1)
    print("voci nel gioco      : %d" % tot_voci)
    print("voci tradotte       : %d  (%.1f%%)" % (tot_tradotte, perc))
    print("sezioni riempite    : %d + %d mappe" % (sezioni_piene, mappe_piene))
    print("\nscritto: %s  (%.1f MB)" % (dest, os.path.getsize(dest) / 1e6))
    print("scritto: %s" % os.path.join(PATCH, "Init", "intl.rb"))
    print("scritto: %s" % os.path.join(PATCH, "Mods", "intl.rb"))
    if campione:
        print("\ncontrollo di rilettura -> [%s] %r = %r"
              % (campione[0], campione[1][:50], campione[2][:50]))
    print("\nIn gioco: menu principale -> Language -> Italiano")


if __name__ == "__main__":
    main()
