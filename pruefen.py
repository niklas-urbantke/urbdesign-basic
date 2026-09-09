#!/usr/bin/env python3
"""urbDesign, Selbstpruefung des Design-Systems.

Aufruf:  python3 pruefen.py

Aufruf:  python3 pruefen.py --selbsttest   (nur die Selbsttests der Regeln)

Prueft sieben Dinge:
  1. CSS-Struktur: Verschachtelung der Bloecke, nicht nur ihre Bilanz
  2. Die eiserne Regel: kein --urb-* und kein roher Farbwert ausserhalb tokens.css
  3. Jedes benutzte Token ist definiert oder hat einen Fallback
  4. Das Icon-Sprite in index.html ist auf dem Stand von icons.svg
  5. WCAG-Kontraste aller Textstufen, je Theme, auch auf Glasflaechen
  6. Symbolfaehigkeit: jede Klasse, die ein Symbol aufnehmen kann, hat
     display mit Flex-Wert und gap (D12a)
  7. Showcase: index.html zeigt zu jeder dieser Klassen eine Variante mit
     Symbol (D12b, nur Warnung)

Keine Abhaengigkeiten, nur die Standardbibliothek.
"""
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
CSS_DATEIEN = ["components.css", "showcase.css", "icons.css"]
HTML_DATEIEN = ["index.html", "icons.html"]

fehler, warnungen = [], []


def entkommentiert(css):
    return re.sub(r"/\*.*?\*/", " ", css, flags=re.S)


def entkommentiert_zeilentreu(css):
    """Wie entkommentiert, behaelt aber die Zeilenumbrueche, damit
    gemeldete Zeilennummern zur Datei passen."""
    return re.sub(r"/\*.*?\*/",
                  lambda m: "\n" * m.group(0).count("\n"), css, flags=re.S)


# ============================================================
#  1 bis 4: Struktur und Regeln
# ============================================================
def pruefe_syntax(name, css):
    """Struktur statt Bilanz.

    Blosses Zaehlen findet den haeufigsten Fall nicht: eine schliessende
    Klammer zu viel an einer Stelle und eine zu wenig an einer anderen
    gleichen sich in der Summe aus. Deshalb wird die Verschachtelung
    Zeichen fuer Zeichen verfolgt.
    """
    if css.count("/*") != css.count("*/"):
        fehler.append(f"{name}: Kommentare unbalanciert "
                      f"({css.count('/*')} auf, {css.count('*/')} zu)")

    code = re.sub(r'"[^"]*"|\'[^\']*\'', '""', entkommentiert_zeilentreu(css))

    stapel = []          # offene Bloecke als (Zeile, Kopfzeile)
    zeile = 1
    for i, c in enumerate(code):
        if c == "\n":
            zeile += 1
        elif c == "{":
            kopf = code.rfind("\n", 0, i)
            stapel.append((zeile, code[kopf + 1:i].strip()[:60]))
        elif c == "}":
            if not stapel:
                fehler.append(f"{name}:{zeile}: ueberzaehlige schliessende Klammer")
            else:
                stapel.pop()

    for z, kopf in stapel:
        fehler.append(f"{name}:{z}: Block nicht geschlossen -> {kopf!r}")

    # Eine At-Regel darf nicht in einem @keyframes stehen. Genau das
    # passiert, wenn ein @keyframes-Block seine Klammer verliert: der
    # naechste verschwindet stillschweigend darin.
    tiefe, in_keyframes = 0, None
    zeile = 1
    for m in re.finditer(r"\n|@[a-z-]+|[{}]", code):
        t = m.group(0)
        if t == "\n":
            zeile += 1
        elif t == "{":
            tiefe += 1
        elif t == "}":
            tiefe -= 1
            if in_keyframes is not None and tiefe <= in_keyframes[0]:
                in_keyframes = None
        elif t.startswith("@"):
            if in_keyframes is not None:
                fehler.append(f"{name}:{zeile}: {t} steht im @keyframes von "
                              f"Zeile {in_keyframes[1]}, dort fehlt eine schliessende Klammer")
            elif t == "@keyframes":
                in_keyframes = (tiefe, zeile)

    for auf, zu, was in (("(", ")", "runde"),):
        if code.count(auf) != code.count(zu):
            fehler.append(f"{name}: {was} Klammern unbalanciert "
                          f"({code.count(auf)} auf, {code.count(zu)} zu)")


FUNC = re.compile(r"\b(?:rgba?|hsla?)\s*\(")
# --urb-noise ist ein Rauschmuster ohne Farbe und ausdruecklich erlaubt.
URB = re.compile(r"--urb-(?!noise\b)[a-z]")


# ------------------------------------------------------------
#  Hex-Erkennung (D11)
# ------------------------------------------------------------
# Frueher genuegte "#" plus drei bis acht Hex-Ziffern. Damit galt die
# Vue-Kurzform eines Slots (<template #bad>) als Farbe, ebenso jeder
# Anker (href="#check") und jeder Verweis auf einen Verlauf (url(#id)).
# Ein echter Farbwert steht in Wertposition, also hinter einem
# Doppelpunkt oder in einer Funktionsklammer.
HEX_KANDIDAT = re.compile(r"#[0-9a-fA-F]{3,8}")
# Direkt vor einem Farbwert steht nie ein Anfuehrungs- oder Gleichheitszeichen.
VOR_KEIN_HEX = "\"'="
URL_DAVOR = re.compile(r"url\(\s*$", re.I)
# Grenzen des laufenden Abschnitts: Deklaration, Block, HTML-Tag.
TRENNER = ";{}<>"
WORTZEICHEN = re.compile(r"[\w-]")


def hex_treffer(text):
    """Liefert alle rohen Farbwerte in CSS-Wertposition als Match-Objekte.

    Ein Treffer verlangt dreierlei:
      * 3, 4, 6 oder 8 Hex-Ziffern und danach kein Wortzeichen
      * kein Anfuehrungszeichen, Gleichheitszeichen oder url( davor
      * Wertposition: im laufenden Abschnitt steht ein Doppelpunkt davor,
        oder die Stelle liegt in einer noch offenen Funktionsklammer
    """
    for m in HEX_KANDIDAT.finditer(text):
        if len(m.group(0)) - 1 not in (3, 4, 6, 8):
            continue
        rest = text[m.end():m.end() + 1]
        if rest and WORTZEICHEN.match(rest):
            continue
        davor = text[:m.start()]
        if davor and davor[-1] in VOR_KEIN_HEX:
            continue
        if URL_DAVOR.search(davor):
            continue
        schnitt = max(davor.rfind(c) for c in TRENNER)
        abschnitt = davor[schnitt + 1:]
        offene_klammer = abschnitt.count("(") - abschnitt.count(")")
        if ":" not in abschnitt and offene_klammer <= 0:
            continue
        yield m


def hat_hex(text):
    return any(True for _ in hex_treffer(text))


# Gegentest laut Vertrag D11: links der Text, rechts ob ein Treffer erwartet wird.
HEX_FAELLE = [
    ("color: #bad", True),
    ("border-color:#a1b2c3", True),
    ("box-shadow: 0 0 0 #fff8", True),
    ("background-image: linear-gradient(#fff, #000)", True),
    ("<template #bad>", False),
    ('href="#check"', False),
    ("url(#urb-grad-azure)", False),
    ('<use href="#urb-grad-rose">', False),
    ("#nicht-hex", False),
    ("url(#fade)", False),
    ('<use xlink:href="#beef">', False),
    ("color: #abcde", False),
    ("#app { color: var(--color-text); }", False),
]


def selbsttest_hex():
    """Prueft die Hex-Regel gegen die Faelle aus dem Vertrag.
    Gibt die Liste der durchgefallenen Faelle zurueck, leer heisst bestanden."""
    durchgefallen = []
    for text, erwartet in HEX_FAELLE:
        ist = hat_hex(text)
        if ist != erwartet:
            durchgefallen.append(
                f"{text!r}: erwartet {'Treffer' if erwartet else 'kein Treffer'}, "
                f"bekommen {'Treffer' if ist else 'kein Treffer'}")
    return durchgefallen


if "--selbsttest" in sys.argv:
    schlecht = selbsttest_hex()
    print(f"Selbsttest Hex-Regel: {len(HEX_FAELLE)} Faelle")
    for s in schlecht:
        print("  FEHLGESCHLAGEN " + s)
    print("  bestanden" if not schlecht else f"  {len(schlecht)} fehlgeschlagen")
    sys.exit(1 if schlecht else 0)

for s in selbsttest_hex():
    fehler.append(f"pruefen.py: Selbsttest der Hex-Regel fehlgeschlagen -> {s}")

tokens_css = (ROOT / "tokens.css").read_text()
pruefe_syntax("tokens.css", tokens_css)
DEFINIERT = set(re.findall(r"(--[a-zA-Z0-9-]+)\s*:", tokens_css))

for name in CSS_DATEIEN:
    p = ROOT / name
    if not p.exists():
        fehler.append(f"{name}: fehlt")
        continue
    roh = p.read_text()
    pruefe_syntax(name, roh)
    code = entkommentiert(roh)

    treffer = [(m, "roher Hex-Wert") for m in hex_treffer(code)]
    for muster, label in ((FUNC, "rgb/hsl-Funktion"), (URB, "Primitiv --urb-*")):
        treffer += [(m, label) for m in muster.finditer(code)]
    for m, label in sorted(treffer, key=lambda t: t[0].start()):
        fehler.append(f"{name}:{code[:m.start()].count(chr(10)) + 1}: {label} -> {m.group(0)}")

    # Die Kurzform "background:" setzt background-origin auf padding-box
    # zurueck und hebt damit die Regel aus dem base-Layer auf. Folge ist
    # ein andersfarbiger Saum an Flaechen mit Verlauf und Rahmen.
    for m in re.finditer(r"(?:^|[;{\s])background:\s", code):
        fehler.append(f"{name}:{code[:m.start()].count(chr(10)) + 1}: "
                      f"Kurzform 'background:' setzt background-origin zurueck, "
                      f"bitte background-color oder background-image verwenden")

    lokal = set(re.findall(r"(--[a-zA-Z0-9-]+)\s*:", code))
    for m in re.finditer(r"var\(\s*(--[a-zA-Z0-9-]+)\s*(,)?", code):
        name_t, hat_fallback = m.group(1), bool(m.group(2))
        if name_t in DEFINIERT or name_t in lokal or hat_fallback:
            continue
        fehler.append(f"{name}:{code[:m.start()].count(chr(10)) + 1}: {name_t} weder definiert noch mit Fallback")

# HTML: style-Attribute. Im Farbabschnitt von index.html sind Primitive erlaubt,
# denn dort werden sie ja gerade gezeigt. Der Block ist im HTML als Ausnahme markiert.
for name in HTML_DATEIEN:
    p = ROOT / name
    if not p.exists():
        fehler.append(f"{name}: fehlt")
        continue
    roh = p.read_text()
    ende = roh.find("Ende der Ausnahme")
    for m in re.finditer(r'style="([^"]*)"', roh):
        inhalt, pos = m.group(1), m.start()
        zeile = roh[:pos].count("\n") + 1
        if hat_hex(inhalt) or FUNC.search(inhalt):
            fehler.append(f"{name}:{zeile}: roher Farbwert im style-Attribut")
        if re.search(r"(?:^|;\s*)background:\s", inhalt):
            fehler.append(f"{name}:{zeile}: Kurzform 'background:' im style-Attribut "
                          f"setzt background-origin zurueck")
        if URB.search(inhalt) and not (0 < pos < ende):
            fehler.append(f"{name}:{zeile}: --urb-* im style-Attribut ausserhalb des Farbabschnitts")

# Sprite-Abgleich: index.html traegt eine Kopie von icons.svg.
svg = (ROOT / "icons.svg").read_text()
idx = (ROOT / "index.html").read_text()
im_svg = set(re.findall(r'<symbol\b[^>]*id="([^"]+)"', svg))
im_html = set(re.findall(r'<symbol\b[^>]*id="([^"]+)"', idx))
if im_svg != im_html:
    fehlend = sorted(im_svg - im_html)
    zuviel = sorted(im_html - im_svg)
    fehler.append(f"index.html: Sprite veraltet (fehlen: {fehlend or 'keine'}, ueberzaehlig: {zuviel or 'keine'})")
benutzt = set(re.findall(r'<use\s+href="#([^"]+)"', idx))
if benutzt - im_html:
    fehler.append(f"index.html: benutzt Icons, die es nicht gibt: {sorted(benutzt - im_html)}")


# ============================================================
#  5: Kontraste
# ============================================================
CSS = entkommentiert(tokens_css)


def block(sel):
    i = CSS.find(sel)
    if i < 0:
        sys.exit(f"Token-Block {sel} nicht gefunden")
    i = CSS.index("{", i)
    tiefe, j = 0, i
    while True:
        if CSS[j] == "{":
            tiefe += 1
        elif CSS[j] == "}":
            tiefe -= 1
            if tiefe == 0:
                break
        j += 1
    return dict(re.findall(r"(--[a-zA-Z0-9-]+)\s*:\s*([^;]+);", CSS[i:j]))


PRIM = block(":root {")
THEMES = {
    "LIGHT": dict(PRIM, **block(':root,\n  [data-theme="light"]')),
    "DARK": dict(PRIM, **block('[data-theme="dark"]')),
}


def hex2rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def aufloesen(value, table, tiefe=0):
    """Loest var-Ketten und color-mix auf. -> (r, g, b, alpha) oder None."""
    if tiefe > 12 or value is None:
        return None
    v = value.strip()
    m = re.fullmatch(r"var\(\s*(--[a-zA-Z0-9-]+)\s*(?:,[^)]*)?\)", v)
    if m:
        return aufloesen(table.get(m.group(1)), table, tiefe + 1)
    if v.startswith("#"):
        return hex2rgb(v) + (1.0,)
    m = re.fullmatch(r"color-mix\(\s*in srgb\s*,\s*(.+?)\s+([\d.]+)%\s*,\s*transparent\s*\)", v, re.S)
    if m:
        basis = aufloesen(m.group(1), table, tiefe + 1)
        return None if not basis else (basis[0], basis[1], basis[2], basis[3] * float(m.group(2)) / 100)
    return None


def ueber(vorne, hinten):
    a = vorne[3]
    return tuple(vorne[i] * a + hinten[i] * (1 - a) for i in range(3))


def leuchtdichte(rgb):
    def kanal(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (kanal(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def verhaeltnis(a, b):
    la, lb = leuchtdichte(a), leuchtdichte(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def farbe(table, name, basis=(255, 255, 255)):
    r = aufloesen(table.get(name), table)
    if r is None:
        return None
    return ueber(r, basis) if r[3] < 1 else r[:3]


TEXTE = ["--color-text", "--color-text-secondary", "--color-text-muted"]
ROLLEN = ["--color-accent", "--color-success", "--color-warning", "--color-danger", "--color-info"]
TOENE = ["--tone-azure", "--tone-indigo", "--tone-amber", "--tone-jade", "--tone-rose", "--tone-slate"]
# Farben der Hintergrund-Blobs der Demo-Seite und ihre Deckkraft je Theme.
BLOBS = {"blau": (56, 165, 251), "indigo": (79, 44, 184), "amber": (251, 175, 11), "jade": (47, 164, 115)}
DECKKRAFT = {"LIGHT": 0.45, "DARK": 0.34}

AA = 4.5      # WCAG AA, normaler Text
AA_GROSS = 3.0  # WCAG AA, grosser Text und Bedienelemente

schwach = []
print("Kontraste (WCAG AA verlangt 4.5:1 fuer Text)\n")

for theme, table in THEMES.items():
    print(f"  {theme}")
    grund = farbe(table, "--color-bg")
    flaechen = [(n[8:], farbe(table, n)) for n in
                ("--color-bg", "--color-surface", "--color-surface-2", "--color-surface-3")]

    tint = aufloesen(table["--glass-tint"], table)
    d = DECKKRAFT[theme]
    for n, b in BLOBS.items():
        unter = tuple(b[i] * d + grund[i] * (1 - d) for i in range(3))
        flaechen.append((f"Glas ueber {n}", ueber(tint, unter)))

    kopf = "".join(f"{t.replace('--color-text', 'text'):>16}" for t in TEXTE)
    print(f"    {'Flaeche':<20}{kopf}")
    for fname, f in flaechen:
        zeile = f"    {fname:<20}"
        for t in TEXTE:
            r = verhaeltnis(farbe(table, t, basis=f), f)
            zeile += f"{r:>14.1f}{' ' if r >= AA else '!'} "
            if r < AA:
                schwach.append((theme, t, fname, r))
        print(zeile)

    for gruppe, namen in (("Rollen", ROLLEN), ("Toene", TOENE)):
        f = farbe(table, "--color-surface")
        teile = []
        for n in namen:
            r = verhaeltnis(farbe(table, n, basis=f), f)
            teile.append(f"{n.split('-')[-1]} {r:.1f}{'' if r >= AA else '!'}")
            if r < AA:
                schwach.append((theme, n, "surface", r))
        print(f"    {gruppe + ' auf surface':<20}  " + "  ".join(teile))

    f = farbe(table, "--color-accent")
    r = verhaeltnis(farbe(table, "--color-on-accent", basis=f), f)
    print(f"    {'on-accent':<20}  {r:.1f}{'' if r >= AA else '  ZU WENIG'}")
    if r < AA:
        schwach.append((theme, "--color-on-accent", "accent", r))
    print()

for theme, t, f, r in schwach:
    (fehler if r < AA_GROSS else warnungen).append(f"Kontrast {theme}: {t} auf {f} nur {r:.1f}:1")


# ============================================================
#  6 und 7: Symbolfaehigkeit (D12)
# ============================================================
# Drei gemeldete Layoutfehler hatten dieselbe Wurzel: eine Komponente darf
# ein Symbol aufnehmen, ist aber nicht darauf ausgelegt. Ohne Flex-Anzeige
# und ohne gap klebt das Symbol am Text und sitzt auf der Grundlinie.
# In der Showcase faellt das nicht auf, solange dort nur Textvarianten stehen.
SYMBOL_KLASSEN = [
    "btn", "segmented__item", "tab", "menu__item", "chip", "alert",
    "toast", "badge", "field__group", "page-btn", "step", "empty",
]
# gap ist die Vorgabe; column-gap wird als gleichwertig anerkannt, es
# erzeugt denselben waagerechten Abstand zwischen Symbol und Text.
GAP_NAMEN = ("gap", "column-gap")
GRUPPE = re.compile(r":(?:is|where|matches)\(([^()]*)\)", re.I)
KOMBINATOR = re.compile(r"\s*[>+~]\s*|\s+")
PSEUDO = re.compile(r"(?<!:):(?!:)")


def ohne_strings(css):
    """Ersetzt Zeichenketten durch leere, damit Data-URIs mit Klammern
    oder Semikolon die Zerlegung nicht durcheinanderbringen."""
    return re.sub(r'"[^"]*"|\'[^\']*\'', '""', css)


def css_regeln(css):
    """Zerlegt CSS in (Selektortext, Rumpf) und steigt dabei in @layer,
    @media und @supports hinein. @keyframes und Verwandte bleiben aussen vor."""
    regeln = []

    def lauf(text):
        i = 0
        while True:
            j = text.find("{", i)
            if j < 0:
                return
            kopf = text[i:j].strip()
            k, tiefe = j, 0
            while k < len(text):
                if text[k] == "{":
                    tiefe += 1
                elif text[k] == "}":
                    tiefe -= 1
                    if tiefe == 0:
                        break
                k += 1
            rumpf = text[j + 1:k]
            if kopf.startswith("@"):
                if not kopf.startswith(("@keyframes", "@font-face", "@property")):
                    lauf(rumpf)
            else:
                regeln.append((kopf, rumpf))
            i = k + 1

    lauf(ohne_strings(entkommentiert(css)))
    return regeln


def selektor_teile(sel):
    """Trennt an Kommas der obersten Ebene, also nicht in :is(...)."""
    teile, akt, tiefe = [], "", 0
    for c in sel:
        if c in "([":
            tiefe += 1
        elif c in ")]":
            tiefe -= 1
        if c == "," and tiefe == 0:
            teile.append(akt)
            akt = ""
        else:
            akt += c
    teile.append(akt)
    return [t.strip() for t in teile if t.strip()]


def entfalte(teil, tiefe=0):
    """Loest :is()- und :where()-Sammelselektoren in einzelne Selektoren auf,
    damit eine Deklaration aus einer Gruppe der einzelnen Klasse zugerechnet wird."""
    m = GRUPPE.search(teil)
    if not m or tiefe > 6:
        return [teil]
    raus = []
    for alt in selektor_teile(m.group(1)):
        raus += entfalte(teil[:m.start()] + alt + teil[m.end():], tiefe + 1)
    return raus


def gilt_fuer(selektor, klasse):
    """Wahr, wenn der Selektor das Element selbst und bedingungslos trifft.
    Vorfahren duerfen davorstehen, Zustaende und Zusatzklassen nicht:
    .tab trifft zu, .tabs .tab auch, .tab:hover und .tab.is-active nicht."""
    letzte = KOMBINATOR.split(selektor.strip())[-1]
    if not letzte or "::" in letzte or "[" in letzte or PSEUDO.search(letzte):
        return False
    return re.findall(r"\.([A-Za-z0-9_-]+)", letzte) == [klasse]


def deklarationen(rumpf):
    """Eigenschaft und Wert je Deklaration, in Reihenfolge der Datei."""
    return re.findall(r"(?:^|[;{])\s*(-{0,2}[a-zA-Z][a-zA-Z0-9-]*)\s*:\s*([^;{}]*)", rumpf)


def gesammelt(regeln, klasse):
    """Alle Deklarationen, die fuer die Klasse selbst gelten, quer ueber
    mehrere Regeln und Sammelselektoren. Spaeter gewinnt."""
    werte = {}
    for kopf, rumpf in regeln:
        passt = any(gilt_fuer(s, klasse)
                    for teil in selektor_teile(kopf) for s in entfalte(teil))
        if not passt:
            continue
        for prop, wert in deklarationen(rumpf):
            werte[prop.strip().lower()] = wert.strip()
    return werte


SVG_ICON = re.compile(r'<svg\b[^>]*\bclass="[^"]*\bicon\b', re.I)
LEERE_TAGS = {"input", "img", "br", "hr", "use", "path", "meta", "link", "source"}


def element_inhalt(html, start):
    """Inhalt des Elements, dessen Starttag bei start beginnt."""
    m = re.match(r"<([a-zA-Z][\w-]*)", html[start:])
    if not m:
        return ""
    tag = m.group(1)
    auf_ende = html.find(">", start)
    if auf_ende < 0 or html[auf_ende - 1] == "/" or tag.lower() in LEERE_TAGS:
        return ""
    muster = re.compile(r"</?" + re.escape(tag) + r"\b", re.I)
    tiefe, i = 1, auf_ende + 1
    while True:
        mm = muster.search(html, i)
        if not mm:
            return html[auf_ende + 1:]
        if html[mm.start() + 1] == "/":
            tiefe -= 1
            if tiefe == 0:
                return html[auf_ende + 1:mm.start()]
        else:
            tiefe += 1
        i = mm.end()


def zeigt_symbol(html, klasse):
    """Wahr, wenn irgendein Element mit dieser Klasse ein <svg class="icon ...
    enthaelt, die Showcase also die Variante mit Symbol zeigt."""
    for m in re.finditer(r'class="([^"]*)"', html):
        if klasse not in m.group(1).split():
            continue
        start = html.rfind("<", 0, m.start())
        if start < 0:
            continue
        if SVG_ICON.search(element_inhalt(html, start)):
            return True
    return False


comp_css = (ROOT / "components.css").read_text()
REGELN = css_regeln(comp_css)

print("Symbolfaehigkeit (Flex-Anzeige und gap, D12)\n")
print(f"    {'Klasse':<20}{'display':<16}{'gap':<20}{'Showcase':<10}")
for klasse in SYMBOL_KLASSEN:
    werte = gesammelt(REGELN, klasse)
    anzeige = werte.get("display")
    gap_prop = next((p for p in GAP_NAMEN if werte.get(p)), None)
    gap_wert = werte.get(gap_prop) if gap_prop else None

    fehlt = []
    if not anzeige or "flex" not in anzeige:
        fehlt.append(f"display mit Flex-Wert (gefunden: {anzeige or 'nichts'})")
    if not gap_wert or gap_wert in ("0", "normal"):
        fehlt.append(f"gap (gefunden: {gap_wert or 'nichts'})")
    if fehlt:
        fehler.append(f"components.css: .{klasse} kann ein Symbol aufnehmen, "
                      f"ist aber nicht darauf ausgelegt, es fehlt " + " und ".join(fehlt))

    im_html = zeigt_symbol(idx, klasse)
    if not im_html:
        warnungen.append(f"index.html: zu .{klasse} fehlt ein Beispiel mit "
                         f"<svg class=\"icon ...>, die Symbolvariante fehlt in der Showcase")
    print(f"    {'.' + klasse:<20}{(anzeige or '-'):<16}"
          f"{(gap_wert or '-'):<20}{'ja' if im_html else 'FEHLT':<10}")
print()


# ============================================================
#  Ergebnis
# ============================================================
print("=" * 62)
if warnungen:
    print(f"\n{len(warnungen)} Warnung(en):")
    for w in warnungen:
        print("  " + w)
if fehler:
    print(f"\n{len(fehler)} Fehler:")
    for f in fehler:
        print("  " + f)
    sys.exit(1)
print(f"\nAlles in Ordnung. {len(DEFINIERT)} Tokens, {len(im_svg)} Icons.")
