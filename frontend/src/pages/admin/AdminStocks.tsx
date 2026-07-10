import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { setStockLogo } from "../../api/admin";
import { listStocks } from "../../api/stocks";
import type { Stock } from "../../api/types";

export function AdminStocks() {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [logoUrls, setLogoUrls] = useState<Record<number, string>>({});
  const [message, setMessage] = useState<string | null>(null);

  function load() {
    listStocks().then(setStocks);
  }

  useEffect(load, []);

  async function handleSetLogo(stockId: number) {
    const url = logoUrls[stockId];
    if (!url) return;
    await setStockLogo(stockId, url);
    setMessage(`Logo fetch triggered for stock #${stockId}`);
    load();
  }

  return (
    <div>
      <h1>Admin: Stocks</h1>
      <nav style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <Link to="/admin/users">Users</Link>
        <Link to="/admin/stocks">Stocks</Link>
        <Link to="/admin/tickets">Support tickets</Link>
        <Link to="/admin/reports">Reports</Link>
      </nav>
      {message && <p className="success">{message}</p>}
      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Name</th>
            <th>Price</th>
            <th>Logo URL</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {stocks.map((s) => (
            <tr key={s.id}>
              <td>{s.ticker}</td>
              <td>{s.name}</td>
              <td>${s.price.toFixed(2)}</td>
              <td>
                <input
                  placeholder="https://example.com/logo.png"
                  value={logoUrls[s.id] ?? s.logo_url ?? ""}
                  onChange={(e) => setLogoUrls({ ...logoUrls, [s.id]: e.target.value })}
                  style={{ width: "100%" }}
                />
              </td>
              <td>
                <button onClick={() => handleSetLogo(s.id)}>Set logo</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
