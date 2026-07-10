import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listUsers } from "../../api/admin";
import type { User } from "../../api/types";

export function AdminUsers() {
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    listUsers().then(setUsers);
  }, []);

  return (
    <div>
      <h1>Admin: Users</h1>
      <nav style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <Link to="/admin/users">Users</Link>
        <Link to="/admin/stocks">Stocks</Link>
        <Link to="/admin/tickets">Support tickets</Link>
        <Link to="/admin/reports">Reports</Link>
      </nav>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Email</th>
            <th>Role</th>
            <th>Balance</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.id}</td>
              <td>{u.username}</td>
              <td>{u.email}</td>
              <td>{u.role}</td>
              <td>${u.balance.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
