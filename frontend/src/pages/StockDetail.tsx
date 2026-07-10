import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getStock } from "../api/stocks";
import { placeOrder } from "../api/orders";
import type { Stock } from "../api/types";
import { useAuth } from "../context/AuthContext";

export function StockDetail() {
  const { id } = useParams();
  const { refreshUser } = useAuth();
  const [stock, setStock] = useState<Stock | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) getStock(Number(id)).then(setStock);
  }, [id]);

  async function handleTrade(side: "buy" | "sell") {
    if (!stock) return;
    setMessage(null);
    setError(null);
    try {
      await placeOrder(stock.id, side, quantity, stock.price);
      setMessage(`${side === "buy" ? "Bought" : "Sold"} ${quantity} share(s) of ${stock.ticker}`);
      await refreshUser();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Order failed");
    }
  }

  if (!stock) return <p>Loading...</p>;

  return (
    <div>
      <h1>
        {stock.ticker} <span style={{ color: "var(--text)" }}>{stock.name}</span>
      </h1>
      <p style={{ fontSize: 24, fontWeight: 700 }}>${stock.price.toFixed(2)}</p>

      <div className="card" style={{ maxWidth: 320 }}>
        <label>
          Quantity
          <input
            type="number"
            min={1}
            value={quantity}
            onChange={(e) => setQuantity(Number(e.target.value))}
            style={{ display: "block", marginTop: 4, marginBottom: 12, width: "100%" }}
          />
        </label>
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={() => handleTrade("buy")}>Buy</button>
          <button onClick={() => handleTrade("sell")}>Sell</button>
        </div>
        {message && <p className="success">{message}</p>}
        {error && <p className="error">{error}</p>}
      </div>
    </div>
  );
}
