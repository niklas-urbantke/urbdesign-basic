# urbDesign — Theme "Aero Plasma"

Ein token-basierter CSS-Baukasten mit Light- und Dark-Theme. Die Optik zitiert das
Aero-Glas aus Windows Vista und Windows 7, liest es aber modern: echte Unschärfe
statt gemalter Verläufe, subtiler Glanz statt Chrom, große weiche Radien.

Farbwelt: helles Blau (Azure) als Akzent, Lila-Indigo als Verlaufspartner,
Orange-Gelb (Amber) und dunkles Grün (Jade) als weitere Markentöne. Icons sind
farbfähig und können einfarbig, bunt, duotone, mit Verlaufsstrich oder als
Glaskachel erscheinen.

## Öffnen

`index.html` im Browser öffnen, auch per Doppelklick. Der Umschalter oben rechts
wechselt das Theme, die Wahl bleibt gespeichert. Ohne eigene Wahl folgt die Seite
der System-Einstellung.

`icons.html` zeigt alle Icons mit Suche, Filter, Größenregler und den fünf
Darstellungsarten. Diese Seite lädt das Sprite per `fetch` und braucht deshalb
einen lokalen Server:

```bash
python3 -m http.server 8000
```

## Prüfen

Vor jedem Commit, ohne Abhängigkeiten:

```bash
python3 pruefen.py
```

Das Skript meldet Verstöße gegen die eiserne Regel, unbekannte Tokens, ein
veraltetes Sprite in `index.html` und jeden Kontrast unter 4.5:1. Exitcode 1
bei Fehlern, damit es sich in einen Hook hängen lässt.

## Dateien

| Datei | Zweck |
|---|---|
| `tokens.css` | Alle Design-Tokens: Primitive und semantische Rollen, Light und Dark. Die einzige Datei mit Rohwerten. |
| `components.css` | Der Baukasten. Reset, Grundtypografie und alle Komponenten. Nutzt ausschließlich semantische Tokens. |
| `icons.svg` | Icon-Set als Sprite, 101 Linien-Icons, farbfähig. |
| `icons.css` | Nur das Layout der Icon-Übersicht. |
| `icons.html` | Icon-Übersicht. |
| `showcase.css` | Nur das Layout der Demo-Seite. Nicht Teil des Systems. |
| `index.html` | Der Style-Guide mit allen Farben, Skalen und Komponenten. |
| `theme.js` | Theme-Umschaltung über `data-theme` am `<html>`. |
| `pruefen.py` | Selbstprüfung: Regeln, Tokens, Sprite-Stand, WCAG-Kontraste. |
| `CHANGELOG.md` | Was sich wann geändert hat. |

## Das Prinzip: zwei Ebenen, eine Regel

```
Komponente  →  benutzt nur  →  semantisches Token  →  zeigt auf  →  Primitiv
.btn--primary    var(--color-accent)     --color-accent: var(--urb-azure-600)   #036bc7
```

**Ebene 1, Primitive.** Heißen `--urb-*`. Rohwerte der Palette. Sie ändern sich nie
mit dem Theme.

**Ebene 2, semantisch.** Alles ohne `urb-`: `--color-*`, `--glass-*`, `--shadow-*`,
`--tone-*`, dazu die nicht-farbigen Skalen `--space-*`, `--radius-*`, `--text-*`.
Nur diese Ebene benutzen die Komponenten.

Daraus folgt die einzige Regel, die das System zusammenhält:

> In `components.css`, `showcase.css`, `icons.css` und in jedem `style`-Attribut
> stehen **niemals `--urb-*` und niemals rohe Farbwerte** (`#hex`, `rgb()`, `hsl()`).

### Zweite Regel: keine `background`-Kurzform

> Statt `background:` immer `background-color:` oder `background-image:` schreiben.

Die Kurzform setzt alle Untereigenschaften zurück, darunter `background-origin`.
Das System stellt diese im base-Layer auf `border-box`, weil ein Verlauf sonst nur
über die innere Fläche aufgespannt und im Bereich des Rahmens mit seiner Endfarbe
fortgesetzt wird. Sichtbar wird das als andersfarbiger Saum an Flächen mit Verlauf
und Rahmen, oben hell und unten oder links dunkel. Ein einziges `background:`
genügt, um den Effekt zurückzuholen. `pruefen.py` meldet jede Kurzform.

Die Regel ist mit einem Befehl prüfbar. Sie muss ohne Treffer bleiben:

```bash
grep -nE '#[0-9a-fA-F]{3}|rgba?\(|hsla?\(|--urb-[a-z]' components.css showcase.css icons.css
```

Ein Theme-Wechsel biegt nur Ebene 2 um. Kein Komponentencode wird angefasst, und
der Wechsel wirkt überall gleichzeitig.

## Ladereihenfolge

```html
<style>@layer tokens, base, components, showcase;</style>
<link rel="stylesheet" href="tokens.css">
<link rel="stylesheet" href="components.css">
<link rel="stylesheet" href="showcase.css">
<script src="theme.js"></script>
```

Die Layer-Zeile steht vor den Stylesheets und legt die Rangfolge einmal fest.
Spätere Layer gewinnen, ganz ohne `!important`.

## Einbau in eine Seite mit fremdem CSS

Die Layer-Reihenfolge regelt nur das Verhältnis der eigenen Dateien zueinander.
Gegenüber fremdem CSS gilt eine Regel der Kaskade, die leicht übersehen wird:

> **Deklarationen außerhalb aller `@layer` schlagen jede gelayerte Deklaration**,
> unabhängig von der Spezifität.

Bringt die umgebende Seite einen eigenen Reset mit, der nicht in einem Layer
steht (etwa `body { background: #fafaf9 }`), gewinnt dieser gegen
`@layer base { body { background: var(--color-bg) } }`. Sichtbar wird das vor
allem im Dark-Theme: die Tokens schalten korrekt um, aber der Grund bleibt hell,
und weil die Glasflächen halbtransparent sind, wirkt fast die ganze Seite hell.

Abhilfe: einen kleinen, bewusst **ungelayerten** Block ans Ende hängen, der die
Grundflächen aus den Tokens durchsetzt.

```css
/* Ohne @layer, damit es den Reset der umgebenden Seite schlaegt. */
html { color-scheme: light; background-color: var(--color-bg); }
html[data-theme="dark"] { color-scheme: dark; }
body {
  margin: 0;
  background-color: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
}
```

In diesem Repository wird der Block nicht gebraucht, weil hier kein fremdes CSS
mitspielt. Beim Einbau in eine bestehende Anwendung ist er der erste Handgriff.

## Der Glas-Effekt

`.glass` ist das Fundament, alles Glasige leitet sich davon ab. Es besteht aus
fünf Zutaten, die zusammen den Aero-Eindruck ergeben:

1. **Unschärfe mit Sättigung**: `backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-saturate))`.
   Die Sättigung ist wichtig, sonst wirkt der Hintergrund hinter dem Glas ausgewaschen.
2. **Tint**: eine halbtransparente Eigenfarbe, `--glass-tint`. Sie hält Text lesbar.
3. **Kante**: eine feine, dunklere Innenkante unten (`--glass-lowlight`) und ein
   neutraler, bewusst nicht weißer Rand (`--glass-edge`). Ein heller Saum auf einer
   farbigen Fläche liest sich als Fehler, nicht als Glanz, deshalb trägt das System
   keine weiße Lichtkante mehr.
4. **Sheen**: ein diagonaler Glanzverlauf über der Fläche, `--glass-sheen`.
5. **Körnung**: das Rauschmuster `--urb-noise` mit `--glass-noise-opacity`, eine
   Anleihe beim Acryl aus Fluent. Es nimmt der Fläche das Sterile.

Varianten: `.glass--strong` (deckender, für Dialoge), `.glass--sunken` (eingelassen,
für Eingabefelder), `.glass--glow` (farbiger Schein).

Damit Glas überhaupt wirkt, braucht die Seite etwas hinter sich. Die Demo-Seite
legt dafür einen ruhigen Verlauf aus zwei Markentönen hinter den Inhalt, der sich
über die Tokens von selbst an Hell und Dunkel anpasst. Je mehr Struktur der
Hintergrund hat, desto deutlicher ist die Unschärfe ablesbar.

## Icons

Die Icons sind Linien-Icons, 24x24, und tragen keine feste Farbe. Sie holen sich
alles von außen:

```html
<svg class="icon" aria-hidden="true"><use href="#check"></use></svg>
```

Fünf Darstellungsarten:

| Klasse | Wirkung |
|---|---|
| ohne Zusatz | einfarbig in `currentColor` |
| `.icon--azure` … `.icon--slate` | Tönung aus einem der sechs Markentöne |
| `.icon--duo` | Duotone: die geschlossenen Flächen werden zart gefüllt |
| `.icon--grad-accent` … | Verlaufsstrich aus dem Sprite |
| `.icon-tile .icon-tile--jade` | farbige Glaskachel mit dem Icon darin |

Größen über `--icon-size` oder `.icon--xs`, `.icon--sm`, `.icon--lg`, `.icon--xl`.

Das funktioniert, weil jedes `<symbol>` `stroke="var(--icon-stroke, currentColor)"`
und `fill="var(--icon-fill, none)"` trägt. Voraussetzung: **das Sprite muss im
selben Dokument liegen**, sonst greifen weder die Variablen noch `url(#urb-grad-…)`.
`index.html` hat es deshalb inline eingebettet, `icons.html` lädt und injiziert es.

Neues Icon: in `icons.svg` ein weiteres `<symbol id="name" data-cat="Kategorie"
data-tone="ton" …>` ergänzen. Die Übersicht baut sich automatisch daraus auf.

## Anpassen

- **Akzentfarbe tauschen:** in `tokens.css` die vier Zeilen `--color-accent*` auf
  eine andere Palette zeigen lassen, etwa `var(--urb-jade-600)`. Sonst nichts.
- **Eigene Palette:** die `--urb-<name>-50` bis `-900` ergänzen, dann die
  semantischen Rollen darauf zeigen lassen.
- **Weiteres Theme:** einen Block `[data-theme="name"] { … }` mit eigenen
  semantischen Werten anlegen. Die Primitive bleiben unberührt.
- **Glas stärker oder schwächer:** `--glass-blur`, `--glass-tint` und
  `--glass-noise-opacity` sind die drei Stellschrauben.
- **Weniger Bewegung:** ist zentral gelöst. `prefers-reduced-motion` setzt die
  `--dur-*`-Tokens auf 1ms, alle Übergänge halten damit von selbst still.

## Breakpoints

CSS-Variablen wirken in Media Queries nicht, deshalb eine Konvention mit festen
Werten, immer `min-width`:

```
sm 40rem    md 52rem    lg 64rem    xl 80rem
```

## Absicht dieser Vorlage

Das Repository ist bewusst schlicht gehalten: reines CSS, kein Build-Schritt, keine
Abhängigkeiten, alle Werte direkt lesbar. Wer damit weiterbaut, ob Mensch oder
Agent, soll den kompletten Zusammenhang in `tokens.css` und `components.css` sehen,
ohne ein Werkzeug starten zu müssen.

## Übernahme in urbBase

`tokens.css` (dort aufgeteilt in `primitives.css` und `semantic.css`) und
`components.css` gehören nach `shell-ui/src/theming/`. `index.html`, `showcase.css`,
`icons.html` und `icons.css` bleiben Referenzdokumente und wandern nicht mit.
