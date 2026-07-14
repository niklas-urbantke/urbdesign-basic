// Theme-Umschaltung: setzt data-theme am <html>-Element und merkt
// sich die Wahl im localStorage. Ohne Wahl folgt es der System-Einstellung.
(function () {
  const root = document.documentElement;
  const KEY = "urb-theme";

  function systemPref() {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function apply(theme) {
    root.setAttribute("data-theme", theme);
    const btn = document.querySelector("[data-theme-toggle]");
    if (btn) {
      // Icon (Mond im hellen, Sonne im dunklen Modus) plus Textlabel.
      var icon = theme === "dark" ? "sun" : "moon";
      var label = theme === "dark" ? "Hell" : "Dunkel";
      btn.innerHTML = '<svg class="icon" style="--icon-size:18px" aria-hidden="true"><use href="#' + icon + '"></use></svg>' + label;
      btn.setAttribute("aria-label", theme === "dark" ? "Zu hellem Design wechseln" : "Zu dunklem Design wechseln");
    }
  }

  // Initialer Zustand
  apply(localStorage.getItem(KEY) || systemPref());

  document.addEventListener("click", function (e) {
    const btn = e.target.closest("[data-theme-toggle]");
    if (!btn) return;
    const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    localStorage.setItem(KEY, next);
    apply(next);
  });
})();
