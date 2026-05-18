import { createContext, useContext, useEffect, useState } from "react";

const ThemeContext = createContext();

export const LIGHT_THEME = "light";
export const DARK_THEME = "dark";

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    const stored = localStorage.getItem("peeky-theme");
    return stored === LIGHT_THEME ? LIGHT_THEME : DARK_THEME;
  });

  useEffect(() => {
    const root = document.documentElement;
    if (theme === LIGHT_THEME) {
      root.classList.add("light-theme");
    } else {
      root.classList.remove("light-theme");
    }
    localStorage.setItem("peeky-theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === LIGHT_THEME ? DARK_THEME : LIGHT_THEME));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within ThemeProvider");
  }
  return context;
};