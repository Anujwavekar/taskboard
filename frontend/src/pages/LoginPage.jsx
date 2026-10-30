import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { LoadingState } from "../components/States";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function LoginPage() {
  const { status, login, signup } = useAuth();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // Quietly wake the free server while the user types
  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_URL}/api/health`).catch(() => {});
  }, []);

  if (status === "loading") return <LoadingState label="Checking your session…" />;
  if (status === "authed") return <Navigate to="/tasks" replace />;

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  function switchMode(next) {
    setMode(next);
    setErrors({});
    setFormError("");
  }

  function validate() {
    const e = {};
    if (mode === "signup" && !form.name.trim()) e.name = "Name is required";
    if (!EMAIL_RE.test(form.email.trim())) e.email = "Enter a valid email address";
    if (form.password.length < 8) e.password = "Password must be at least 8 characters";
    return e;
  }

  async function onSubmit(ev) {
    ev.preventDefault();
    setFormError("");
    const e = validate();
    setErrors(e);
    if (Object.keys(e).length) return;

    setSubmitting(true);
    try {
      if (mode === "login") await login(form.email.trim(), form.password);
      else await signup(form.name.trim(), form.email.trim(), form.password);
      // on success the status becomes "authed" and the redirect above runs
    } catch (err) {
      const fieldErrors = err.errors || {};
      setErrors(fieldErrors);
      setFormError(Object.keys(fieldErrors).length ? "" : err.message);
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-wrap">
      <form className="auth-card" onSubmit={onSubmit} noValidate>
        <h1 className="logo center">TaskBoard</h1>

        <div className="tabs auth-tabs">
          <button type="button" className={`tab ${mode === "login" ? "active" : ""}`} onClick={() => switchMode("login")}>
            Log in
          </button>
          <button type="button" className={`tab ${mode === "signup" ? "active" : ""}`} onClick={() => switchMode("signup")}>
            Sign up
          </button>
        </div>

        {mode === "signup" && (
          <div className="field">
            <label htmlFor="name">Name</label>
            <input id="name" className={`input ${errors.name ? "invalid" : ""}`} value={form.name} onChange={set("name")} autoComplete="name" />
            {errors.name && <div className="error-text">{errors.name}</div>}
          </div>
        )}

        <div className="field">
          <label htmlFor="email">Email</label>
          <input id="email" type="email" className={`input ${errors.email ? "invalid" : ""}`} value={form.email} onChange={set("email")} autoComplete="email" />
          {errors.email && <div className="error-text">{errors.email}</div>}
        </div>

        <div className="field">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            className={`input ${errors.password ? "invalid" : ""}`}
            value={form.password}
            onChange={set("password")}
            autoComplete={mode === "login" ? "current-password" : "new-password"}
          />
          {errors.password && <div className="error-text">{errors.password}</div>}
        </div>

        {formError && <div className="error-text form-error">{formError}</div>}

        <button type="submit" className="btn btn-primary full" disabled={submitting}>
          {submitting ? "Please wait…" : mode === "login" ? "Log in" : "Create account"}
        </button>
        {submitting && (
          <p className="muted small center">The server may take up to a minute to wake up.</p>
        )}
      </form>
    </div>
  );
}