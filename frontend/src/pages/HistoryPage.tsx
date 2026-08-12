import { useEffect, useState } from "react";
import { api, type HistoryItem } from "../api";
import AppHeader from "../components/AppHeader";

type Props = { onHome: () => void };

export default function HistoryPage({ onHome }: Props) {
  const [items, setItems] = useState<HistoryItem[]>([]);
  useEffect(() => { api.history.list().then(setItems); }, []);

  return (
    <main className="page">
      <AppHeader title="Drink History" onHome={onHome} />
      <div className="result-list">
        {items.map((item) => (
          <article className="recipe-card" key={item.id}>
            <div>
              <strong>Recipe #{item.recipe_id}</strong>
              <p>{new Date(item.made_at).toLocaleString()}</p>
              {item.rating && <small>{"★".repeat(item.rating)}</small>}
              {item.notes && <p>{item.notes}</p>}
            </div>
          </article>
        ))}
        {items.length === 0 && <p className="empty-state">No drinks recorded yet.</p>}
      </div>
    </main>
  );
}
