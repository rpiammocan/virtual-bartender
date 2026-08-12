import { useEffect, useState } from "react";
import { api, type BarSession } from "../api";
import AppHeader from "../components/AppHeader";

type Props = { onHome: () => void; openRecipe: (id: number) => void };

export default function SurprisePage({ onHome, openRecipe }: Props) {
  const [sessions, setSessions] = useState<BarSession[]>([]);
  const [context, setContext] = useState("my_bar");
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => { api.bars.list().then(setSessions); }, []);

  async function surprise() {
    try {
      setError("");
      const data = context === "my_bar"
        ? await api.surprise.myBar()
        : await api.surprise.session(Number(context));
      setResult(data);
    } catch (err) {
      setResult(null);
      setError(err instanceof Error ? err.message : "No eligible drinks found.");
    }
  }

  return (
    <main className="page">
      <AppHeader title="Surprise Me" onHome={onHome} />
      <div className="toolbar">
        <select value={context} onChange={(e) => setContext(e.target.value)}>
          <option value="my_bar">My Bar</option>
          {sessions.map((session) => (
            <option value={session.id} key={session.id}>{session.name} — {session.session_date}</option>
          ))}
        </select>
        <button className="primary" onClick={surprise}>Surprise Me</button>
      </div>

      {result && (
        <section className="surprise-card">
          <p className="eyebrow">Your drink</p>
          <h2>{result.recipe_name}</h2>
          <p>{result.explanation}</p>
          {result.substitutions?.length > 0 && <p>Substitutions: {result.substitutions.join(", ")}</p>}
          <button onClick={() => openRecipe(result.recipe_id)}>View Recipe</button>
        </section>
      )}

      {error && <p className="error">{error}</p>}
    </main>
  );
}
