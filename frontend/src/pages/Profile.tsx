import { useRef, useState, type FormEvent } from "react";
import { useAuth } from "../context/AuthContext";
import { updateMe, uploadAvatar } from "../api/users";
import { exportBackup, importBackup } from "../api/portfolio";
import { API_BASE } from "../api/client";

export function Profile() {
  const { user, refreshUser } = useAuth();
  const [username, setUsername] = useState(user?.username ?? "");
  const [message, setMessage] = useState<string | null>(null);
  const [backup, setBackup] = useState<string | null>(null);
  const [importData, setImportData] = useState("");
  const fileInput = useRef<HTMLInputElement>(null);

  if (!user) return null;

  async function handleSaveProfile(e: FormEvent) {
    e.preventDefault();
    await updateMe({ username });
    await refreshUser();
    setMessage("Profile updated.");
  }

  async function handleAvatarUpload(e: FormEvent) {
    e.preventDefault();
    const file = fileInput.current?.files?.[0];
    if (!file) return;
    await uploadAvatar(file);
    await refreshUser();
    setMessage("Avatar uploaded.");
  }

  async function handleExport() {
    const res = await exportBackup();
    setBackup(res.backup);
  }

  async function handleImport(e: FormEvent) {
    e.preventDefault();
    const res = await importBackup(importData);
    setMessage(res.detail);
  }

  return (
    <div>
      <h1>Profile</h1>

      <div className="card">
        <h2>Account</h2>
        <form className="form" onSubmit={handleSaveProfile}>
          <label>
            Email
            <input
              value={user.email}
              disabled
              style={{ display: "block", width: "100%", marginTop: 4 }}
            />
          </label>
          <label>
            Username
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{ display: "block", width: "100%", marginTop: 4 }}
            />
          </label>
          <button type="submit">Save</button>
        </form>
      </div>

      <div className="card">
        <h2>Avatar</h2>
        {user.avatar_path && (
          <img src={`${API_BASE}${user.avatar_path}`} alt="avatar" width={80} height={80} />
        )}
        <form onSubmit={handleAvatarUpload}>
          <input type="file" ref={fileInput} />
          <button type="submit">Upload</button>
        </form>
      </div>

      <div className="card">
        <h2>Portfolio backup</h2>
        <p>Export your holdings to a portable backup blob, or restore from one.</p>
        <button onClick={handleExport}>Export backup</button>
        {backup && (
          <textarea readOnly value={backup} rows={4} style={{ width: "100%", marginTop: 8 }} />
        )}
        <form className="form" onSubmit={handleImport} style={{ marginTop: 12 }}>
          <textarea
            placeholder="Paste a backup blob to restore..."
            value={importData}
            onChange={(e) => setImportData(e.target.value)}
            rows={4}
          />
          <button type="submit">Import backup</button>
        </form>
      </div>

      {message && <p className="success">{message}</p>}
    </div>
  );
}
