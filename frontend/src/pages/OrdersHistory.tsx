import { useEffect, useState } from "react";
import { cancelOrder, listMyOrders } from "../api/orders";
import type { Order } from "../api/types";

export function OrdersHistory() {
  const [orders, setOrders] = useState<Order[]>([]);

  function load() {
    listMyOrders().then(setOrders);
  }

  useEffect(load, []);

  async function handleCancel(id: number) {
    await cancelOrder(id);
    load();
  }

  return (
    <div>
      <h1>Order history</h1>
      {orders.length === 0 ? (
        <p>No orders yet.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Side</th>
              <th>Stock</th>
              <th>Qty</th>
              <th>Price</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.id}>
                <td>{o.id}</td>
                <td>{o.side}</td>
                <td>#{o.stock_id}</td>
                <td>{o.quantity}</td>
                <td>${o.price.toFixed(2)}</td>
                <td>{o.status}</td>
                <td>
                  <button onClick={() => handleCancel(o.id)}>Cancel</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
