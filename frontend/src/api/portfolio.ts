import { apiFetch } from "./client";
import type { Holding } from "./types";

export function getPortfolio(userId: number): Promise<Holding[]> {
  return apiFetch<Holding[]>(`/api/portfolio/${userId}`);
}

export function exportBackup(): Promise<{ backup: string }> {
  return apiFetch("/api/portfolio/export/backup");
}

export function importBackup(data: string): Promise<{ detail: string }> {
  return apiFetch("/api/portfolio/import/backup", { method: "POST", body: { data } });
}
