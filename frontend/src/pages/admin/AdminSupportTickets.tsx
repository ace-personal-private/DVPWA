import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listAllTickets } from "../../api/admin";
import type { SupportTicket } from "../../api/types";

export function AdminSupportTickets() {
  const [tickets, setTickets] = useState<SupportTicket[]>([]);

  useEffect(() => {
    listAllTickets().then(setTickets);
  }, []);

  return (
    <div>
      <h1>Admin: Support tickets</h1>
      <nav style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <Link to="/admin/users">Users</Link>
        <Link to="/admin/stocks">Stocks</Link>
        <Link to="/admin/tickets">Support tickets</Link>
        <Link to="/admin/reports">Reports</Link>
      </nav>
      {tickets.map((t) => (
        <div key={t.id} className="card">
          <h3>
            {t.subject} <span style={{ fontSize: 12 }}>(user #{t.user_id})</span>
          </h3>
          {/* VULN-CWE-79: ticket.message is rendered as raw HTML with no
              sanitization. It's stored verbatim from user input in
              support.py, so a malicious ticket body executes here in the
              admin's browser session (which holds the admin JWT in
              localStorage). */}
          <div className="ticket-message" dangerouslySetInnerHTML={{ __html: t.message }} />
        </div>
      ))}
    </div>
  );
}
