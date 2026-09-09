# Änderungen

## v0.3.2 — Kantensaum endgültig behoben (2026-09-09)

Der andersfarbige Saum an den Glanz-Kacheln war zurück, laut Rückmeldung an
mehreren Stellen. Die globale Regel `background-origin: border-box` aus v0.2.3
stand unverändert im base-Layer, wurde aber ausgehebelt.

**Ursache: die Kurzschreibweise.** `background:` setzt alle Untereigenschaften auf
ihren Anfangswert zurück, auch `background-origin`. Jede Stelle, die
`background: var(--gradient-accent)` schrieb, hat damit `padding-box`
wiederhergestellt. In `index.html` standen diese Angaben zusätzlich als
`style`-Attribut, also mit der höchsten Spezifität überhaupt.

- 13 Vorkommen in `index.html`, `showcase.css`, `icons.css` und `components.css`
  auf `background-color:` beziehungsweise `background-image:` umgestellt
- `pruefen.py` meldet die Kurzform ab jetzt als Fehler, in CSS-Dateien und in
  `style`-Attributen. Gegengetestet: eine testweise eingebaute Kurzform wird
  gefunden
- Die Regel steht im README unter „Zweite Regel: keine background-Kurzform"

Ein Fix, den eine einzelne Zeile an anderer Stelle stillschweigend aufhebt, ist
kein Fix. Deshalb diesmal mit Prüfung statt nur mit Korrektur.

## v0.3.1 — Rahmen bei Hinweisen, ruhiger Hintergrund (2026-09-09)

**Hinweise mit Rahmen rundherum.** `.alert` hatte einen dünnen Rahmen in einer
eigenen Linienfarbe plus eine dickere farbige Kante nur an der Startseite. Der
Rahmen läuft jetzt in `--border-med` und in der Tonfarbe des Zustands um die
ganze Fläche, genau wie beim Toast. Das Token `--alert-line` wird damit nicht
mehr gebraucht und ist aus allen vier Varianten entfernt.

**Linienmuster im Hintergrund entfernt.** Zur Frage, ob es zum Theme gehört:
nein. Es lag in `showcase.css`, also im Layout der Demo-Seite, nicht im
Design-System. `tokens.css` und `components.css` waren nie beteiligt.

An seiner Stelle steht jetzt ein ruhiger Verlauf über zwei Markentöne:

```css
background-image: linear-gradient(150deg,
  color-mix(in srgb, var(--tone-azure) 16%, var(--color-bg)) 0%,
  var(--color-bg) 46%,
  color-mix(in srgb, var(--tone-indigo) 14%, var(--color-bg)) 100%);
```

Weil sowohl die Markentöne als auch `--color-bg` pro Theme umgestellt werden,
passt sich der Verlauf ohne eigene Dark-Regel an. Entfallen sind damit vier
animierte Farbblobs, zwei Streifenraster, drei Keyframe-Animationen und der
zugehörige `prefers-reduced-motion`-Riegel, dazu fünf Elemente in `index.html`.

Nebenwirkung, bewusst in Kauf genommen: Ein glatter Verlauf gibt der Unschärfe
weniger zu verwischen, der Glaseffekt ist auf der Seite dadurch dezenter. Die
Bühne im Abschnitt „Glas" behält ihr Streifenmuster, dort soll die Unschärfe
ablesbar bleiben.

## v0.3 — Kantiger, flacher, satteres Rot (2026-09-09)

Fünf Vorgaben umgesetzt.

**Weniger runde Ecken.** Die Radienskala rückt deutlich zusammen:

| Token | vorher | nachher |
|---|---|---|
| `--radius-sm` | 6px | 3px |
| `--radius-md` | 10px | 5px |
| `--radius-lg` | 14px | 8px |
| `--radius-xl` | 20px | 11px |
| `--radius-2xl` | 28px | 14px |

`--radius-full` bleibt, damit Switch, Avatar und Chip rund bleiben.

**Mehr Rot beim Löschen.** Die Rose-Palette hatte einen Pinkstich (500 war
`#e42a4c`). Alle zehn Stufen sind auf ein satteres, reineres Rot gezogen
(500 jetzt `#e21f0c`). Das wirkt auf alles, was Gefahr signalisiert: den
Löschen-Button, das Papierkorb-Icon, Fehler-Toasts und Alerts. Kontrast bleibt
über AA: `--color-danger` auf Fläche 7.0:1 im Light, 7.0:1 im Dark.

**Keine Farbverläufe in Bedienelementen.** Betroffen sind Schaltflächen (auch
die Löschen-Variante), Switch, Schieberegler, Segmented Control, Menüeintrag,
Pagination, aktive Lasche, Meter und Stepper. Alle sind jetzt einfarbig. Auch
die dunkle Abstufung zur Unterkante in `--btn-img` ist weg, Tiefe kommt nur noch
aus Kante und Schatten. `--btn-grad` bleibt als Erweiterungspunkt und steht auf
`none`.

Verläufe behalten allein die nicht bedienbaren Flächen: Fortschrittsbalken
(auf Wunsch ausgenommen), Avatar, Icon-Kachel und die Demo-Bühne.

**Umschalter einheitlich.** Checkbox, Radio, Switch, Schieberegler, Segmented
Control und aktive Lasche zeigen jetzt alle auf `--color-accent`, flach und in
derselben Farbe. Vorher hatte der Switch einen Verlauf, die Checkbox über
`accent-color` eine Volltonfarbe, dadurch sahen gleichwertige Umschalter
unterschiedlich aus.

**Toast mit Rand rundherum.** Der farbige Rand lag nur an der Startkante
(`border-inline-start`). Er läuft jetzt in `--border-med` um die ganze Fläche,
in der Farbe des jeweiligen Zustands.

Nachgezogen: zwei Beschreibungen in `index.html`, die noch von Verläufen an
Schaltflächen und an der aktiven Lasche sprachen.

## v0.2.3 — Kantenregel verallgemeinert (2026-09-09)

Auf Rückmeldung: Die Glanz-Beispiele im Abschnitt „Glas" hatten unten und links
einen andersfarbigen Rahmen. Dieselbe Ursache wie in v0.2.1 Punkt 4, aber an einer
Stelle, die mein damaliger Fix nicht erfasst hat.

`.sg-box` liegt in `showcase.css` und hat einen Rahmen aus `--color-border`, der im
Dark-Theme halbtransparent ist (`weiß 12 %`). Der Verlauf scheint dadurch durch den
Rahmen hindurch, und weil `background-origin` auf `padding-box` stand, mit seiner
fortgesetzten Endfarbe: links die helle Startfarbe, unten die dunkle.

- Die Klassenliste aus v0.2.1 ist ersetzt durch eine Regel für alles:
  `*, *::before, *::after { background-origin: border-box; }` im base-Layer
- Eine Aufzählung von Klassen wäre dauerhaft unvollständig geblieben, denn der
  Effekt trifft jede Fläche mit Verlauf, auch jede später hinzukommende

## v0.2.2 — Dark-Theme in fremder Umgebung (2026-09-09)

Auf Rückmeldung: Im veröffentlichten Style-Guide blieb beim Umschalten auf Dunkel
fast alles hell. Lokal war das nicht zu sehen, und genau darin lag der Fehler
meiner Prüfung.

**Ursache: die Kaskade, nicht das Theme.** Deklarationen außerhalb aller `@layer`
schlagen jede gelayerte Deklaration, unabhängig von der Spezifität. Die Host-Seite
des Artifacts bringt einen eigenen Reset mit, der nicht in einem Layer steht. Sein
`body { background: #fafaf9; color: #1c1917 }` gewinnt deshalb gegen
`@layer base { body { background: var(--color-bg) } }`.

Die Tokens schalteten korrekt um (`--color-bg` war `#080d16`), aber der Grund blieb
`rgb(250,250,249)`. Weil die Glasflächen halbtransparent sind, zeigten sie diesen
hellen Grund, und die Seite wirkte fast vollständig hell, während Text und Toolbar
schon auf Dunkel standen.

- Die veröffentlichte Fassung bekommt einen bewusst **ungelayerten** Grundblock,
  der `html` und `body` aus den Tokens setzt, inklusive `color-scheme` je Theme
- `README.md` erklärt das unter „Einbau in eine Seite mit fremdem CSS", weil es
  jeden trifft, der den Baukasten in eine bestehende Anwendung einsetzt
- Am Projekt selbst musste nichts geändert werden: dort spielt kein fremdes CSS
  mit, deshalb war und ist das Dark-Theme lokal vollständig

**Lehre für die Prüfung.** Ich hatte nur die lokale Datei angesehen, nicht die
veröffentlichte Seite in ihrer echten Umgebung. Der Fehler war in der Vorschau
nicht sichtbar, weil dort der fremde Reset fehlt.

## v0.2.1 — Weiße Kanten entfernt (2026-09-09)

Auf Rückmeldung: Buttons, Karten und Icon-Kacheln trugen einen hellen Saum, der
oben und links sichtbar in die Form ragte. Zwei Ursachen, beide behoben.

**1. Die Lichtkante.** `box-shadow: inset 0 1px 0 var(--glass-highlight)` lag auf
fast jedem Element, und `--glass-highlight` war im Light-Theme 92 % Weiß. Bei
abgerundeten Ecken zieht sich diese Linie oben herum und in die Ecken hinein.

- 30 dieser Insets aus `components.css` (27) und `showcase.css` (3) entfernt
- `--glass-highlight`: Light 92 % → 60 %, Dark 26 % → 20 %. Es dient jetzt nur
  noch als Glanzfarbe für Fortschrittsbalken, Streifen und Hintergrundmuster
- `--glass-edge`: Light 75 % → 48 %

**2. Der Glanzverlauf.** `--glass-sheen` lag als oberste Hintergrundebene auf
17 Komponenten, mit 55 % Weiß am Start und einem harten Abbruch bei 60 %. Auf
einem 26 px hohen Button deckt das die obere Hälfte ab und liest sich als weißer
Rand. Weil es ein Winkel-Verlauf war (`165deg`), drehte er sich zusätzlich mit dem
Seitenverhältnis: auf der breiten Toolbar kamen 79 % der Verlaufsachse aus der
Breite, der Glanz lief dort also quer und schnitt mit sichtbarer Kante durch.

- Glanz aus allen 16 kompakten Bedienelementen entfernt (Button, Badge, Chip,
  Switch, Range, Alert, Segmented, Tabellenkopf, Menü, Accordion, Pagination,
  Empty State, Tooltip, Kbd). Er liegt jetzt nur noch auf den großen Glasflächen
- `--glass-sheen` neu: `to bottom` statt `165deg`, damit er sich nicht mehr mit
  dem Seitenverhältnis dreht, 22 % statt 55 % Weiß, und weiches Auslaufen bis
  85 % statt Abbruch bei 60 %
- `.icon-tile` hat keinen hellen Rand mehr, der Farbverlauf trägt die Form allein

**3. Der Rahmen.** Auf weitere Rückmeldung (App-Icon im Header, Theme-Umschalter,
Schieberegler): `--glass-edge` war ein weißer Rand mit 48 % Deckkraft und lag über
die `.glass`-Familie auf Toolbar, Menü, Modal, Toast, Glas-Karte und
`.btn--glass`.

- `--glass-edge`: Light von 48 % Weiß auf eine neutrale Linie
  (`slate-500` mit 22 %), Dark von 14 % auf 9 % Weiß. Die Kante definiert die
  Form weiterhin, leuchtet aber nicht mehr
- `.icon-tile` aus der Glanz-Ebene genommen: die Kachel ist jetzt reiner
  Farbverlauf, ohne aufgesetzte helle Oberkante

**4. Der Kanteneffekt.** Nach zwei weiteren Beispielen (App-Icon mit hellem Saum
oben, Button mit dunklem Rand links) zeigte ein Ausschlusstest die eigentliche
Ursache, die kein gezeichneter Rand war: `background-origin` steht standardmäßig
auf `padding-box`. Ein Verlauf wird dadurch nur über die padding-box aufgespannt
und im Bereich des Rahmens mit seiner jeweiligen Endfarbe fortgesetzt. Bei einem
transparenten 1px-Rahmen, wie ihn `.btn--primary` und die Icon-Kachel haben, ist
dieser eine Pixel deshalb heller oder dunkler als die Fläche daneben.

Das erklärt beide Beobachtungen mit einer Ursache: Bei der Kachel läuft der
Verlauf von azure-300 (hell) nach azure-600, oben entsteht also ein heller Saum.
Beim Button liegt unter dem hellen Verlaufsanfang die dunklere Grundfarbe, links
entsteht also ein dunkler.

- `background-origin: border-box` für alle Komponenten mit Verlauf (Button, Badge,
  Chip, Icon-Kachel, Switch, Fortschritt, Segmented, Pagination, Meter, Avatar,
  Tag-Dot, Stepper, Toast, Alert)
- Maße und sichtbare Rahmen bleiben unverändert. `border: none` hätte es auch
  behoben, aber den Rahmen des Standard-Buttons mitgenommen

**Dokumentation nachgezogen.** `index.html`, `README.md` und die CSS-Kommentare
beschrieben die Lichtkante noch als „den eigentlichen Vista-Effekt". Alle acht
Stellen sagen jetzt, was das System wirklich tut.

**Nebenbefund behoben.** Ein `data-theme` auf einem Teilbaum (etwa ein dunkler
Abschnitt in einer hellen Seite) tauschte nur die Tokens. Die vom `body` bereits
geerbte `color` blieb stehen, dadurch stand dunkler Text auf dunklem Grund. Eine
Regel `[data-theme] { color: var(--color-text); }` im base-Layer behebt das.

## v0.2 — Theme "Aero Plasma" (2026-09-09)

Der Umbau vom violett-indigo Standard-Theme auf Aero Plasma: Glasoptik nach
Windows Vista und Windows 7, modern gelesen, mit vier Markentönen und farbfähigen
Icons. Alle neun Bestandsdateien wurden angefasst, zwei kamen dazu.

### tokens.css — die Grundlage, komplett neu

Vorher 68 Tokens in zwei Paletten, jetzt 185 Tokens in sechs.

**Paletten ersetzt.** `--urb-neutral-*` heißt jetzt `--urb-slate-*` und ist kühler
und blaustichiger. `--urb-accent-*` ist aufgelöst in vier gleichrangige Familien,
jede mit den Stufen 50 bis 900:

| Palette | Rolle | Beispiel 600 |
|---|---|---|
| `--urb-azure-*` | helles Blau, Primärakzent | `#036bc7` |
| `--urb-indigo-*` | Lila-Indigo, Verlaufspartner | `#6039db` |
| `--urb-amber-*` | Orange-Gelb | `#c06f02` |
| `--urb-jade-*` | dunkles Grün | `#0a6a48` |
| `--urb-rose-*` | Rot für Fehler | `#c11739` |
| `--urb-slate-*` | Neutral, 50 bis 950 | `#43536b` |

**Neu hinzugekommen:**

- **Glas-Rollen** (Zeile 178 ff. und 296 ff.): `--glass-blur`, `--glass-blur-strong`,
  `--glass-saturate`, `--glass-tint`, `--glass-tint-strong`, `--glass-tint-sunken`,
  `--glass-edge`, `--glass-highlight`, `--glass-lowlight`, `--glass-sheen`,
  `--glass-noise-opacity`, `--glass-glow`, dazu `--urb-noise` als Rauschmuster.
- **Markentöne** `--tone-{azure|indigo|amber|jade|rose|slate}` mit je `-soft`,
  `-line` und `-grad`. Das ist die bunte Klaviatur für Icons und Kategorien.
- **Verläufe** `--gradient-accent`, `--gradient-warm`, `--gradient-cool`.
- **Ebenen-Skala** `--z-base` bis `--z-tooltip`. Vorher gab es keine.
- `--color-surface-3`, `--color-accent-line`, `--color-*-line` je Statusfarbe.
- `--radius-2xl`, `--border-med`, `--dur-slow`, `--ease-out`,
  `--tracking-tight`, `--tracking-wide`.
- **Breakpoint-Konvention** als Kommentar (Zeile 188 ff.), weil CSS-Variablen in
  Media Queries nicht wirken.
- **`prefers-reduced-motion`** ganz am Ende: setzt die drei `--dur-*` auf 1ms.
  Damit hält jede Komponente still, die diese Tokens benutzt, ohne eigenen Code.

**Rohwerte in der semantischen Ebene beseitigt.** Vorher zeigten `--color-surface`,
`--color-on-accent`, alle `*-soft` im Light und alle Statusfarben im Dark auf keinen
Primitiv, sondern trugen direkt einen Hex-Wert. Jetzt gibt es `--urb-white` und
`--urb-black`, und jede weiche Fläche entsteht per `color-mix` aus einem Primitiv.

**Kontrast nachgebessert** (nach deiner Meldung zu den Sekundärtexten):

| Token | Theme | vorher | nachher | Kontrast vorher → nachher |
|---|---|---|---|---|
| `--color-text-secondary` | Light | slate-600 | slate-700 | 6.8 → 9.4:1 |
| `--color-text-muted` | Light | slate-400 | slate-600 | 2.6 → 6.8:1 |
| `--color-text-secondary` | Dark | slate-300 | slate-200 | 11.0 → 14.4:1 |
| `--color-text-muted` | Dark | slate-400 | slate-300 | 6.4 → 11.0:1 |
| `--glass-tint` | Light | 62 % | 78 % | auf Glas 3.1 → 9.0:1 |
| `--glass-tint` | Dark | 55 % | 76 % | auf Glas 2.0 → 5.0:1 |
| `--glass-tint-strong` | beide | 80 / 78 % | 90 % | Dialoge |
| `--glass-tint-sunken` | beide | 38 / 45 % | 58 / 62 % | Eingabefelder |

Der zweite Block war die eigentliche Ursache: der Tint war zu dünn, um den
Untergrund zu neutralisieren, deshalb schlug ein farbiger Hintergrund durch die
Glasfläche und löschte das Grau darauf aus.

### components.css — neu geschrieben

Von 350 auf 1330 Zeilen. Alle bisherigen Komponenten sind erhalten und auf Aero
umgebaut, dazu kamen die Lücken, die ein Design-System üblicherweise füllt.

**Neues Fundament `.glass`.** Backdrop-Filter mit Sättigung, halbtransparenter
Tint, Lichtkante oben und Schattenkante unten als Inset-Schatten, Glanzverlauf als
`::before`, Körnung als `::after`. Karte, Toolbar, Menü, Modal, Toast und
`.btn--glass` hängen über eine gemeinsame `:is()`-Regel daran und stellen nur ihre
lokalen Variablen um. Varianten `--strong`, `--sunken`, `--glow`, plus `.sheen`
als Helfer.

**Neue Komponenten:** Toast und Toast-Stack, Menü, Accordion, Pagination, Skeleton,
Empty State, Stepper, Segmented Control, Toolbar, Meter, Tag-Dot, Modal-Backdrop.

**Neue Layout-Primitive** (waren vorher nur in der Demo, nicht im System):
`.container`, `.stack`, `.cluster`, `.grid-auto`, `.spread`.

**Icons als Komponente ausgebaut:** Größenklassen, elf Tönungsklassen,
`.icon--duo`, acht `.icon--grad-*`, und `.icon-tile` als farbige Glaskachel.

**Robustheit:** jedes `backdrop-filter` mit `-webkit-`-Präfix, ein
`@supports not`-Block setzt alle Glasflächen auf deckende Farben, wo der Browser
keine Unschärfe kann, und alle fünf Animationen mit fester Dauer stehen im
`prefers-reduced-motion`-Block still.

**Harte Farben entfernt.** Vorher standen `#fff` in `.btn--danger` und im
Switch-Knopf. Beide zeigen jetzt auf Tokens.

### index.html — neu gebaut

15 Abschnitte statt 12, jeder mit deutscher Kurzerklärung: Farben, Typografie,
Skalen, **Glas**, Buttons, Formular, Marker, Hinweise und **Toasts**, Karten und
**Toolbar**, Tabs mit **Segmented, Menü, Accordion**, Tabelle mit **Pagination,
Breadcrumb, Stepper**, Fortschritt mit **Meter, Skeleton, Empty State**, Dialog und
**Tooltip**, **Icons in allen fünf Darstellungsarten**, Code und Kbd.

Kopfzeile ist jetzt eine klebende Glas-Toolbar mit Sprungnavigation. Das
Icon-Sprite ist inline eingebettet (101 Symbole, acht Verläufe), weil `<use>` und
`url(#urb-grad-*)` nur im selben Dokument auflösen. Alle Textzeichen als Symbol
(das alte `✕` in den Chips) sind durch echte Icons ersetzt.

### showcase.css — neu gebaut

Aero-Hintergrund als eigene fixe Ebene: vier weiche Farbblobs (Azure, Indigo,
Amber, Jade) mit 45 % Deckkraft im Light und 34 % im Dark, sehr langsam bewegt,
dazu ein Lichtmuster. Ohne diesen Hintergrund wäre kein Glaseffekt zu sehen.
Eigener `prefers-reduced-motion`-Riegel für die Keyframes.

### icons.svg — farbfähig gemacht

Die 101 Symbole sind inhaltlich unverändert. Geändert hat sich, wie sie Farbe
annehmen:

- `stroke="currentColor"` → `stroke="var(--icon-stroke, currentColor)"`
- `fill="none"` → `fill="var(--icon-fill, none)"`
- acht `<linearGradient>` in `<defs>` mit den IDs `urb-grad-azure`, `-indigo`,
  `-amber`, `-jade`, `-rose`, `-accent`, `-warm`, `-cool`
- jedes Symbol trägt zusätzlich zu `data-cat` jetzt ein `data-tone`
- das Wurzel-SVG steht auf `position:absolute;width:0;height:0` statt
  `display:none`, sonst lösen die Verläufe als Paint-Server nicht zuverlässig auf

### icons.html und icons.css

Übersicht neu im Aero-Stil, mit Umschalter für die fünf Darstellungsarten,
Kategoriefilter, Suche, Größenregler, Theme-Umschalter und Klick-zum-Kopieren
inklusive passender Farbklasse. Eigene Layoutklassen tragen jetzt das Präfix
`ic-`, damit `.icon-tile` für die Komponente frei bleibt.

### theme.js

- folgt der System-Einstellung auch nachträglich, solange keine eigene Wahl
  gespeichert ist (`matchMedia`-Listener)
- übersteht blockierten `localStorage` (privater Modus) ohne Fehler
- zieht die Beschriftung bei `DOMContentLoaded` nach, dadurch kann das Skript im
  `<head>` stehen und das Theme steht vor dem ersten Bild
- der Einbau-Hinweis im Kopfkommentar enthält kein schließendes Script-Tag mehr:
  das hätte beim Inline-Einbetten der Datei den umgebenden Script-Block beendet

### Neu: pruefen.py

Selbstprüfung ohne Abhängigkeiten, `python3 pruefen.py`. Prüft CSS-Syntax, die
eiserne Regel (kein `--urb-*` und kein roher Farbwert außerhalb `tokens.css`),
ob jedes benutzte Token definiert ist oder einen Fallback hat, ob das Sprite in
`index.html` auf dem Stand von `icons.svg` ist, und rechnet alle WCAG-Kontraste
je Theme aus, auch für Glasflächen über den Hintergrundfarben.

### Neu: .claude/launch.json

Startet einen lokalen Server auf Port 8348 für die Vorschau. `icons.html` braucht
ihn, weil sie das Sprite per `fetch` lädt.

### Was bewusst nicht geändert wurde

Kein Build-Schritt, keine Abhängigkeiten, keine JSON-Tokens, kein Paket. Alle
Werte stehen weiterhin direkt lesbar im CSS, damit die Vorlage ohne Werkzeug
verständlich bleibt.
