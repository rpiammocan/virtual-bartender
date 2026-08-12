import { useEffect, useState } from "react";
import { api } from "../api";
import AppHeader from "../components/AppHeader";

type Props = { onHome: () => void; openRecipe: (id: number) => void };

export default function FavoritesPage({ onHome, openRecipe }: Props) {
  const [items, setItems] = useState<{ recipe_id: number; name: string }[]>([]);
  useEffect(() => { api.favorites.list().then(setItems); }, []);

  return (
    <main className="page">
      <AppHeader title="Favorites" onHome={onHome} />
      <div className="result-list">
        {items.map((item) => (
          <button className="recipe-list-button" key={item.recipe_id} onClick={() => openRecipe(item.recipe_id)}>
            <strong>{item.name}</strong>
          </button>
        ))}
        {items.length === 0 && <p className="empty-state">No favorites yet.</p>}
      </div>
    </main>
  );
}
