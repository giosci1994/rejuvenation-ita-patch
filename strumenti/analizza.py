# -*- coding: utf-8 -*-
"""Ispeziona Data/messages.dat: struttura, numero di stringhe, volume di testo."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rmarshal
from rmarshal import Sym, UserDef

import percorsi

GAME = percorsi.trova_gioco()


def decode_ordered_hash(ud):
    """OrderedHash usa _dump -> Marshal.dump([keys, values]). Ritorna dict ordinato."""
    keys, values = rmarshal.load(ud.data)
    return dict(zip(keys, values))


def main():
    path = os.path.join(GAME, "Data", "messages.dat")
    print("Carico %s (%.1f MB)..." % (path, os.path.getsize(path) / 1e6))
    msgs = rmarshal.load_file(path)

    print("\nTipo radice: %s" % type(msgs).__name__)
    map_sections = 0
    tot_strings = 0
    tot_chars = 0
    uniq = set()

    print("\n--- Sezioni non-mappa ---")
    for key, val in msgs.items():
        if key == 0:
            continue
        if isinstance(val, UserDef):
            h = decode_ordered_hash(val)
            n = len(h)
            c = sum(len(v) for v in h.values() if isinstance(v, str))
            tot_strings += n
            tot_chars += c
            uniq.update(v for v in h.values() if isinstance(v, str))
            print("  %-26s %7d voci %10d caratteri" % (key, n, c))
        elif isinstance(val, list):
            n = len([v for v in val if v])
            c = sum(len(v) for v in val if isinstance(v, str))
            tot_strings += n
            tot_chars += c
            uniq.update(v for v in val if isinstance(v, str))
            print("  %-26s %7d voci %10d caratteri (Array)" % (key, n, c))
        else:
            print("  %-26s tipo inatteso: %s" % (key, type(val).__name__))

    maps = msgs.get(0)
    map_chars = 0
    map_strings = 0
    if isinstance(maps, list):
        for i, m in enumerate(maps):
            if m is None:
                continue
            h = decode_ordered_hash(m) if isinstance(m, UserDef) else m
            map_sections += 1
            map_strings += len(h)
            c = sum(len(v) for v in h.values() if isinstance(v, str))
            map_chars += c
            uniq.update(v for v in h.values() if isinstance(v, str))

    tot_strings += map_strings
    tot_chars += map_chars

    print("\n--- Mappe (sezione 0) ---")
    print("  mappe con testo: %d (indice max %d)" % (map_sections, len(maps) - 1 if maps else 0))
    print("  stringhe: %d  caratteri: %d" % (map_strings, map_chars))

    print("\n=== TOTALI ===")
    print("  stringhe totali:  %d" % tot_strings)
    print("  stringhe uniche:  %d" % len(uniq))
    print("  caratteri totali: %d (~%.1f MB di testo)" % (tot_chars, tot_chars / 1e6))
    words = sum(len(s.split()) for s in uniq)
    print("  parole uniche (token): ~%d" % words)


if __name__ == "__main__":
    main()
