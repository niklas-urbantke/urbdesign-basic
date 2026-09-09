#!/usr/bin/env python3
"""urbDesign, Selbstpruefung des Design-Systems.

Aufruf:  python3 pruefen.py

Prueft fuenf Dinge:
  1. CSS-Syntax grob (Kommentare geschlossen, Klammern balanciert)
  2. Die eiserne Regel: kein --urb-* und kein roher Farbwert ausserhalb tokens.css
  3. Jedes benutzte Token ist definiert oder hat einen Fallback
  4. Das Icon-Sprite in index.html ist auf dem Stand von icons.svg
  5. WCAG-Kontraste aller Textstufen, je Theme, auch auf Glasflaechen

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


# ============================================================
#  1 bis 4: Struktur und Regeln
# ============================================================
def pruefe_syntax(name, css):
    if css.count("/*") != css.count("*/"):
        fehler.append(f"{name}: Kommentare unbalanciert ({css.count('/*')} auf, {css.count('*/')} zu)")
    body = re.sub(r'"[^"]*"|\'[^\']*\'', '""', entkommentiert(css))
    for auf, zu, was in (("{", "}", "geschweifte"), ("(", ")", "runde")):
        if body.count(auf) != body.count(zu):
            fehler.append(f"{name}: {was} Klammern unbalanciert ({body.count(auf)} auf, {body.count(zu)} zu)")


HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
FUNC = re.compile(r"\b(?:rgba?|hsla?)\s*\(")
# --urb-noise ist ein Rauschmuster ohne Farbe und ausdruecklich erlaubt.
URB = re.compile(r"--urb-(?!noise\b)[a-z]")

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

    for muster, label in ((HEX, "roher Hex-Wert"), (FUNC, "rgb/hsl-Funktion"), (URB, "Primitiv --urb-*")):
        for m in muster.finditer(code):
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
        if HEX.search(inhalt) or FUNC.search(inhalt):
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
