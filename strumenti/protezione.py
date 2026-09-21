# -*- coding: utf-8 -*-
"""
Protezione dei codici di controllo.

Il testo del gioco contiene codici che NON vanno tradotti ne' alterati:
  \\PN \\v[12] \\c[6] \\ts[1] \\f[NP_1] \\| \\^ \\n ...
  {1} {2} ...            segnaposto di _INTL
  <i> <c=green> <icon=fieldUp> ...   tag di formattazione

maschera()  sostituisce ogni codice con un segnaposto opaco (§0§, §1§, ...)
ripristina() rimette i codici originali al loro posto.

I segnaposto usano il carattere § che non compare mai nel testo inglese e che
i traduttori automatici lasciano intatto.
"""
import re

SEGNAPOSTO = "\u00a7"   # §

# Ordine importante: le alternative piu' lunghe vanno per prime.
CODICI = re.compile(
    r"""(
        \\wskin\{[^}]*\}                      # \wskin{a|b}
      | \\wskin\[[^\]]*\]                     # \wskin[a|b]
      | \\sign\[[^\]]*\]                      # \sign[...]
      | \\[A-Za-z]{1,6}\[[^\]]*\]             # \v[12] \c[6] \ts[1] \f[NP_1] \l[3] \n[2] \vu[9]
      | \\\[[0-9A-Fa-f]{8}\]                  # \[AARRGGBB]
      | \\[Pp][Nn](?:Upper|Lower)?            # \PN \PNUpper \PNLower \pn
                                              # codici a parola: i piu' lunghi prima
      | \\(?:egsc|gsc|pog|pg|pm|sh|SH|ac|br|wm|sj|cl|CN|
            b|r|n|l|w|g|G|W|N|C|\d)
      | \\[^A-Za-z0-9\s]                      # \| \^ \. \! \# \\ \[
      | \{\d+\}                               # {1} {2} ...
      | </?[A-Za-z][A-Za-z0-9]{0,9}(?:=[^<>\n]{0,60})?>   # <i> </c> <c=red> <icon=x,tts="y">
      | %[sdif]                               # %i
      | \n                                    # a capo reale: va conservato
    )""",
    re.VERBOSE,
)


def maschera(testo):
    """Ritorna (testo_mascherato, lista_codici)."""
    codici = []

    def _sost(m):
        codici.append(m.group(0))
        return "%s%d%s" % (SEGNAPOSTO, len(codici) - 1, SEGNAPOSTO)

    return CODICI.sub(_sost, testo), codici


def ripristina(testo, codici):
    """Rimette i codici; tollera spazi introdotti dal traduttore nei segnaposto."""
    def _sost(m):
        i = int(m.group(1))
        return codici[i] if 0 <= i < len(codici) else m.group(0)

    return re.sub(r"%s\s*(\d+)\s*%s" % (SEGNAPOSTO, SEGNAPOSTO), _sost, testo)


def segnaposto_presenti(testo):
    """Indici dei segnaposto trovati nel testo, in ordine di apparizione."""
    return [int(x) for x in re.findall(
        r"%s\s*(\d+)\s*%s" % (SEGNAPOSTO, SEGNAPOSTO), testo)]


def verifica(originale, tradotto):
    """
    Controlla che la traduzione conservi tutti i codici dell'originale.
    Ritorna None se va bene, altrimenti una stringa che descrive il problema.
    """
    a = CODICI.findall(originale)
    b = CODICI.findall(tradotto)
    if sorted(a) != sorted(b):
        mancanti = [c for c in a if a.count(c) > b.count(c)]
        aggiunti = [c for c in b if b.count(c) > a.count(c)]
        parti = []
        if mancanti:
            parti.append("mancano %s" % sorted(set(mancanti)))
        if aggiunti:
            parti.append("in piu' %s" % sorted(set(aggiunti)))
        return "; ".join(parti)
    if SEGNAPOSTO in tradotto:
        return "segnaposto non ripristinato"
    return None


# ---------------------------------------------------------------------------
# Verifica di copertura sul corpus
# ---------------------------------------------------------------------------
def _audit():
    import os
    import sys
    from collections import Counter

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import rmarshal
    from rmarshal import UserDef

    import percorsi
    game = percorsi.trova_gioco()
    msgs = rmarshal.load_file(os.path.join(game, "Data", "messages.dat"))

    def tutte():
        for k, v in msgs.items():
            if k == 0:
                continue
            if isinstance(v, UserDef):
                ks, vs = rmarshal.load(v.data)
                for s in vs:
                    if isinstance(s, str) and s:
                        yield s
        for m in msgs.get(0) or []:
            if isinstance(m, UserDef):
                ks, vs = rmarshal.load(m.data)
                for s in vs:
                    if isinstance(s, str) and s:
                        yield s

    scoperti = Counter()
    mascherate = 0
    totali = 0
    esempi = {}

    # Qualunque residuo di backslash o di tag dopo la mascheratura e' sospetto.
    residuo = re.compile(r"\\[^\s]{0,8}|<[^<>\n]{0,40}>|\{\d+\}")

    for s in tutte():
        totali += 1
        m, codici = maschera(s)
        if codici:
            mascherate += 1
        for r in residuo.findall(m):
            scoperti[r] += 1
            esempi.setdefault(r, s)

    print("stringhe: %d   con codici mascherati: %d" % (totali, mascherate))
    print("\nsequenze NON coperte dalla maschera: %d forme" % len(scoperti))
    for tok, n in scoperti.most_common(30):
        ctx = esempi[tok]
        i = ctx.find(tok)
        print("  %-16s x%-6d ... %s" % (repr(tok), n, repr(ctx[max(0, i - 25):i + 35])))


if __name__ == "__main__":
    _audit()
