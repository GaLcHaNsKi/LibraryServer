(() => {
    const storageKey = "library-site-theme";
    const root = document.documentElement;
    const toggle = document.querySelector(".theme-toggle");
    const icon = toggle?.querySelector(".theme-icon");
    const systemTheme = window.matchMedia("(prefers-color-scheme: dark)");

    const savedTheme = localStorage.getItem(storageKey);
    let theme = savedTheme === "light" || savedTheme === "dark"
        ? savedTheme
        : (systemTheme.matches ? "dark" : "light");

    function updateThemeImages() {
        document.querySelectorAll("[data-theme-image]").forEach((image) => {
            const source = theme === "dark" ? image.dataset.darkSrc : image.dataset.lightSrc;
            if (source && image.getAttribute("src") !== source) image.setAttribute("src", source);
        });
    }

    function applyTheme(nextTheme, saveChoice = false) {
        theme = nextTheme;
        root.dataset.theme = theme;
        if (saveChoice) localStorage.setItem(storageKey, theme);
        if (toggle) toggle.setAttribute("aria-label", theme === "dark" ? "Включить светлую тему" : "Включить тёмную тему");
        if (icon) icon.textContent = theme === "dark" ? "☀️" : "🌙";
        updateThemeImages();
    }

    applyTheme(theme);
    toggle?.addEventListener("click", () => applyTheme(theme === "dark" ? "light" : "dark", true));
    systemTheme.addEventListener("change", (event) => {
        if (!localStorage.getItem(storageKey)) applyTheme(event.matches ? "dark" : "light");
    });
})();
