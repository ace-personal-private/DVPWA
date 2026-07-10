import { useEffect, useState, type FormEvent } from "react";
import { deposit, listMyTransactions, withdraw } from "../api/wallet";
import type { Transaction } from "../api/types";
import { useAuth } from "../context/AuthContext";

export function Wallet() {
  const { user, refreshUser } = useAuth();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [amount, setAmount] = useState("");
  const [error, setError] = useState<string | null>(null);

  function load() {
    listMyTransactions().then(setTransactions);
  }

  useEffect(load, []);

  async function handleDeposit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await deposit(Number(amount));
      await refreshUser();
      load();
      setAmount("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Deposit failed");
    }
  }

  async function handleWithdraw(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await withdraw(Number(amount));
      await refreshUser();
      load();
      setAmount("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Withdraw failed");
    }
  }

  return (
    <div>
      <h1>Wallet</h1>
      <p style={{ fontSize: 24, fontWeight: 700 }}>${user?.balance.toFixed(2)}</p>

      <form className="form" style={{ flexDirection: "row" }}>
        <input
          type="number"
          placeholder="Amount"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
        />
        <button onClick={handleDeposit}>Deposit</button>
        <button onClick={handleWithdraw}>Withdraw</button>
      </form>
      {error && <p className="error">{error}</p>}

      <h2>Transaction history</h2>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Type</th>
            <th>Amount</th>
            <th>Balance after</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((t) => (
            <tr key={t.id}>
              <td>{t.id}</td>
              <td>{t.type}</td>
              <td>${t.amount.toFixed(2)}</td>
              <td>${t.balance_after.toFixed(2)}</td>
              <td>{new Date(t.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
