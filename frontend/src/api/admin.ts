import { apiFetch } from "./client";
import type { Stock, SupportTicket, User } from "./types";

export function listUsers(): Promise<User[]> {
  return apiFetch<User[]>("/api/admin/users");
}

export function listAllTickets(): Promise<SupportTicket[]> {
  return apiFetch<SupportTicket[]>("/api/admin/support/tickets");
}

export function setStockLogo(stockId: number, logoUrl: string): Promise<Stock> {
  return apiFetch<Stock>(`/api/admin/stocks/${stockId}/logo`, {
    method: "PUT",
    body: { logo_url: logoUrl },
  });
}

export function generateReport(
  ticker: string,
): Promise<{ ticker: string; output: string; error: string }> {
  return apiFetch(`/api/admin/reports/${encodeURIComponent(ticker)}`, { method: "POST" });
}
