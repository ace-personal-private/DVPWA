import { apiFetch } from "./client";
import type { Order } from "./types";

export function placeOrder(
  stockId: number,
  side: "buy" | "sell",
  quantity: number,
  price: number,
): Promise<Order> {
  return apiFetch<Order>("/api/orders", {
    method: "POST",
    body: { stock_id: stockId, side, quantity, price },
  });
}

export function listMyOrders(): Promise<Order[]> {
  return apiFetch<Order[]>("/api/orders");
}

export function getOrder(id: number): Promise<Order> {
  return apiFetch<Order>(`/api/orders/${id}`);
}

export function cancelOrder(id: number): Promise<{ detail: string }> {
  return apiFetch(`/api/orders/${id}`, { method: "DELETE" });
}
