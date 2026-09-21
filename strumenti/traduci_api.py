# -*- coding: utf-8 -*-
"""
Traduce il testo del gioco con l'API di Claude usando la Batch API (costo -50%).

Uso tipico:
    set ANTHROPIC_API_KEY=sk-ant-...
    python traduci_api.py --prova              # 3 unita' di assaggio, costo irrisorio
    python traduci_api.py --stima              # stima del costo, nessuna chiamata
    python traduci_api.py --prio 2             # prima l'interfaccia (poche migliaia di stringhe)
    python traduci_api.py                      # tutto il resto

Lo script e' ripartibile: quello che e' gia' in lavoro/tradotte.jsonl viene saltato,
quindi puoi interromperlo e rilanciarlo quando vuoi.
"""
import argparse
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import protezione

import percorsi

QUI = os.path.dirname(os.path.abspath(__file__))
LAVORO = percorsi.LAVORO
DA_TRADURRE = percorsi.DA_TRADURRE
TRADOTTE = percorsi.TRADUZIONI      # la traduzione versionata nel repository
SCARTI = percorsi.DA_RIVEDERE

# Prezzi Batch API (meta' del listino), dollari per milione di token.
PREZZI = {
    "claude-opus-5":   (2.50, 12.50),
    "claude-sonnet-5": (1.00, 5.00),
    "claude-haiku-4-5": (0.50, 2.50),
}


class Contatore:
    """
    Somma il consumo REALE dichiarato dall'API, invece di indovinarlo dai
    caratteri. La scrittura in cache costa 1.25x, la rilettura 0.1x.
    """

    def __init__(self, modello, batch=True):
        pin, pout = PREZZI.get(modello, PREZZI["claude-sonnet-5"])
        if not batch:
            pin, pout = pin * 2, pout * 2
        self.pin, self.pout = pin, pout
        self.ingresso = self.uscita = self.scritte = self.lette = 0
        self.stringhe = 0

    def aggiungi(self, usage, stringhe=0):
        if usage is None:
            return
        self.ingresso += getattr(usage, "input_tokens", 0) or 0
        self.uscita += getattr(usage, "output_tokens", 0) or 0
        self.scritte += getattr(usage, "cache_creation_input_tokens", 0) or 0
        self.lette += getattr(usage, "cache_read_input_tokens", 0) or 0
        self.stringhe += stringhe

    @property
    def costo(self):
        return (self.ingresso * self.pin
                + self.scritte * self.pin * 1.25
                + self.lette * self.pin * 0.10
                + self.uscita * self.pout) / 1e6

    def riepilogo(self):
        r = ["  token in %d, out %d" % (self.ingresso, self.uscita)]
        if self.scritte or self.lette:
            r.append("  cache: %d scritti, %d riletti" % (self.scritte, self.lette))
        r.append("  SPESA REALE: %.4f $" % self.costo)
        if self.stringhe:
            mille = self.costo / self.stringhe * 1000
            r.append("  ossia %.4f $ ogni mille stringhe" % mille)
        return "\n".join(r)

RIGA = re.compile(r"^\s*\[\[(\d+)\]\][ \t]?(.*)$")

# Forme con apostrofo, per i pochi font decorativi privi di glifi accentati.
ACCENTI = {
    "à": "a'", "è": "e'", "é": "e'", "ì": "i'", "ò": "o'", "ù": "u'",
    "À": "A'", "È": "E'", "É": "E'", "Ì": "I'", "Ò": "O'", "Ù": "U'",
}

_GLOSSARIO = None


def glossario():
    global _GLOSSARIO
    if _GLOSSARIO is None:
        with open(os.path.join(QUI, "glossario.json"), encoding="utf-8") as f:
            _GLOSSARIO = json.load(f)
    return _GLOSSARIO


def senza_accenti(testo):
    testo = testo.replace("Pokémon", "Pokemon").replace("Pokédex", "Pokedex")
    for acc, piano in ACCENTI.items():
        testo = testo.replace(acc, piano)
    return testo


def adatta_font(en, it):
    """
    Font come Cute Notes o Garufan non hanno i glifi accentati: in quelle poche
    stringhe le lettere accentate diventerebbero quadratini, quindi si ripiega
    sulle forme con apostrofo.
    """
    for nome in glossario().get("font_senza_accenti", []):
        if "<fn=%s>" % nome in en:
            return senza_accenti(it)
    return it


def costruisci_sistema():
    g = glossario()

    def coppie(d, n=None):
        voci = list(d.items())[:n] if n else list(d.items())
        return ", ".join("%s=%s" % (k, v) for k, v in voci)

    return """Sei un traduttore professionista di videogiochi. Traduci dall'inglese \
all'italiano il testo di Pokémon Rejuvenation, un gioco di ruolo fan-made dai toni \
maturi e dalla trama complessa.

REGOLE ASSOLUTE
1. I segnaposto come §0§ §1§ §2§ sono codici di controllo del gioco. Riportali \
IDENTICI, nello stesso numero, senza spazi interni. Puoi spostarli se la sintassi \
italiana lo richiede, ma non inventarne, non ometterne, non rinumerarli.
2. Traduci OGNI riga. Rispondi solo con le righe tradotte, una per riga, nel formato \
esatto [[numero]] testo, con gli stessi numeri che ricevi e nello stesso ordine.
3. Nessun commento, nessuna spiegazione, nessuna riga in più.
4. Se una riga è già italiana, un nome proprio o un simbolo, riportala invariata.
5. Scrivi in italiano tipografico corretto, con le lettere accentate vere: è, à, ì, \
ò, ù, é, È. Non usare MAI le forme con apostrofo tipo "e'", "gia'", "puo'", "Eta". \
Il gioco disegna correttamente tutte le lettere accentate.

STILE
Dai SEMPRE del tu, anche in cartelli, avvisi, annunci pubblici e insegne: mai il voi \
né il lei. Registro colloquiale e naturale come nei giochi Pokémon ufficiali \
italiani. Mantieni il tono del personaggio: sarcasmo, slang e volgarità vanno resi, \
non addolciti. Conserva la punteggiatura espressiva (!!!, ..., MAIUSCOLE) e gli spazi \
iniziali o finali della riga.
"I see" detto per capire vale "Capisco", non "Vedo". I nomi di scuole, aziende e \
istituzioni restano in inglese come i nomi di luogo.

TERMINOLOGIA UFFICIALE ITALIANA
I nomi dei Pokémon restano invariati. Restano invariati anche i nomi propri di \
persone e luoghi.
Tipi: %s
Nature: %s
Statistiche: %s
Interfaccia: %s
Stati: %s""" % (
        coppie(g["tipi"]),
        coppie(g["nature"]),
        coppie(g["statistiche"]),
        coppie(g["interfaccia"]),
        coppie(g["stati"]),
    )


def carica_lavoro(prio, limite):
    fatte = set()
    if os.path.exists(TRADOTTE):
        with open(TRADOTTE, encoding="utf-8") as f:
            for line in f:
                try:
                    fatte.add(json.loads(line)["id"])
                except Exception:
                    pass

    voci = []
    with open(DA_TRADURRE, encoding="utf-8") as f:
        for line in f:
            o = json.loads(line)
            if o["id"] in fatte:
                continue
            # basta che la stringa compaia in UNA sezione della priorita'
            # richiesta: "Fire" sta nei tipi e anche nei dialoghi, e serve
            # tradurla gia' col lotto dell'interfaccia.
            if prio and not (set(o.get("prios") or [o["prio"]]) & prio):
                continue
            voci.append(o)
            if limite and len(voci) >= limite:
                break
    return voci, len(fatte)


TETTO_CARATTERI = 6000      # per non avvicinarsi al limite di token in uscita


def fai_unita(voci, per_richiesta):
    """
    Raggruppa le voci in unita' di richiesta, mascherando i codici.

    Il gruppo si chiude al raggiungimento del numero di stringhe OPPURE del
    tetto di caratteri: ordinando per lunghezza decrescente, contare solo le
    stringhe produrrebbe richieste enormi e risposte troncate.
    """
    unita = []
    righe, meta, car = [], [], 0

    def chiudi():
        if meta:
            unita.append({"testo": "\n".join(righe), "meta": list(meta)})
        righe.clear()
        meta.clear()

    for o in voci:
        mascherato, codici = protezione.maschera(o["en"])
        if meta and (len(meta) >= per_richiesta or car + len(mascherato) > TETTO_CARATTERI):
            chiudi()
            car = 0
        righe.append("[[%d]] %s" % (len(meta) + 1, mascherato))
        meta.append({"id": o["id"], "en": o["en"], "codici": codici})
        car += len(mascherato)
    chiudi()
    return unita


USA_CACHE = False   # misurato: in batch le scritture superano di molto le riletture


def parametri_modello(modello, sistema, testo):
    blocco = {"type": "text", "text": sistema}
    if USA_CACHE:
        blocco["cache_control"] = {"type": "ephemeral"}
    p = {
        "model": modello,
        "max_tokens": 16000,
        "system": [blocco],
        "messages": [{"role": "user", "content": testo}],
    }
    if modello == "claude-haiku-4-5":
        pass                                   # niente thinking ne' effort
    elif modello == "claude-opus-5":
        p["output_config"] = {"effort": "low"}  # su Opus 5 il thinking resta attivo
    else:
        p["thinking"] = {"type": "disabled"}
        p["output_config"] = {"effort": "low"}
    return p


def analizza_risposta(testo, meta):
    """Estrae le traduzioni; ritorna (buone, scartate)."""
    trovate = {}
    for riga in testo.splitlines():
        m = RIGA.match(riga)
        if m:
            trovate[int(m.group(1))] = m.group(2)

    buone, scarti = [], []
    for n, info in enumerate(meta, start=1):
        grezza = trovate.get(n)
        if grezza is None:
            scarti.append({"id": info["id"], "motivo": "riga mancante"})
            continue
        it = protezione.ripristina(grezza, info["codici"])
        problema = protezione.verifica(info["en"], it)
        if problema:
            scarti.append({"id": info["id"], "motivo": problema, "resa": it})
            continue
        buone.append({"id": info["id"], "it": adatta_font(info["en"], it)})
    return buone, scarti


LOTTI = percorsi.LOTTI


def registra_lotto(lotto_id, mappa):
    """
    Annota il lotto appena inviato. Se il programma viene interrotto, il lavoro
    prosegue sul server e viene comunque fatturato: questo file permette di
    riprendersi i risultati con --recupera invece di buttarli.
    """
    percorsi.assicura_lavoro()
    with open(LOTTI, "a", encoding="utf-8") as f:
        f.write(json.dumps({"lotto": lotto_id, "mappa": mappa}) + "\n")


def leggi_lotti():
    if not os.path.exists(LOTTI):
        return []
    voci = []
    with open(LOTTI, encoding="utf-8") as f:
        for line in f:
            try:
                voci.append(json.loads(line))
            except Exception:
                pass
    return voci


def chiudi_lotto(lotto_id):
    """Toglie dall'elenco un lotto i cui risultati sono stati incassati."""
    voci = [v for v in leggi_lotti() if v["lotto"] != lotto_id]
    with open(LOTTI, "w", encoding="utf-8") as f:
        for v in voci:
            f.write(json.dumps(v) + "\n")


def salva(buone, scarti):
    percorsi.assicura_lavoro()
    os.makedirs(percorsi.DATI, exist_ok=True)
    if buone:
        with open(TRADOTTE, "a", encoding="utf-8") as f:
            for b in buone:
                f.write(json.dumps(b, ensure_ascii=False) + "\n")
    if scarti:
        with open(SCARTI, "a", encoding="utf-8") as f:
            for s in scarti:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")


def stima(unita, modello, sistema, batch=True):
    """Stima approssimativa: ~4 caratteri per token."""
    car_in = sum(len(u["testo"]) for u in unita)
    tok_sist = len(sistema) / 4.0 * len(unita)
    tok_in = car_in / 4.0 + tok_sist
    tok_out = car_in * 1.15 / 4.0 + sum(len(u["meta"]) for u in unita) * 4
    pin, pout = PREZZI.get(modello, PREZZI["claude-sonnet-5"])
    if not batch:
        pin, pout = pin * 2, pout * 2      # l'assaggio non passa dalla Batch API
    # Le stime a caratteri sottostimano: il costo fisso di ogni richiesta pesa
    # piu' di quanto sembri, soprattutto sulle stringhe corte. Il fattore e'
    # calibrato sul consumo reale misurato. La cifra che conta resta comunque
    # quella che il programma misura durante l'esecuzione.
    costo = (tok_in / 1e6 * pin + tok_out / 1e6 * pout) * 1.5
    print("  richieste           : %d" % len(unita))
    print("  stringhe            : %d" % sum(len(u["meta"]) for u in unita))
    print("  COSTO STIMATO       : ~%.2f $ con %s (%s)"
          % (costo, modello, "Batch API, -50%" if batch else "prezzo pieno"))
    print("  stima prudenziale e approssimativa; la spesa vera viene misurata")
    print("  e stampata mentre il lavoro procede")
    return costo


def esegui_batch(client, unita, modello, sistema, per_batch, tetto=0.0):
    totale_ok = totale_ko = 0
    cont = Contatore(modello, batch=True)
    for inizio in range(0, len(unita), per_batch):
        if tetto and cont.costo >= tetto:
            print("\nRaggiunto il tetto di spesa di %.2f $: mi fermo qui." % tetto)
            print("Il lavoro fatto e' salvato, rilancia quando vuoi proseguire.")
            break
        gruppo = unita[inizio:inizio + per_batch]
        richieste = [{
            "custom_id": "u%d" % (inizio + i),
            "params": parametri_modello(modello, sistema, u["testo"]),
        } for i, u in enumerate(gruppo)]

        lotto = client.messages.batches.create(requests=richieste)
        registra_lotto(lotto.id, {
            "u%d" % (inizio + i): [m["id"] for m in u["meta"]]
            for i, u in enumerate(gruppo)
        })
        print("\nlotto %s inviato: %d richieste (%d-%d di %d)"
              % (lotto.id, len(richieste), inizio + 1,
                 inizio + len(gruppo), len(unita)))

        attesa = 20
        while True:
            time.sleep(attesa)
            stato = client.messages.batches.retrieve(lotto.id)
            c = stato.request_counts
            print("  %s  ok=%d errore=%d in corso=%d"
                  % (stato.processing_status, c.succeeded, c.errored, c.processing),
                  flush=True)
            if stato.processing_status == "ended":
                break
            attesa = min(attesa * 1.5, 120)

        mappa = {"u%d" % (inizio + i): u for i, u in enumerate(gruppo)}

        for res in client.messages.batches.results(lotto.id):
            u = mappa.get(res.custom_id)
            if u is None:
                continue
            if res.result.type != "succeeded":
                salva([], [{"id": m["id"], "motivo": "richiesta %s" % res.result.type}
                           for m in u["meta"]])
                totale_ko += len(u["meta"])
                continue
            testo = "".join(b.text for b in res.result.message.content
                            if b.type == "text")
            cont.aggiungi(getattr(res.result.message, "usage", None), len(u["meta"]))
            buone, scarti = analizza_risposta(testo, u["meta"])
            salva(buone, scarti)
            totale_ok += len(buone)
            totale_ko += len(scarti)

        chiudi_lotto(lotto.id)          # risultati incassati, non serve piu'
        print("  cumulato: %d tradotte, %d da rivedere" % (totale_ok, totale_ko))
        print(cont.riepilogo())
        if cont.stringhe:
            resto = sum(len(u["meta"]) for u in unita) - cont.stringhe
            if resto > 0:
                print("  proiezione per le %d stringhe rimaste: %.2f $"
                      % (resto, cont.costo / cont.stringhe * resto))
    return totale_ok, totale_ko, cont


_anthropic = None


def fai_client():
    """Crea il client, spiegando in italiano cosa manca se qualcosa manca."""
    global _anthropic
    try:
        import anthropic
    except ImportError:
        print("\nmanca il pacchetto anthropic:  pip install anthropic")
        return None
    _anthropic = anthropic

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\nmanca ANTHROPIC_API_KEY nell'ambiente.")
        return None

    # Una chiave creata a livello di organizzazione non e' legata ad alcun
    # workspace, e in quel caso l'API pretende l'header anthropic-workspace-id.
    intestazioni = {}
    ws = os.environ.get("ANTHROPIC_WORKSPACE_ID")
    if ws:
        intestazioni["anthropic-workspace-id"] = ws
    return anthropic.Anthropic(default_headers=intestazioni or None)


def esegui_recupero(client, modello):
    """
    Incassa i risultati dei lotti inviati e mai raccolti, per esempio dopo un
    Ctrl+C o un crollo della rete. I risultati restano disponibili sul server
    per settimane, e sono gia' stati pagati: buttarli sarebbe uno spreco.
    """
    pendenti = leggi_lotti()
    if not pendenti:
        print("Nessun lotto in sospeso da recuperare.")
        return

    testi = {}
    with open(DA_TRADURRE, encoding="utf-8") as f:
        for line in f:
            o = json.loads(line)
            testi[o["id"]] = o["en"]

    cont = Contatore(modello, batch=True)
    print("lotti in sospeso: %d\n" % len(pendenti))

    for voce in pendenti:
        lotto_id, mappa = voce["lotto"], voce["mappa"]
        stato = client.messages.batches.retrieve(lotto_id)
        print("%s -> %s" % (lotto_id, stato.processing_status))
        if stato.processing_status != "ended":
            print("  non ancora pronto, riprova piu' tardi")
            continue

        ok = ko = 0
        for res in client.messages.batches.results(lotto_id):
            ids = mappa.get(res.custom_id)
            if not ids or res.result.type != "succeeded":
                continue
            meta = []
            for i in ids:
                en = testi.get(i)
                if en is None:
                    continue
                meta.append({"id": i, "en": en,
                             "codici": protezione.maschera(en)[1]})
            testo = "".join(b.text for b in res.result.message.content
                            if b.type == "text")
            cont.aggiungi(getattr(res.result.message, "usage", None), len(meta))
            buone, scarti = analizza_risposta(testo, meta)
            salva(buone, scarti)
            ok += len(buone)
            ko += len(scarti)

        chiudi_lotto(lotto_id)
        print("  recuperate %d traduzioni, %d da rivedere" % (ok, ko))

    print("\n" + cont.riepilogo())


def esegui_prova(client, unita, modello, sistema):
    cont = Contatore(modello, batch=False)
    for u in unita:
        r = client.messages.create(**parametri_modello(modello, sistema, u["testo"]))
        testo = "".join(b.text for b in r.content if b.type == "text")
        cont.aggiungi(getattr(r, "usage", None), len(u["meta"]))
        buone, scarti = analizza_risposta(testo, u["meta"])
        for b in buone[:12]:
            en = next(m["en"] for m in u["meta"] if m["id"] == b["id"])
            print("  EN: %s\n  IT: %s\n" % (en[:110], b["it"][:110]))
        print("  -> %d valide, %d da rivedere in questa unita'\n" % (len(buone), len(scarti)))
        salva(buone, scarti)
    print(cont.riepilogo())
    return cont


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modello", default="claude-sonnet-5",
                    help="claude-sonnet-5 (default), claude-opus-5, claude-haiku-4-5")
    ap.add_argument("--prio", default="", help="filtra per priorita', es. 1 oppure 2,3")
    ap.add_argument("--per-richiesta", type=int, default=150,
                    help="stringhe per richiesta: piu' alto = meno costo fisso")
    # Lotti piccoli: il tetto di spesa puo' scattare solo fra un lotto e l'altro,
    # quindi mandarne uno solo gigante lo renderebbe inutile.
    ap.add_argument("--per-lotto", type=int, default=250)
    ap.add_argument("--tetto", type=float, default=0.0,
                    help="spesa massima in dollari: oltre quella soglia si ferma")
    ap.add_argument("--cache", action="store_true",
                    help="riattiva la cache di prompt (misurata in perdita in batch)")
    ap.add_argument("--recupera", action="store_true",
                    help="incassa i risultati di lotti inviati e mai raccolti")
    ap.add_argument("--limite", type=int, default=0, help="massimo di stringhe da trattare")
    ap.add_argument("--stima", action="store_true", help="solo stima del costo")
    ap.add_argument("--prova", action="store_true", help="3 unita' di assaggio, senza batch")
    args = ap.parse_args()

    global USA_CACHE
    USA_CACHE = args.cache

    if args.recupera:
        client = fai_client()
        if client:
            esegui_recupero(client, args.modello)
        return

    prio = {int(x) for x in args.prio.split(",") if x.strip()} if args.prio else None
    limite = args.limite or (3 * args.per_richiesta if args.prova else 0)

    voci, gia_fatte = carica_lavoro(prio, limite)
    print("gia' tradotte: %d   da fare ora: %d" % (gia_fatte, len(voci)))
    if not voci:
        print("niente da tradurre.")
        return

    sistema = costruisci_sistema()
    unita = fai_unita(voci, args.per_richiesta)

    print("\nstima:")
    stima(unita, args.modello, sistema, batch=not args.prova)

    if args.stima:
        return

    client = fai_client()
    if client is None:
        return

    try:
        if args.prova:
            print("\n--- assaggio ---\n")
            esegui_prova(client, unita, args.modello, sistema)
            return

        print("\nInvio alla Batch API. Puoi interrompere e rilanciare quando vuoi.")
        ok, ko, cont = esegui_batch(client, unita, args.modello, sistema,
                                    args.per_lotto, args.tetto)
        print("\nfatto: %d tradotte, %d da rivedere (in %s)" % (ok, ko, SCARTI))
        print(cont.riepilogo())
    except _anthropic.APIStatusError as e:
        spiega_errore(e)


def spiega_errore(e):
    """Traduce in italiano gli inciampi piu' comuni dell'API."""
    msg = str(getattr(e, "message", "")) or str(e)
    print("\nL'API ha rifiutato la richiesta:\n  %s\n" % msg)
    if "workspace" in msg.lower():
        print("La chiave non e' legata a un workspace. Due modi per risolvere:")
        print("  a) crea una chiave nuova scegliendo un workspace, su")
        print("     platform.claude.com/settings/keys")
        print("  b) oppure imposta l'ID del workspace nell'ambiente:")
        print('     $env:ANTHROPIC_WORKSPACE_ID = "wrkspc_..."')
    elif "credit" in msg.lower() or "balance" in msg.lower():
        print("Credito esaurito: ricaricalo su platform.claude.com/settings/billing")
    elif "authentication" in msg.lower() or "api key" in msg.lower():
        print("Chiave non valida. Controlla ANTHROPIC_API_KEY, oppure creane una")
        print("nuova su platform.claude.com/settings/keys")


if __name__ == "__main__":
    main()
