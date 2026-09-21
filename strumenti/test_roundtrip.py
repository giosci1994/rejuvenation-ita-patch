# -*- coding: utf-8 -*-
"""
Verifica che il writer Marshal produca byte identici a quelli generati da Ruby.

Gli OrderedHash dentro messages.dat sono blob auto-contenuti prodotti da
Marshal.dump([keys, values]) in Ruby: li ri-codifichiamo con il nostro writer e
confrontiamo i byte. Se combaciano, il formato e' corretto.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rmarshal
from rmarshal import UserDef

import percorsi

GAME = percorsi.trova_gioco()


def main():
    msgs = rmarshal.load_file(os.path.join(GAME, "Data", "messages.dat"))

    blobs = []
    for key, val in msgs.items():
        if key != 0 and isinstance(val, UserDef):
            blobs.append((str(key), val))
    for i, m in enumerate(msgs.get(0) or []):
        if isinstance(m, UserDef):
            blobs.append(("Map%d" % i, m))

    print("OrderedHash trovati: %d\n" % len(blobs))

    ok = bad = 0
    mismatches = []
    for name, ud in blobs:
        keys, values = rmarshal.load(ud.data)
        reenc = rmarshal.dump([keys, values])
        if reenc == ud.data:
            ok += 1
        else:
            bad += 1
            if len(mismatches) < 5:
                mismatches.append((name, len(ud.data), len(reenc)))

    print("byte-identici : %d" % ok)
    print("differenti    : %d" % bad)
    for name, a, b in mismatches:
        print("   %-12s originale %d byte, rigenerato %d byte" % (name, a, b))

    # round-trip completo della struttura radice
    print("\nRound-trip struttura completa...")
    rebuilt = {}
    for key, val in msgs.items():
        if key == 0:
            arr = []
            for m in val or []:
                if isinstance(m, UserDef):
                    k, v = rmarshal.load(m.data)
                    arr.append(UserDef(m.cls, rmarshal.dump([k, v])))
                else:
                    arr.append(m)
            rebuilt[key] = arr
        elif isinstance(val, UserDef):
            k, v = rmarshal.load(val.data)
            rebuilt[key] = UserDef(val.cls, rmarshal.dump([k, v]))
        else:
            rebuilt[key] = val

    raw = rmarshal.dump(rebuilt)
    back = rmarshal.load(raw)
    same_keys = set(map(str, back.keys())) == set(map(str, msgs.keys()))
    print("  dump: %.1f MB, chiavi coincidenti: %s" % (len(raw) / 1e6, same_keys))

    probe = None
    for key, val in back.items():
        if key != 0 and isinstance(val, UserDef):
            k, v = rmarshal.load(val.data)
            if k:
                probe = (str(key), k[0], v[0])
                break
    if probe:
        print("  esempio rileggibile -> [%s] %r = %r"
              % (probe[0], probe[1][:40], probe[2][:40]))

    print("\nESITO: %s" % ("OK" if bad == 0 and same_keys else "DA VERIFICARE"))


if __name__ == "__main__":
    main()
