/* ============================================================
   Theme-Umschaltung
   Setzt data-theme am <html>-Element und merkt sich die Wahl.
   Ohne eigene Wahl folgt die Seite der System-Einstellung und
   wechselt mit, wenn das System umschaltet.

   Einbau: ein script-Element mit src="theme.js" im <head>, ohne defer.
   (Hier bewusst ohne echtes Tag geschrieben: ein schliessendes
    script-Tag im Kommentar wuerde beim Inline-Einbetten dieser
    Datei den umgebenden Script-Block vorzeitig beenden.)
   Dann steht das Theme, bevor das erste Bild gezeichnet wird.

   Schalter im HTML:
     <button class="btn btn--glass" data-theme-toggle></button>
   Beschriftung und Icon setzt dieses Skript selbst.
   ============================================================ */
(function () {
  "use strict";

  var root = document.documentElement;
  var KEY = "urb-theme";
  var media = window.matchMedia("(prefers-color-scheme: dark)");

  function stored() {
    try {
      return localStorage.getItem(KEY);
    } catch (e) {
      // Privater Modus oder blockierter Speicher: dann eben ohne Gedaechtnis.
      return null;
    }
  }

  function remember(theme) {
    try {
      localStorage.setItem(KEY, theme);
    } catch (e) {
      /* absichtlich still */
    }
  }

  function systemPref() {
    return media.matches ? "dark" : "light";
  }

  function paintToggle(theme) {
    var btn = document.querySelector("[data-theme-toggle]");
    if (!btn) return;

    // Gezeigt wird, wohin der Klick fuehrt: im hellen Theme der Mond.
    var icon = theme === "dark" ? "sun" : "moon";
    var label = theme === "dark" ? "Hell" : "Dunkel";
    var title = theme === "dark" ? "Zu hellem Design wechseln" : "Zu dunklem Design wechseln";

    btn.innerHTML =
      '<svg class="icon icon--sm" aria-hidden="true"><use href="#' + icon + '"></use></svg>' +
      "<span>" + label + "</span>";
    btn.setAttribute("aria-label", title);
    btn.setAttribute("title", title);
  }

  function apply(theme) {
    root.setAttribute("data-theme", theme);
    paintToggle(theme);
  }

  // Startzustand: gespeicherte Wahl schlaegt System-Einstellung.
  apply(stored() || systemPref());

  // Solange der Nutzer nicht selbst gewaehlt hat, dem System folgen.
  media.addEventListener("change", function () {
    if (!stored()) apply(systemPref());
  });

  // Der Schalter kann spaeter im DOM auftauchen, deshalb Klick am Dokument.
  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-theme-toggle]");
    if (!btn) return;
    var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    remember(next);
    apply(next);
  });

  // Beschriftung nachziehen, sobald das Dokument steht (Schalter kommt nach dem <head>).
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      paintToggle(root.getAttribute("data-theme"));
    });
  }
})();
