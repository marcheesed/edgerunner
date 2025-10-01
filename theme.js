function calculateSettingAsThemeString({ localStorageTheme, systemSettingDark }) {
  if (localStorageTheme !== null) {
    return localStorageTheme;
  }
  if (systemSettingDark.matches) {
    return "dark";
  }
  return "light";
}

// Get system preference + saved theme
const localStorageTheme = localStorage.getItem("theme");
const systemSettingDark = window.matchMedia("(prefers-color-scheme: dark)");

let currentThemeSetting = calculateSettingAsThemeString({ localStorageTheme, systemSettingDark });

// Apply initial theme
document.querySelector("html").setAttribute("data-theme", currentThemeSetting);

// Update button text
const button = document.querySelector("[data-theme-toggle]");
button.innerText = currentThemeSetting === "dark" ? "turn on background gif" : "turn off background gif";
button.setAttribute("aria-label", button.innerText);

// Handle click
button.addEventListener("click", () => {
  const newTheme = currentThemeSetting === "dark" ? "light" : "dark";

  const newCta = newTheme === "dark" ? "turn on background gif" : "turn off background gif";
  button.innerText = newCta;
  button.setAttribute("aria-label", newCta);

  document.querySelector("html").setAttribute("data-theme", newTheme);
  localStorage.setItem("theme", newTheme);
  currentThemeSetting = newTheme;
});