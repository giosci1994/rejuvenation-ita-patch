# -*- coding: utf-8 -*-
"""
Controlla che nel repository non finisca nulla che non deve starci, e che la
traduzione sia integra.

Non serve il gioco: lavora solo sui file versionati, quindi gira anche su
GitHub Actions. Esce con codice 1 se qualcosa non va.

    python verifica_repo.py
"""
import json
import os
import re
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, ".."))

# Roba che appartiene al gioco e non va mai pubblicata.
VIETATI = [
    (re.compile(r"^lavoro/"), "materiale di lavoro: contiene il copione inglese del gioco"),
    (re.compile(r"(^|/)messages\.dat$"), "file di testo del gioco"),
    (re.compile(r"(^|/)da_tradurre\.jsonl$"), "copione inglese integrale"),
    (re.compile(r"^patch/italiano\.dat$"), "artefatto compilato: va nelle Release, non in git"),
    (re.compile(r"\.rxdata$"), "dati di RPG Maker appartenenti al gioco"),
    (re.compile(r"\.(exe|dll)$"), "eseguibile o libreria del gioco"),
    (re.compile(r"^(Data|Graphics|Audio|Fonts|Scripts)/"), "cartella del gioco"),
    (re.compile(r"^gioco\.txt$"), "percorso locale, non ha senso condividerlo"),
]

CAMPI_AMMESSI = {"id", "it", "sez"}
IDENT = re.compile(r"^[0-9a-f]{16}$")
GG = re.compile(r"\\gg\[([^\]\|]*)\|([^\]\|]*)(?:\|([^\]]*))?\]")
GG_SOSPETTO = re.compile(r"\\gg(?!\[)|\\gg\[[^\]]*$")

errori = []
avvisi = []


def file_versionati():
    out = subprocess.run(["git", "ls-files"], cwd=REPO,
                         capture_output=True, text=True, check=True)
    return [r.strip().replace("\\", "/") for r in out.stdout.splitlines() if r.strip()]


def controlla_contenuto(percorsi):
    print("1. Nessun materiale del gioco fra i file versionati")
    trovati = 0
    for p in percorsi:
        for rx, motivo in VIETATI:
            if rx.search(p):
                errori.append("%s non deve stare nel repository (%s)" % (p, motivo))
                trovati += 1
    print("   %d file controllati, %d problemi\n" % (len(percorsi), trovati))


def controlla_traduzione():
    print("2. Integrita' di dati/traduzioni.jsonl")
    p = os.path.join(REPO, "dati", "traduzioni.jsonl")
    if not os.path.exists(p):
        errori.append("manca dati/traduzioni.jsonl")
        return

    righe = accordi = 0
    with open(p, encoding="utf-8") as f:
        for n, linea in enumerate(f, 1):
            linea = linea.strip()
            if not linea:
                continue
            righe += 1
            try:
                o = json.loads(linea)
            except Exception as e:
                errori.append("riga %d non e' JSON valido: %s" % (n, e))
                continue

            estranei = set(o) - CAMPI_AMMESSI
            if estranei:
                # "en" significherebbe testo inglese del gioco pubblicato
                errori.append("riga %d ha campi non ammessi: %s" % (n, sorted(estranei)))
            if not IDENT.match(str(o.get("id", ""))):
                errori.append("riga %d ha un identificativo malformato" % n)
            testo = o.get("it")
            if not isinstance(testo, str):
                errori.append("riga %d non ha testo italiano" % n)
                continue
            if GG_SOSPETTO.search(testo):
                errori.append("riga %d ha un codice di genere malformato" % n)
            if "\\gg[" in testo:
                accordi += 1

    print("   %d righe, %d con accordo di genere, %d problemi\n"
          % (righe, accordi, len([e for e in errori if "riga" in e])))


def controlla_strumenti():
    print("3. Gli strumenti si compilano")
    import ast
    rotti = 0
    for nome in sorted(os.listdir(QUI)):
        if not nome.endswith(".py"):
            continue
        try:
            with open(os.path.join(QUI, nome), encoding="utf-8") as f:
                ast.parse(f.read())
        except SyntaxError as e:
            errori.append("%s non compila: riga %s" % (nome, e.lineno))
            rotti += 1
    print("   %d script controllati, %d rotti\n" % (
        len([n for n in os.listdir(QUI) if n.endswith('.py')]), rotti))


def controlla_patch():
    print("4. Gli script di attivazione della lingua sono al loro posto")
    attesi = ["patch/Init/intl.rb", "patch/Mods/intl.rb"]
    for a in attesi:
        p = os.path.join(REPO, a.replace("/", os.sep))
        if not os.path.exists(p):
            errori.append("manca %s" % a)
            continue
        with open(p, encoding="utf-8") as f:
            testo = f.read()
        if "LANGUAGES" not in testo:
            errori.append("%s non definisce LANGUAGES" % a)
    # il file in Mods deve contenere anche l'accordo di genere
    p = os.path.join(REPO, "patch", "Mods", "intl.rb")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            if "espandiGenere" not in f.read():
                avvisi.append("patch/Mods/intl.rb non contiene l'accordo di genere: "
                              "rigeneralo con costruisci.py")
    print("   %d file controllati\n" % len(attesi))


def main():
    print("Verifica del repository\n" + "=" * 46 + "\n")
    percorsi = file_versionati()
    controlla_contenuto(percorsi)
    controlla_traduzione()
    controlla_strumenti()
    controlla_patch()

    print("=" * 46)
    for a in avvisi:
        print("AVVISO: %s" % a)
    if errori:
        print("\n%d PROBLEMI:\n" % len(errori))
        for e in errori[:30]:
            print("  - %s" % e)
        if len(errori) > 30:
            print("  ... e altri %d" % (len(errori) - 30))
        sys.exit(1)
    print("\nTutto a posto.")


if __name__ == "__main__":
    main()
