import { apiFetch } from "./client";
import type { SupportTicket } from "./types";

export function createTicket(subject: string, message: string): Promise<SupportTicket> {
  return apiFetch<SupportTicket>("/api/support/tickets", {
    method: "POST",
    body: { subject, message },
  });
}

export function listMyTickets(): Promise<SupportTicket[]> {
  return apiFetch<SupportTicket[]>("/api/support/tickets");
}
