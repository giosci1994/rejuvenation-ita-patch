# -*- coding: utf-8 -*-
"""
Inserisce il codice \\gg[o|a] nelle frasi che si rivolgono al giocatore con un
accordo di genere.

L'inglese ha una sola frase per tutte e tre le scelte iniziali, quindi il
traduttore ha dovuto sceglierne una e ha messo il maschile. Qui le frasi
interessate vengono riscritte perche' il gioco decida a partita in corso.

    python accordo_genere.py --stima      quante frasi e quanto costa
    python accordo_genere.py --prova      assaggio su poche frasi
    python accordo_genere.py --applica    esegue e salva

Il controllo di sicurezza e' semplice e rigoroso: espandendo al maschile, la
frase deve tornare IDENTICA all'originale. Se il modello cambia anche una
virgola, la riscrittura viene scartata.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import percorsi
from traduci_api import Contatore, fai_client, spiega_errore, RIGA, PREZZI

# Frasi in seconda persona con un aggettivo o participio che si accorda.
CANDIDATE = re.compile(
    r"\b(?:sei|ti sei|eri|ti eri|sarai|sarest[i]|sembri|resti|rimani|diventi)\s+"
    r"(?:gi[aà]\s+|molto\s+|davvero\s+|proprio\s+|ancora\s+|troppo\s+)*"
    r"[a-zàèéìòù]+[oa]\b", re.IGNORECASE)

GG = re.compile(r"\\gg\[([^\]\|]*)\|([^\]\|]*)(?:\|([^\]]*))?\]")

SISTEMA = """Sei un revisore di traduzioni italiane di videogiochi.

Ricevi frasi italiane gia' tradotte, tratte da un gioco di ruolo. In alcune il \
testo si rivolge a chi sta giocando, con parole che in italiano si accordano al \
genere. All'inizio della partita si sceglie fra uomo, donna e non binario.

Il tuo compito: inserire il codice \\gg[maschile|femminile] SOLO dove una parola \
si accorda con la persona a cui il testo si rivolge.

Esempio: "Sei pronto?" diventa "Sei pront\\gg[o|a]?"
Esempio: "Ti sei alzato tardi." diventa "Ti sei alzat\\gg[o|a] tardi."
Esempio: "Non sei arrivato primo." diventa "Non sei arrivat\\gg[o|a] prim\\gg[o|a]."

ATTENZIONE, L'ERRORE PIU' FREQUENTE
In una stessa frase le parole da accordare possono essere PIU' DI UNA, anche \
lontane dal verbo. Devi marcarle TUTTE, non solo la prima.
  "sei stato piu' problematico di quanto pensassi"
  diventa
  "sei stat\\gg[o|a] piu' problematic\\gg[o|a] di quanto pensassi"
Si accordano i participi (stato, arrivato, venuto, rimasto) ma anche gli \
aggettivi riferiti a te (pronto, libero, sicuro, stanco, problematico, solo, \
bravo, fortunato), ovunque si trovino nella frase.
Se la frase contiene gia' qualche \\gg[..|..] da una revisione precedente, \
lasciali dove sono e aggiungi quelli mancanti.

REGOLE ASSOLUTE
1. Non cambiare NIENT'ALTRO. Nemmeno una virgola, un accento o uno spazio. \
L'unica modifica ammessa e' inserire \\gg[..|..] al posto della desinenza.
2. Metti il codice al posto della sola desinenza che cambia, non dell'intera \
parola: "pront\\gg[o|a]", non "\\gg[pronto|pronta]".
3. Se la frase NON si rivolge al giocatore, o se la parola non si accorda con \
lui, riporta la frase IDENTICA, senza toccarla. Molte frasi sono dialoghi fra \
altri personaggi: quelle vanno lasciate stare.
4. Attenzione ai falsi allarmi: "davvero", "proprio", "solo", "subito", "dopo" \
non si accordano mai. Non toccarli.
5. I codici come \\PN, \\c[6], {1}, §0§ vanno riportati identici.
6. Rispondi solo con le righe, nel formato [[numero]] testo, stessi numeri e \
stesso ordine, senza commenti."""


def al_maschile(testo):
    return GG.sub(lambda m: m.group(1), testo)


def candidate(testo):
    """
    Il controllo si fa sulla forma al maschile, non sul testo grezzo: cosi' una
    frase gia' marcata resta candidata e puo' essere completata. Serve perche'
    il modello, quando in una frase ci sono due parole da accordare, a volte ne
    prende solo una.
    """
    return bool(CANDIDATE.search(al_maschile(testo)))


def carica():
    """Frasi tradotte valide come candidate: id -> testo italiano."""
    fuori = {}
    with open(percorsi.TRADUZIONI, encoding="utf-8") as f:
        for line in f:
            try:
                o = json.loads(line)
            except Exception:
                continue
            if o.get("sez"):
                continue          # le sezioni di dati non contengono dialoghi
            fuori[o["id"]] = o["it"]
    return fuori


def unita(voci, per_richiesta):
    gruppi = []
    for i in range(0, len(voci), per_richiesta):
        blocco = voci[i:i + per_richiesta]
        righe = ["[[%d]] %s" % (n, t) for n, (_, t) in enumerate(blocco, 1)]
        gruppi.append({"testo": "\n".join(righe), "meta": blocco})
    return gruppi


def analizza(testo, meta):
    trovate = {}
    for riga in testo.splitlines():
        m = RIGA.match(riga)
        if m:
            trovate[int(m.group(1))] = m.group(2)

    buone, scartate, invariate = [], 0, 0
    for n, (ident, originale) in enumerate(meta, start=1):
        resa = trovate.get(n)
        if resa is None:
            scartate += 1
            continue
        if resa == originale or "\\gg[" not in resa:
            invariate += 1
            continue
        # Il controllo che conta: espandendo al maschile si deve riottenere la
        # frase di partenza, anch'essa espansa. Il confronto si fa fra le due
        # forme maschili perche' la frase in ingresso puo' gia' contenere
        # accordi messi in una passata precedente.
        if al_maschile(resa) != al_maschile(originale):
            scartate += 1
            continue
        buone.append({"id": ident, "it": resa})
    return buone, scartate, invariate


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--modello", default="claude-sonnet-5")
    ap.add_argument("--per-richiesta", type=int, default=40)
    ap.add_argument("--per-lotto", type=int, default=60)
    ap.add_argument("--limite", type=int, default=0)
    ap.add_argument("--stima", action="store_true")
    ap.add_argument("--prova", action="store_true")
    ap.add_argument("--applica", action="store_true")
    args = ap.parse_args()

    tutte = carica()
    voci = [(i, t) for i, t in tutte.items() if candidate(t)]
    voci.sort(key=lambda x: x[0])
    if args.prova and not args.limite:
        args.limite = 3 * args.per_richiesta
    if args.limite:
        voci = voci[:args.limite]

    print("frasi tradotte esaminate : %d" % len(tutte))
    print("candidate all'accordo    : %d" % len(voci))
    if not voci:
        return

    gruppi = unita(voci, args.per_richiesta)
    car = sum(len(g["testo"]) for g in gruppi)
    pin, pout = PREZZI.get(args.modello, PREZZI["claude-sonnet-5"])
    if args.prova:
        pin, pout = pin * 2, pout * 2
    tok_in = car / 4.0 + len(SISTEMA) / 4.0 * len(gruppi)
    stima = (tok_in / 1e6 * pin + car / 3.5 / 1e6 * pout) * 1.5
    print("richieste                : %d" % len(gruppi))
    print("costo stimato            : ~%.2f $" % stima)

    if args.stima:
        return
    if not (args.prova or args.applica):
        print("\nAnteprima. Usa --prova per un assaggio o --applica per eseguire.")
        return

    client = fai_client()
    if client is None:
        return

    cont = Contatore(args.modello, batch=not args.prova)
    buone_tot = scartate_tot = invariate_tot = 0

    def params(testo):
        p = {
            "model": args.modello, "max_tokens": 16000,
            "system": [{"type": "text", "text": SISTEMA}],
            "messages": [{"role": "user", "content": testo}],
        }
        if args.modello != "claude-haiku-4-5":
            p["output_config"] = {"effort": "low"}
            if args.modello != "claude-opus-5":
                p["thinking"] = {"type": "disabled"}
        return p

    def salva(buone):
        if not buone:
            return
        with open(percorsi.TRADUZIONI, "a", encoding="utf-8") as f:
            for b in buone:
                f.write(json.dumps(b, ensure_ascii=False) + "\n")

    try:
        if args.prova:
            print("\n--- assaggio ---\n")
            for g in gruppi:
                r = client.messages.create(**params(g["testo"]))
                testo = "".join(b.text for b in r.content if b.type == "text")
                cont.aggiungi(getattr(r, "usage", None), len(g["meta"]))
                buone, sc, inv = analizza(testo, g["meta"])
                for b in buone[:10]:
                    orig = dict(g["meta"])[b["id"]]
                    print("  PRIMA: %s\n  DOPO : %s\n" % (orig[:100], b["it"][:100]))
                buone_tot += len(buone); scartate_tot += sc; invariate_tot += inv
                salva(buone)
        else:
            for inizio in range(0, len(gruppi), args.per_lotto):
                fetta = gruppi[inizio:inizio + args.per_lotto]
                richieste = [{"custom_id": "g%d" % (inizio + i),
                              "params": params(u["testo"])}
                             for i, u in enumerate(fetta)]
                lotto = client.messages.batches.create(requests=richieste)
                print("\nlotto %s: %d richieste" % (lotto.id, len(richieste)))
                import time
                attesa = 20
                while True:
                    time.sleep(attesa)
                    st = client.messages.batches.retrieve(lotto.id)
                    print("  %s" % st.processing_status, flush=True)
                    if st.processing_status == "ended":
                        break
                    attesa = min(attesa * 1.5, 120)
                mappa = {"g%d" % (inizio + i): u for i, u in enumerate(fetta)}
                for res in client.messages.batches.results(lotto.id):
                    u = mappa.get(res.custom_id)
                    if u is None or res.result.type != "succeeded":
                        continue
                    testo = "".join(b.text for b in res.result.message.content
                                    if b.type == "text")
                    cont.aggiungi(getattr(res.result.message, "usage", None), len(u["meta"]))
                    buone, sc, inv = analizza(testo, u["meta"])
                    salva(buone)
                    buone_tot += len(buone); scartate_tot += sc; invariate_tot += inv
                print("  accordate %d, lasciate stare %d, scartate %d"
                      % (buone_tot, invariate_tot, scartate_tot))
    except Exception as e:
        if hasattr(e, "status_code"):
            spiega_errore(e)
            return
        raise

    print("\nfrasi con accordo aggiunto : %d" % buone_tot)
    print("lasciate invariate         : %d" % invariate_tot)
    print("scartate dal controllo     : %d" % scartate_tot)
    print(cont.riepilogo())
    print("\nOra ricostruisci la patch:  python costruisci.py")


if __name__ == "__main__":
    main()
