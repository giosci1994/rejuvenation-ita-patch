# -*- coding: utf-8 -*-
"""
Mostra lo stato dei lotti inviati alla Batch API e non ancora incassati.

Si puo' lanciare da un'altra finestra mentre traduci_api.py sta lavorando: fa
solo letture, non interferisce e non costa nulla.

    python stato_lotti.py
"""
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from traduci_api import leggi_lotti, fai_client


def eta(momento):
    """L'API puo' restituire un datetime o una stringa ISO: regge entrambi."""
    if not momento:
        return "?"
    try:
        if isinstance(momento, str):
            momento = datetime.fromisoformat(momento.replace("Z", "+00:00"))
        if momento.tzinfo is None:
            momento = momento.replace(tzinfo=timezone.utc)
        minuti = (datetime.now(timezone.utc) - momento).total_seconds() / 60
        if minuti < 60:
            return "%d minuti fa" % minuti
        return "%.1f ore fa" % (minuti / 60)
    except Exception:
        return str(momento)


def main():
    pendenti = leggi_lotti()
    if not pendenti:
        print("Nessun lotto in sospeso: tutto incassato.")
        return

    client = fai_client()
    if client is None:
        return

    print("lotti in sospeso: %d\n" % len(pendenti))
    for voce in pendenti:
        s = client.messages.batches.retrieve(voce["lotto"])
        c = s.request_counts
        print("%s" % voce["lotto"])
        print("  stato    : %s" % s.processing_status)
        print("  creato   : %s" % eta(getattr(s, "created_at", None)))
        print("  richieste: %d in corso, %d completate, %d in errore"
              % (c.processing, c.succeeded, c.errored))
        scadenza = getattr(s, "expires_at", None)
        if scadenza:
            print("  scade    : %s" % scadenza)
        print()

    print("Finche' lo stato e' in_progress il lavoro procede sui server di")
    print("Anthropic. La garanzia formale e' di 24 ore, ma di solito e' molto")
    print("piu' rapido. Se chiudi traduci_api.py, riprendi i risultati con:")
    print("    python traduci_api.py --recupera")


if __name__ == "__main__":
    main()
