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

### Markenzeichen gehören nicht ins Set

Symbole für fremde Marken (Spotify, GitHub, Google und so weiter) sind bewusst
**nicht** enthalten, und das soll so bleiben. Drei Gründe:

- Sie unterliegen fremden Marken- und Gestaltungsrichtlinien, die meist
  vorschreiben, dass Form und Farbe unverändert bleiben.
- Genau das bricht die Regel dieses Sets: jedes Symbol bekommt seine Farbe vom
  System, über `currentColor` und die Tönungsklassen. Ein Markenzeichen darf das
  nicht.
- Sie ändern sich nach fremdem Zeitplan und müssten getrennt gepflegt werden.

Wohin stattdessen: eine eigene, klar getrennte Datei in der Anwendung, etwa
`marken.svg`, mit unveränderten Originalen. Als Quelle eignet sich
[Simple Icons](https://simpleicons.org). Diese Symbole werden **ohne** die
`.icon--*`-Tönungsklassen eingebunden und behalten ihre eigene Farbe.

### Was `activity` ist und was nicht

`activity` ist eine Pulslinie und steht für den Zustand eines Systems, nicht für
Statistik. Für Auswertungen und Diagramme gibt es `bar-chart`, `line-chart` und
`pie-chart`. Wer beides mit `activity` löst, bekommt zwei gleiche Bilder mit
verschiedener Bedeutung nebeneinander.

## Achsen: was `data-theme` NICHT tragen sollte

Beim ersten Einsatz in einer echten Anwendung wurden vier unabhängige Fragen in
ein einziges `data-theme` gepresst. Das geht schief: Ein Stil-Block, der
`color-scheme: light` mitbrachte, hat im dunklen Erscheinungsbild sämtliche
Bedienelemente ins Helle gekippt, weil er eine Rolle umgebogen hat, die nicht zu
seiner Achse gehört.

Trenne die Achsen auf eigene Attribute, alle am Wurzelelement:

| Attribut | Werte | Darf umbiegen |
|---|---|---|
| `data-theme` | `light`, `dark` | **Nur** hell/dunkel: Flächen, Text, Linien, Schatten, Glas-Tints, `color-scheme` |
| `data-style` | frei, z. B. `aero`, `klassik` | Den kompletten Token-Satz, aber **kein** `color-scheme` und keine Komponenten-Regeln |
| `data-accent` | `azure`, `indigo`, `amber`, `jade`, `rose`, `slate` | Nur `--color-accent*`, `--color-focus-ring`, `--gradient-accent` |
| `data-glass` | `on` (Standard), `off` | Nur `--glass-*` |
| `data-gradients` | `on` (Standard), `off` | Nur `--gradient-*` und `--tone-*-grad` |

```html
<html data-theme="dark" data-style="aero" data-accent="jade" data-glass="off">
```

Die eiserne Regel dahinter: **Jede Achse fasst nur die Rollen an, für die sie
zuständig ist.** `color-scheme` gehört ausschließlich zu `data-theme`. Sobald
eine zweite Achse es setzt, gewinnt je nach Reihenfolge mal die eine, mal die
andere, und die nativen Bedienelemente kippen.

`data-glass` und `data-gradients` sind in `tokens.css` bereits umgesetzt.
`data-accent` und `data-style` sind als Muster gedacht, siehe die nächsten
beiden Abschnitte.

### Akzentfarbe als eigene Achse

```css
[data-accent="jade"] {
  --color-accent:        var(--urb-jade-600);
  --color-accent-hover:  var(--urb-jade-700);
  --color-accent-active: var(--urb-jade-800);
  --color-accent-soft:   var(--urb-jade-50);
  --color-accent-line:   var(--urb-jade-200);
  --color-focus-ring:    color-mix(in srgb, var(--urb-jade-500) 55%, transparent);
  --gradient-accent:     linear-gradient(140deg, var(--urb-jade-300), var(--urb-jade-600));
}
```

Diese Blöcke gehören hinter die Theme-Blöcke und brauchen je Theme eine eigene
Fassung, weil im Dunkeln hellere Stufen nötig sind.

## Zweiter Token-Satz als Stil

Soll der bisherige Look einer Anwendung neben dem neuen wählbar bleiben, ist der
saubere Weg **eine zweite Token-Datei ohne zweite Komponenten-Schicht**:

```html
<style>@layer tokens, base, components, showcase;</style>
<link rel="stylesheet" href="tokens.css">
<link rel="stylesheet" href="tokens-klassik.css">   <!-- nur [data-style="klassik"] -->
<link rel="stylesheet" href="components.css">
```

```css
@layer tokens {
  [data-style="klassik"] { --color-accent: …; --radius-md: …; }
  [data-style="klassik"][data-theme="dark"] { … }
}
```

**Die Einschränkung, die dabei zu beachten ist:** In den Token-Layer gehört nur,
was ein Token ist. Regeln, die eine Komponente betreffen, etwa runde Pillen
statt kantiger Ecken über `.btn { border-radius: 999px }`, verlieren dort gegen
`components.css`, weil der `components`-Layer später kommt. Solche Regeln
brauchen entweder ein Token (`--radius-md` umbiegen genügt für den Pillen-Fall
meist schon) oder einen eigenen Layer **hinter** `components`:

```css
@layer tokens, base, components, stil, showcase;
```

Faustregel: Lässt sich der Unterschied als Token ausdrücken, gehört er in den
Token-Layer. Braucht er einen Selektor auf eine Komponente, gehört er in einen
eigenen Layer dahinter.

## Wann Glas abschalten

`backdrop-filter` verwischt, was hinter der Fläche liegt. Liegt dort nichts,
etwa weil die Anwendung einen einfarbigen Grund hat, ist der Effekt unsichtbar
und kostet trotzdem Rechenzeit, auf jedem Frame und auf jeder Fläche.

Schalte Glas ab, wenn eines davon zutrifft:

- der Seitenhintergrund ist einfarbig
- die Oberfläche ist sehr dicht, etwa Tabellen und Listen über den ganzen Schirm
- die Zielgeräte sind schwach, oder die Anwendung läuft in vielen Fenstern
- gemessene Bildraten brechen beim Rollen ein

```html
<html data-glass="off">
```

Der Schalter setzt Unschärfe auf 0, macht die Tints deckend und nimmt die
Körnung heraus. Alles andere bleibt: Farben, Abstände, Radien, Schatten. Es
braucht also keine eigenen Überschreibungen in der Anwendung.

## Portierung auf andere Plattformen

Das System wurde nach Jetpack Compose übersetzt. Was dabei ging und was nicht:

| Token-Gruppe | Übertragbar | Anmerkung |
|---|---|---|
| Farben (`--urb-*`, `--color-*`, `--tone-*`) | ja, eins zu eins | Hex-Werte direkt übernehmen, Theme-Umschaltung über zwei Farbschemata |
| Abstände (`--space-*`) | ja | rem in dp, Faktor 16 |
| Radien (`--radius-*`) | ja | `--radius-full` wird zu einer Kapselform |
| Typografie (`--text-*`, `--font-*`) | ja | Schriftfamilie ersetzen, Skala bleibt |
| Schatten (`--shadow-*`) | teilweise | Plattform-Elevation statt mehrschichtiger Schatten, Farbe geht verloren |
| Ebenen (`--z-*`) | teilweise | Reihenfolge ergibt sich meist aus der Komposition |
| Verläufe (`--gradient-*`) | ja | als Brush nachbauen |
| **`backdrop-filter`** | **nein** | Auf Android erst ab API 31 über `RenderEffect`, und nur mit einer eigenen Ebene **unter** dem Inhalt, sonst wird der Text mit unscharf. Darunter: deckende Fläche aus `--glass-tint`. |
| **Körnung (`--urb-noise`)** | **nein** | Kostet Füllrate und ist auf Telefondichten kaum sichtbar. Ersatzlos streichen. |
| `color-mix()` | nein | Vorher ausrechnen und als fester Wert übernehmen |
| `prefers-reduced-motion` | ja | Plattform-Einstellung abfragen |

Praktischer Weg: Die beiden nicht übertragbaren Punkte sind genau die, die
`data-glass="off"` ausschaltet. Eine Portierung entspricht damit dem System im
Zustand `data-glass="off"`, was auch die Vorlage für den Vergleich liefert.

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
