# -*- coding: utf-8 -*-
"""Censisce i codici di controllo presenti nel testo: vanno preservati intatti."""
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rmarshal
from rmarshal import UserDef

import percorsi

GAME = percorsi.trova_gioco()


def decode_oh(ud):
    keys, values = rmarshal.load(ud.data)
    return dict(zip(keys, values))


def iter_strings(msgs):
    for key, val in msgs.items():
        if key == 0:
            continue
        h = decode_oh(val) if isinstance(val, UserDef) else val
        it = h.values() if isinstance(h, dict) else (h or [])
        for v in it:
            if isinstance(v, str) and v:
                yield v
    maps = msgs.get(0) or []
    for m in maps:
        if m is None:
            continue
        h = decode_oh(m) if isinstance(m, UserDef) else m
        for v in h.values():
            if isinstance(v, str) and v:
                yield v


PATTERNS = [
    ("backslash-code", re.compile(r"\\[A-Za-z]+(?:\[[^\]]*\])?")),
    ("backslash-simbolo", re.compile(r"\\[^A-Za-z\s]")),
    ("graffe {1}", re.compile(r"\{\d+\}")),
    ("tag <..>", re.compile(r"<[^<>\n]{1,30}>")),
    ("normalizzato <<x>>", re.compile(r"<<[^>]*>>")),
    ("percent %s", re.compile(r"%[sdif]")),
]


def main():
    msgs = rmarshal.load_file(os.path.join(GAME, "Data", "messages.dat"))
    counters = {name: Counter() for name, _ in PATTERNS}
    total = 0
    with_codes = 0

    for s in iter_strings(msgs):
        total += 1
        hit = False
        for name, rx in PATTERNS:
            for m in rx.findall(s):
                counters[name][m] += 1
                hit = True
        if hit:
            with_codes += 1

    print("stringhe analizzate: %d - contengono codici: %d (%.1f%%)\n"
          % (total, with_codes, 100.0 * with_codes / max(total, 1)))

    for name, _ in PATTERNS:
        c = counters[name]
        print("=== %s === (%d occorrenze, %d forme distinte)"
              % (name, sum(c.values()), len(c)))
        for tok, n in c.most_common(25):
            print("    %-28s %7d" % (repr(tok), n))
        print()


if __name__ == "__main__":
    main()
