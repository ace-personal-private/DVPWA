import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { clearTokens, getAccessToken, setTokens } from "../api/client";
import { login as apiLogin, register as apiRegister } from "../api/auth";
import { getMe } from "../api/users";
import type { User } from "../api/types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    if (!getAccessToken()) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const me = await getMe();
      setUser(me);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  async function login(email: string, password: string) {
    const tokens = await apiLogin(email, password);
    setTokens(tokens.access_token, tokens.refresh_token);
    await refreshUser();
  }

  async function register(email: string, username: string, password: string) {
    const tokens = await apiRegister(email, username, password);
    setTokens(tokens.access_token, tokens.refresh_token);
    await refreshUser();
  }

  function logout() {
    clearTokens();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
