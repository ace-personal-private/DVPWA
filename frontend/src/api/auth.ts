import { apiFetch } from "./client";
import type { TokenResponse } from "./types";

export function register(
  email: string,
  username: string,
  password: string,
): Promise<TokenResponse> {
  return apiFetch<TokenResponse>("/api/auth/register", {
    method: "POST",
    body: { email, username, password },
    skipAuth: true,
  });
}

export function login(email: string, password: string): Promise<TokenResponse> {
  return apiFetch<TokenResponse>("/api/auth/login", {
    method: "POST",
    body: { email, password },
    skipAuth: true,
  });
}

export function forgotPassword(email: string): Promise<{ detail: string; reset_token?: string }> {
  return apiFetch("/api/auth/forgot-password", {
    method: "POST",
    body: { email },
    skipAuth: true,
  });
}

export function resetPassword(token: string, newPassword: string): Promise<{ detail: string }> {
  return apiFetch("/api/auth/reset-password", {
    method: "POST",
    body: { token, new_password: newPassword },
    skipAuth: true,
  });
}
