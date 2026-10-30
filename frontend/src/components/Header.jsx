import { useState } from "react";
import { useAuth } from "../context/AuthContext";

export default function Header() {
  const { user, logout } = useAuth();
  const [theme, setTheme] = useState(document.documentElement.dataset.theme);

  function toggleTheme() {
    const next = theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    localStorage.setItem("theme", next);
    setTheme(next);
  }

  return (
    <header className="header">
      <div className="header-inner">
        <span className="logo">TaskBoard</span>
        <div className="header-right">
          <span className="greeting">Hi, {user.name}</span>
          <button className="icon-btn" onClick={toggleTheme} aria-label="Toggle dark mode">
            {theme === "dark" ? "☀️" : "🌙"}
          </button>
          <button className="btn btn-ghost" onClick={logout}>
            Log out
          </button>
        </div>
      </div>
    </header>
  );
}