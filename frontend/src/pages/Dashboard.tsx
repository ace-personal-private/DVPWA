import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { getPortfolio } from "../api/portfolio";
import { listStocks } from "../api/stocks";
import type { Holding, Stock } from "../api/types";

export function Dashboard() {
  const { user } = useAuth();
  const [holdings, setHoldings] = useState<Holding[]>([]);
  const [stocks, setStocks] = useState<Stock[]>([]);

  useEffect(() => {
    if (!user) return;
    getPortfolio(user.id).then(setHoldings);
    listStocks().then(setStocks);
  }, [user]);

  if (!user) return null;

  const stockById = new Map(stocks.map((s) => [s.id, s]));

  return (
    <div>
      <h1>Welcome, {user.username}</h1>
      <div className="card">
        <h2>Cash balance</h2>
        <p style={{ fontSize: 28, fontWeight: 700 }}>${user.balance.toFixed(2)}</p>
      </div>

      <h2>Your holdings</h2>
      {holdings.length === 0 ? (
        <p>No holdings yet. Head to the Stocks page to place your first trade.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Quantity</th>
              <th>Avg price</th>
              <th>Current price</th>
              <th>Value</th>
            </tr>
          </thead>
          <tbody>
            {holdings.map((h) => {
              const stock = stockById.get(h.stock_id);
              return (
                <tr key={h.id}>
                  <td>{stock?.ticker ?? h.stock_id}</td>
                  <td>{h.quantity}</td>
                  <td>${h.avg_price.toFixed(2)}</td>
                  <td>{stock ? `$${stock.price.toFixed(2)}` : "-"}</td>
                  <td>{stock ? `$${(stock.price * h.quantity).toFixed(2)}` : "-"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
