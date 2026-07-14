# Claude Design System

Ein token-basierter Baukasten (Style-Guide) mit Light- und Dark-Theme,
violett-indigo Akzent und leicht glasigen Flächen.

## Öffnen

`index.html` im Browser öffnen. Der Umschalter oben rechts wechselt zwischen
hellem und dunklem Theme; die Wahl wird im Browser gespeichert.

## Aufbau

Die Dateien sind bewusst getrennt, damit Tokens, Komponenten und Demo nicht
vermischen:

| Datei | Zweck |
|---|---|
| `tokens.css` | Design-Tokens in zwei Stufen: **Primitive** (Rohwerte der Palette) und **semantische** Tokens (Rollen wie `--color-accent`). Light und Dark. |
| `components.css` | Wiederverwendbare Komponenten (Button, Feld, Karte, Alert …). Nutzen ausschließlich semantische Tokens. |
| `showcase.css` | Nur Layout dieser Demo-Seite (Raster, Farbfelder, Skalen). Nicht Teil des Systems. |
| `index.html` | Die Baukasten-Seite mit allen Elementen. |
| `theme.js` | Theme-Umschaltung (`data-theme` am `<html>`). |

## Das Prinzip: zwei Token-Stufen

```
Komponente  →  benutzt nur  →  semantisches Token  →  zeigt auf  →  Primitiv
Button.css       var(--color-accent)     --color-accent: var(--urb-accent-600)   #5f43e0
```

Ein Theme ändert nur die semantische Stufe. Kein Komponentencode wird angefasst,
ein Theme-Wechsel wirkt überall gleichzeitig.

## Reihenfolge der Stylesheets

Wichtig ist die Ladereihenfolge über CSS-Layer:

```
@layer tokens, base, components, showcase;
```

Damit ist die Rangfolge einmal festgelegt; spätere Overrides gewinnen ohne
`!important`.

## Anpassen

- **Akzentfarbe ändern:** in `tokens.css` die `--urb-accent-*`-Werte tauschen.
- **Radien/Abstände:** die `--radius-*` bzw. `--space-*` in `tokens.css`.
- **Neues Theme:** einen Block `[data-theme="name"] { … }` mit eigenen
  semantischen Werten ergänzen.

## Übernahme in urbBase

Für urbBase gehören `tokens.css` (aufgeteilt in `primitives.css` und
`semantic.css`) und die Komponenten nach `shell-ui/src/theming/`. Die Demo-Seite
und `showcase.css` bleiben ein reines Referenzdokument.
