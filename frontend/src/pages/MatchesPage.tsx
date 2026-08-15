import { useEffect, useState } from "react";
import { api, type BarSession, type RecipeMatch } from "../api";
import AppHeader from "../components/AppHeader";

type Props = { onHome: () => void; onTonightBar: () => void; openRecipe: (id: number) => void };

type Context =
  | { type: "my_bar"; label: "My Bar" }
  | { type: "session"; id: number; label: "Tonight's Bar" };

export default function MatchesPage({ onHome, onTonightBar, openRecipe }: Props) {
  const [sessions, setSessions] = useState<BarSession[]>([]);
  const [context, setContext] = useState<Context | null>(null);
  const [matches, setMatches] = useState<RecipeMatch[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.bars.list().then(setSessions).catch((err) =>
      setError(err instanceof Error ? err.message : "Unable to load bar sessions.")
    );
  }, []);

  async function loadMatches(next: Context) {
    setContext(next);
    setLoading(true);
    setError("");
    try {
      const data = next.type === "my_bar"
        ? await api.matches.myBar()
        : await api.matches.session(next.id);
      setMatches(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to find drinks.");
    } finally {
      setLoading(false);
    }
  }

  const exact = matches.filter((x) => x.status === "exact");
  const substitutions = matches.filter((x) => x.status === "substitution");
  const variants = matches.filter((x) => x.status === "variant");
  const almost = matches.filter((x) => x.status === "almost_there");

  function render(items: RecipeMatch[], badge: string, className: string) {
    if (!items.length) return <p className="empty-state">None right now.</p>;
    return (
      <div className="result-list">
        {items.map((item) => (
          <article
            className="recipe-card recipe-card-link"
            key={`${item.status}-${item.recipe_id}`}
            role="button"
            tabIndex={0}
            onClick={() => openRecipe(item.recipe_id)}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                openRecipe(item.recipe_id);
              }
            }}
          >
            <div>
              <strong>{item.recipe_name}</strong>
              <p>{item.explanation}</p>
              {item.substitutions.length > 0 && <small>Substitutions: {item.substitutions.join(", ")}</small>}
              {item.variant_recipe_name && <small>Variant: {item.variant_recipe_name}</small>}
              {item.missing_required.length > 0 && <small>Missing: {item.missing_required.join(", ")}</small>}
              {item.quantity_issues.length > 0 && <small>Quantity shortfall: {item.quantity_issues.join(", ")}</small>}
              {item.optional_missing.length > 0 && <small>Optional missing: {item.optional_missing.join(", ")}</small>}
              <small>View recipe →</small>
            </div>
            <span className={`status ${className}`}>{badge}</span>
          </article>
        ))}
      </div>
    );
  }

  const tonight = sessions[0] ?? null;

  return (
    <main className="page">
      <AppHeader title="What Can I Make?" onHome={onHome} />

      {!context ? (
        <section>
          <p className="lede">Choose which inventory you want to use.</p>
          <div className="context-grid">
            <button className="context-card" onClick={() => loadMatches({ type: "my_bar", label: "My Bar" })}>
              <strong>My Bar</strong>
              <span>Use your permanent inventory</span>
            </button>
            <button
              className="context-card"
              onClick={() => {
                if (tonight) loadMatches({ type: "session", id: tonight.id, label: "Tonight's Bar" });
                else onTonightBar();
              }}
            >
              <strong>Tonight's Bar</strong>
              <span>{tonight ? `Use tonight's inventory • ${tonight.session_date}` : "Set up tonight's inventory"}</span>
            </button>
          </div>
        </section>
      ) : (
        <>
          <div className="toolbar">
            <div><small>Using</small><strong className="context-label">{context.label}</strong></div>
            <button className="link-button" onClick={() => { setContext(null); setMatches([]); }}>Change Bar</button>
          </div>

          {loading ? <p>Checking recipes…</p> : (
            <>
              <section className="result-section"><h2>🟢 Exact <span>{exact.length}</span></h2>{render(exact, "Can Make", "makeable")}</section>
              <section className="result-section"><h2>🔵 With Substitution <span>{substitutions.length}</span></h2>{render(substitutions, "Substitution", "substitution")}</section>
              <section className="result-section"><h2>🟣 With Variant <span>{variants.length}</span></h2>{render(variants, "Variant", "variant")}</section>
              <section className="result-section"><h2>🟡 Almost There <span>{almost.length}</span></h2>{render(almost, "Almost There", "almost")}</section>
            </>
          )}
        </>
      )}

      {error && <p className="error">{error}</p>}
    </main>
  );
}
