export const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

// VULN: tokens live in localStorage (not an httpOnly cookie), which is what
// makes the stored-XSS chain (support ticket -> admin viewer) able to steal
// an admin session by reading these keys from JS.
const ACCESS_TOKEN_KEY = "stonksco_access_token";
const REFRESH_TOKEN_KEY = "stonksco_refresh_token";

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setTokens(accessToken: string, refreshToken: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

class ApiError extends Error {
  status: number;
  body: unknown;

  constructor(status: number, body: unknown) {
    super(
      typeof body === "object" && body && "detail" in body
        ? String((body as { detail: unknown }).detail)
        : `Request failed (${status})`,
    );
    this.status = status;
    this.body = body;
  }
}

async function tryRefresh(): Promise<boolean> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return false;

  const res = await fetch(`${API_BASE}/api/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  if (!res.ok) return false;

  const data = await res.json();
  setTokens(data.access_token, data.refresh_token);
  return true;
}

export async function apiFetch<T>(
  path: string,
  options: { method?: string; body?: unknown; skipAuth?: boolean; isFormData?: boolean } = {},
): Promise<T> {
  const { method = "GET", body, skipAuth = false, isFormData = false } = options;

  const headers: Record<string, string> = {};
  if (!isFormData) headers["Content-Type"] = "application/json";
  const token = getAccessToken();
  if (!skipAuth && token) headers.Authorization = `Bearer ${token}`;

  const doFetch = () =>
    fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : isFormData ? (body as FormData) : JSON.stringify(body),
    });

  let res = await doFetch();

  if (res.status === 401 && !skipAuth) {
    const refreshed = await tryRefresh();
    if (refreshed) {
      headers.Authorization = `Bearer ${getAccessToken()}`;
      res = await doFetch();
    }
  }

  if (!res.ok) {
    const errBody = await res.json().catch(() => ({}));
    throw new ApiError(res.status, errBody);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}
