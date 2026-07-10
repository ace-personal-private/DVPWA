import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { generateReport } from "../../api/admin";

export function AdminReports() {
  const [ticker, setTicker] = useState("");
  const [output, setOutput] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const res = await generateReport(ticker);
      setOutput(res.output || res.error);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Report generation failed");
    }
  }

  return (
    <div>
      <h1>Admin: Reports</h1>
      <nav style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <Link to="/admin/users">Users</Link>
        <Link to="/admin/stocks">Stocks</Link>
        <Link to="/admin/tickets">Support tickets</Link>
        <Link to="/admin/reports">Reports</Link>
      </nav>
      <form className="form" onSubmit={handleSubmit}>
        <input
          placeholder="Ticker (e.g. AAPL)"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          required
        />
        <button type="submit">Generate report</button>
      </form>
      {error && <p className="error">{error}</p>}
      {output && <pre className="ticket-message">{output}</pre>}
    </div>
  );
}
