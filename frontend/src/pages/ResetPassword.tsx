import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { resetPassword } from "../api/auth";

export function ResetPassword() {
  const navigate = useNavigate();
  const [token, setToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await resetPassword(token, newPassword);
      setSuccess(true);
      setTimeout(() => navigate("/login"), 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Reset failed");
    }
  }

  return (
    <div>
      <h1>Reset password</h1>
      <form className="form" onSubmit={handleSubmit}>
        <input
          placeholder="Reset token"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="New password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          required
        />
        {error && <p className="error">{error}</p>}
        {success && <p className="success">Password reset. Redirecting to login...</p>}
        <button type="submit">Reset password</button>
      </form>
    </div>
  );
}
