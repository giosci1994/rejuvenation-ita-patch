# -*- coding: utf-8 -*-
"""
Genera docs/social-preview.png, l'immagine che GitHub mostra quando il link
viene condiviso su Discord, Reddit, WhatsApp e simili.

Formato 1280x640, quello raccomandato da GitHub. Le catture di gioco vengono
prese da docs/screenshots e inserite alla risoluzione nativa, senza
ricampionamenti che rovinerebbero la grafica a pixel.

    python anteprima_social.py
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, ".."))
CATTURE = os.path.join(REPO, "docs", "screenshots")
USCITA = os.path.join(REPO, "docs", "social-preview.png")

L, A = 1280, 640

SFONDO = (13, 17, 23)          # lo stesso fondo scuro di GitHub
VERDE = (0, 181, 133)          # il verde dei badge degli altri repository
VERDE_CHIARO = (52, 211, 153)
BIANCO = (237, 242, 247)
GRIGIO = (125, 138, 154)

FONT_DIR = r"C:\Windows\Fonts"


def font(nome, dim):
    for f in (nome, "segoeui.ttf", "arial.ttf"):
        p = os.path.join(FONT_DIR, f)
        if os.path.exists(p):
            return ImageFont.truetype(p, dim)
    return ImageFont.load_default()


def grassetto(dim):
    return font("seguisb.ttf", dim)


def normale(dim):
    return font("segoeui.ttf", dim)


def angoli_arrotondati(im, raggio):
    """Ritaglia l'immagine con angoli arrotondati."""
    maschera = Image.new("L", im.size, 0)
    ImageDraw.Draw(maschera).rounded_rectangle(
        [0, 0, im.size[0] - 1, im.size[1] - 1], radius=raggio, fill=255)
    fuori = im.convert("RGBA")
    fuori.putalpha(maschera)
    return fuori


def incolla_cattura(tela, percorso, xy, scala=1.0, raggio=10):
    """Posa una cattura con bordo e ombra, senza sfocarne i pixel."""
    im = Image.open(percorso).convert("RGB")
    if scala != 1.0:
        nuove = (int(im.width * scala), int(im.height * scala))
        # NEAREST sopra 1x tiene i pixel netti, LANCZOS sotto 1x evita l'aliasing
        filtro = Image.NEAREST if scala > 1 else Image.LANCZOS
        im = im.resize(nuove, filtro)

    x, y = xy
    # ombra
    ombra = Image.new("RGBA", tela.size, (0, 0, 0, 0))
    ImageDraw.Draw(ombra).rounded_rectangle(
        [x + 6, y + 10, x + im.width + 6, y + im.height + 10],
        radius=raggio, fill=(0, 0, 0, 150))
    ombra = ombra.filter(ImageFilter.GaussianBlur(14))
    tela.alpha_composite(ombra)

    tela.alpha_composite(angoli_arrotondati(im, raggio), (x, y))

    # bordo sottile
    ImageDraw.Draw(tela).rounded_rectangle(
        [x, y, x + im.width - 1, y + im.height - 1],
        radius=raggio, outline=(255, 255, 255, 40), width=2)
    return im.size


def alone(tela, centro, raggio, colore, intensita=70):
    """Alone morbido di colore, per staccare le catture dal fondo."""
    strato = Image.new("RGBA", tela.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(strato)
    cx, cy = centro
    d.ellipse([cx - raggio, cy - raggio, cx + raggio, cy + raggio],
              fill=colore + (intensita,))
    strato = strato.filter(ImageFilter.GaussianBlur(raggio // 2))
    tela.alpha_composite(strato)


def main():
    if not os.path.isdir(CATTURE):
        print("Manca la cartella %s" % CATTURE)
        sys.exit(1)

    tela = Image.new("RGBA", (L, A), SFONDO + (255,))

    # fondo: due aloni appena accennati
    alone(tela, (980, 300), 340, VERDE, 38)
    alone(tela, (240, 520), 300, (56, 120, 255), 22)

    # ---- catture a destra -------------------------------------------------
    scena = os.path.join(CATTURE, "scena_ita.png")
    menu = os.path.join(CATTURE, "menu_iniziale.png")
    impostazioni = os.path.join(CATTURE, "impostazioni.png")

    # Disposizione a scala, dall'alto a sinistra al basso a destra. Le misure
    # sono scelte perche' NESSUNA cattura esca dalla tela o venga tagliata da
    # un'altra: un menu con "Lingua" mozzato a "gua" sembra un errore, non un
    # effetto grafico.
    if os.path.exists(impostazioni):
        incolla_cattura(tela, impostazioni, (648, 34), scala=0.52, raggio=8)
    if os.path.exists(menu):
        incolla_cattura(tela, menu, (946, 58), scala=0.60, raggio=8)
    if os.path.exists(scena):
        incolla_cattura(tela, scena, (606, 276), scala=0.80, raggio=10)

    d = ImageDraw.Draw(tela)

    # ---- testo a sinistra --------------------------------------------------
    x = 68

    d.text((x, 96), "TRADUZIONE AMATORIALE", font=grassetto(19), fill=VERDE_CHIARO)

    d.text((x, 138), "Rejuvenation", font=grassetto(74), fill=BIANCO)
    d.text((x, 216), "ITA Patch", font=grassetto(74), fill=VERDE)

    d.rounded_rectangle([x, 316, x + 96, 322], radius=3, fill=VERDE)

    d.text((x, 350), "Pokémon Rejuvenation in italiano:", font=normale(27), fill=BIANCO)
    d.text((x, 386), "dialoghi, interfaccia, oggetti e mosse.", font=normale(27), fill=GRIGIO)

    # dato di copertura
    d.text((x, 452), "99,9%", font=grassetto(62), fill=VERDE_CHIARO)
    d.text((x + 196, 470), "del testo", font=normale(24), fill=BIANCO)
    d.text((x + 196, 500), "del gioco tradotto", font=normale(24), fill=GRIGIO)

    d.text((x, 578), "github.com/giosci1994/rejuvenation-ita-patch",
           font=normale(20), fill=GRIGIO)

    # filo verde in basso, come rifinitura
    d.rectangle([0, A - 5, L, A], fill=VERDE)

    os.makedirs(os.path.dirname(USCITA), exist_ok=True)
    tela.convert("RGB").save(USCITA, "PNG", optimize=True)

    kb = os.path.getsize(USCITA) / 1024
    print("scritto %s" % USCITA)
    print("  %dx%d, %.0f KB (il limite di GitHub e' 1 MB)" % (L, A, kb))


if __name__ == "__main__":
    main()
