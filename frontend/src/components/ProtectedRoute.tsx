import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <p>Loading...</p>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

// Cosmetic UI gate only -- hides the nav link / redirects away in the UI.
// It is NOT the real security boundary; every admin endpoint must enforce
// its own access control server-side regardless of what this shows/hides.
export function AdminRoute({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <p>Loading...</p>;
  if (!user || user.role !== "admin") return <Navigate to="/" replace />;
  return <>{children}</>;
}
