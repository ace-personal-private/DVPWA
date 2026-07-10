import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function NavBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">StonksCo</Link>
      </div>
      {user ? (
        <div className="navbar-links">
          <Link to="/">Dashboard</Link>
          <Link to="/stocks">Stocks</Link>
          <Link to="/orders">Orders</Link>
          <Link to="/wallet">Wallet</Link>
          <Link to="/support">Support</Link>
          <Link to="/profile">Profile</Link>
          {user.role === "admin" && <Link to="/admin/users">Admin</Link>}
          <span className="navbar-balance">${user.balance.toFixed(2)}</span>
          <button onClick={handleLogout}>Log out</button>
        </div>
      ) : (
        <div className="navbar-links">
          <Link to="/login">Log in</Link>
          <Link to="/register">Register</Link>
        </div>
      )}
    </nav>
  );
}
