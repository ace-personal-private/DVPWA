import { apiFetch } from "./client";
import type { Transaction } from "./types";

export function deposit(amount: number): Promise<Transaction> {
  return apiFetch<Transaction>("/api/wallet/deposit", { method: "POST", body: { amount } });
}

export function withdraw(amount: number): Promise<Transaction> {
  return apiFetch<Transaction>("/api/wallet/withdraw", { method: "POST", body: { amount } });
}

export function listMyTransactions(): Promise<Transaction[]> {
  return apiFetch<Transaction[]>("/api/wallet/transactions");
}
