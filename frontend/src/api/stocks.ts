import { apiFetch } from "./client";
import type { Stock } from "./types";

export function listStocks(search?: string): Promise<Stock[]> {
  const query = search ? `?search=${encodeURIComponent(search)}` : "";
  return apiFetch<Stock[]>(`/api/stocks${query}`);
}

export function getStock(id: number): Promise<Stock> {
  return apiFetch<Stock>(`/api/stocks/${id}`);
}
