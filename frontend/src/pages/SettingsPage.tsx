import { useEffect, useState } from "react";
import { api } from "../api";
import AppHeader from "../components/AppHeader";

type Props = { onHome: () => void };

export default function SettingsPage({ onHome }: Props) {
  const [backups, setBackups] = useState<any[]>([]);
  const [message, setMessage] = useState("");

  async function load() {
    setBackups(await api.backups.list());
  }

  useEffect(() => { load(); }, []);

  return (
    <main className="page">
      <AppHeader title="Settings" onHome={onHome} />

      <section className="detail-card">
        <h2>Backups</h2>
        <p className="lede">Virtual Bartender keeps recent local backups and supports manual backup/restore.</p>
        <div className="toolbar">
          <button className="primary" onClick={async () => {
            setMessage("Creating backup…");
            try {
              await api.backups.create();
              setMessage("Backup created.");
              await load();
            } catch (err) {
              setMessage(err instanceof Error ? err.message : "Backup failed.");
            }
          }}>Backup Now</button>
        </div>

        {message && <p>{message}</p>}

        <div className="result-list">
          {backups.map((item) => (
            <article className="recipe-card" key={item.id}>
              <div>
                <strong>{new Date(item.created_at).toLocaleString()}</strong>
                <p>{Math.round((item.size_bytes || 0) / 1024)} KB</p>
              </div>
              <button onClick={async () => {
                if (!window.confirm("Restore this backup? Current data will be replaced. A safety copy will be created first.")) return;
                setMessage("Restoring backup…");
                try {
                  await api.backups.restore(item.id);
                  setMessage("Backup restored. Restart the app/backend before continuing.");
                } catch (err) {
                  setMessage(err instanceof Error ? err.message : "Restore failed.");
                }
              }}>Restore</button>
            </article>
          ))}
          {backups.length === 0 && <p className="empty-state">No backups yet.</p>}
        </div>
      </section>
    </main>
  );
}
