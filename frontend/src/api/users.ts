import { apiFetch } from "./client";
import type { User } from "./types";

export function getMe(): Promise<User> {
  return apiFetch<User>("/api/users/me");
}

export function updateMe(fields: Record<string, unknown>): Promise<User> {
  return apiFetch<User>("/api/users/me", { method: "PATCH", body: fields });
}

export function uploadAvatar(file: File): Promise<{ avatar_path: string }> {
  const form = new FormData();
  form.append("file", file);
  return apiFetch("/api/users/me/avatar", { method: "POST", body: form, isFormData: true });
}
