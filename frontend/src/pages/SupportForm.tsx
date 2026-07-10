import { useEffect, useState, type FormEvent } from "react";
import { createTicket, listMyTickets } from "../api/support";
import type { SupportTicket } from "../api/types";

export function SupportForm() {
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [tickets, setTickets] = useState<SupportTicket[]>([]);

  function load() {
    listMyTickets().then(setTickets);
  }

  useEffect(load, []);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await createTicket(subject, message);
    setSubject("");
    setMessage("");
    load();
  }

  return (
    <div>
      <h1>Support</h1>
      <form className="form" onSubmit={handleSubmit}>
        <input
          placeholder="Subject"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          required
        />
        <textarea
          placeholder="How can we help?"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          rows={4}
          required
        />
        <button type="submit">Submit ticket</button>
      </form>

      <h2>Your tickets</h2>
      {tickets.map((t) => (
        <div key={t.id} className="card">
          <h3>{t.subject}</h3>
          <p>{t.message}</p>
          <p style={{ fontSize: 12 }}>Status: {t.status}</p>
        </div>
      ))}
    </div>
  );
}
