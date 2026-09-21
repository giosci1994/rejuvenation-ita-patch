# -*- coding: utf-8 -*-
"""
Risoluzione dei percorsi: dove sta il gioco, dove stanno i file di lavoro.

Gli strumenti vivono nel repository, il gioco sta altrove. La cartella di
Rejuvenation viene cercata, nell'ordine:

  1. l'opzione --gioco passata sulla riga di comando
  2. la variabile d'ambiente REJUVENATION_DIR
  3. il file gioco.txt nella radice del repository
  4. le posizioni tipiche su Windows, macOS e Linux

Una volta trovata viene ricordata in gioco.txt, cosi' la si indica una volta sola.
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, ".."))

LAVORO = os.path.join(REPO, "lavoro")          # temporanei, esclusi da git
DATI = os.path.join(REPO, "dati")              # la traduzione, versionata
PATCH = os.path.join(REPO, "patch")            # il pacchetto da installare

TRADUZIONI = os.path.join(DATI, "traduzioni.jsonl")
DA_TRADURRE = os.path.join(LAVORO, "da_tradurre.jsonl")
DA_RIVEDERE = os.path.join(LAVORO, "da_rivedere.jsonl")
LOTTI = os.path.join(LAVORO, "lotti_in_corso.jsonl")

RICORDO = os.path.join(REPO, "gioco.txt")

CANDIDATE = [
    r"C:\Users\%s\Desktop\Rejuvenation" % os.environ.get("USERNAME", ""),
    r"C:\Program Files (x86)\Pokemon Rejuvenation",
    r"C:\Games\Rejuvenation",
    os.path.expanduser("~/Desktop/Rejuvenation"),
    os.path.expanduser("~/Games/Rejuvenation"),
    os.path.expanduser("~/Rejuvenation"),
]


def e_cartella_gioco(percorso):
    """Riconosce la cartella dal file che contiene tutto il testo."""
    return bool(percorso) and os.path.isfile(
        os.path.join(percorso, "Data", "messages.dat"))


def aggiungi_argomento(parser):
    parser.add_argument(
        "--gioco", default=None,
        help="cartella di Pokemon Rejuvenation (quella con Data e Graphics)")


def ricorda(percorso):
    try:
        with open(RICORDO, "w", encoding="utf-8") as f:
            f.write(percorso + "\n")
    except Exception:
        pass


def trova_gioco(indicato=None, obbligatorio=True):
    prove = []

    if indicato:
        prove.append(("l'opzione --gioco", indicato))
    if os.environ.get("REJUVENATION_DIR"):
        prove.append(("REJUVENATION_DIR", os.environ["REJUVENATION_DIR"]))
    if os.path.isfile(RICORDO):
        try:
            with open(RICORDO, encoding="utf-8") as f:
                salvato = f.read().strip()
            if salvato:
                prove.append(("gioco.txt", salvato))
        except Exception:
            pass
    for c in CANDIDATE:
        prove.append(("ricerca automatica", c))

    for origine, percorso in prove:
        percorso = os.path.expanduser(percorso.strip().strip('"'))
        if e_cartella_gioco(percorso):
            percorso = os.path.abspath(percorso)
            if origine != "gioco.txt":
                ricorda(percorso)
            return percorso

    if not obbligatorio:
        return None

    print("Non trovo la cartella di Pokemon Rejuvenation.")
    print()
    print("Indicala una volta sola, in uno di questi modi:")
    print('  python %s --gioco "C:\\percorso\\del\\gioco"' % os.path.basename(sys.argv[0]))
    print('  oppure scrivi il percorso dentro %s' % RICORDO)
    print()
    print("E' la cartella che contiene Data, Graphics e Rejuvenation.exe.")
    if indicato:
        print()
        print('Il percorso indicato non contiene Data\\messages.dat: %s' % indicato)
    sys.exit(1)


def assicura_lavoro():
    os.makedirs(LAVORO, exist_ok=True)
    return LAVORO
