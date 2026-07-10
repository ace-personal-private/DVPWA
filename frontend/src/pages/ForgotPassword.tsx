import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { forgotPassword } from "../api/auth";

export function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [result, setResult] = useState<{ detail: string; reset_token?: string } | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const res = await forgotPassword(email);
    setResult(res);
  }

  return (
    <div>
      <h1>Forgot password</h1>
      <form className="form" onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <button type="submit">Send reset token</button>
      </form>
      {result && (
        <div className="card">
          <p>{result.detail}</p>
          {result.reset_token && (
            <>
              <p>No email server is configured for this demo, so here's your token directly:</p>
              <p>
                <code>{result.reset_token}</code>
              </p>
              <p>
                <Link to="/reset-password">Continue to reset password</Link>
              </p>
            </>
          )}
        </div>
      )}
    </div>
  );
}
