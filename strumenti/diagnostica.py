# -*- coding: utf-8 -*-
"""Controlla che il reader consumi tutto il file e spiega il delta di dimensione."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rmarshal
from rmarshal import UserDef, MarshalReader

import percorsi

GAME = percorsi.trova_gioco()
path = os.path.join(GAME, "Data", "messages.dat")

raw = open(path, "rb").read()
r = MarshalReader(raw)
msgs = r.load()

print("file            : %d byte" % len(raw))
print("offset finale   : %d byte" % r.i)
print("byte non letti  : %d" % (len(raw) - r.i))
print("oggetti in tabella: %d   simboli: %d" % (len(r.objects), len(r.symbols)))

maps = msgs.get(0) or []
print("\nchiavi radice   : %d" % len(msgs))
print("voci array mappe: %d" % len(maps))

from collections import Counter
tipi = Counter(type(m).__name__ for m in maps)
print("tipi nelle mappe: %s" % dict(tipi))

tipi_root = Counter(type(v).__name__ for k, v in msgs.items() if k != 0)
print("tipi sezioni    : %s" % dict(tipi_root))

blob_tot = 0
for k, v in msgs.items():
    if k != 0 and isinstance(v, UserDef):
        blob_tot += len(v.data)
for m in maps:
    if isinstance(m, UserDef):
        blob_tot += len(m.data)
print("\nsomma byte dei blob OrderedHash: %d (%.1f MB)" % (blob_tot, blob_tot / 1e6))
print("differenza file - blob        : %d (%.1f MB)"
      % (len(raw) - blob_tot, (len(raw) - blob_tot) / 1e6))

# quante voci distinte e quanti oggetti condivisi (link) nel file originale
n_link = raw.count(b"@")
print("\nnota: i blob sono opachi, il resto e' la struttura radice")

# duplicati: lo stesso OrderedHash compare piu' volte?
ids = [id(m) for m in maps if isinstance(m, UserDef)]
print("blob mappa: %d totali, %d oggetti distinti" % (len(ids), len(set(ids))))
