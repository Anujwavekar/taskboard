import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api, getToken, setToken, setUnauthorizedHandler } from "../api/client";

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  // loading | authed | guest | error
  const [status, setStatus] = useState(getToken() ? "loading" : "guest");

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    setStatus("guest");
  }, []);

  const checkSession = useCallback(async () => {
    if (!getToken()) {
      setStatus("guest");
      return;
    }
    setStatus("loading");
    try {
      setUser(await api("/api/auth/me"));
      setStatus("authed");
    } catch (err) {
      if (err.status === 401) logout();
      else setStatus("error");
    }
  }, [logout]);

  useEffect(() => {
    setUnauthorizedHandler(logout);
    checkSession();
  }, [logout, checkSession]);

  async function authenticate(path, body) {
    const data = await api(path, { method: "POST", body, auth: false });
    setToken(data.access_token);
    setUser(data.user);
    setStatus("authed");
  }

  const login = (email, password) => authenticate("/api/auth/login", { email, password });
  const signup = (name, email, password) =>
    authenticate("/api/auth/signup", { name, email, password });

  return (
    <AuthContext.Provider value={{ user, status, login, signup, logout, retry: checkSession }}>
      {children}
    </AuthContext.Provider>
  );
}