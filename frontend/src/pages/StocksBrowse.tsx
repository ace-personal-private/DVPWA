import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listStocks } from "../api/stocks";
import type { Stock } from "../api/types";

export function StocksBrowse() {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    listStocks(search || undefined).then(setStocks);
  }, [search]);

  return (
    <div>
      <h1>Stocks</h1>
      <input
        placeholder="Search by ticker or name..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        style={{ marginBottom: 16, width: "100%", maxWidth: 400 }}
      />
      <div className="stock-grid">
        {stocks.map((stock) => (
          <Link key={stock.id} to={`/stocks/${stock.id}`} className="stock-card">
            <h3>{stock.ticker}</h3>
            <p>{stock.name}</p>
            <p style={{ fontWeight: 600 }}>${stock.price.toFixed(2)}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
