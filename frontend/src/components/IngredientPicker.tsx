import { useMemo, useState } from "react";
import type { Ingredient } from "../api";

type Props = {
  ingredients: Ingredient[];
  usedIds: Set<number>;
  onAdd: (ingredient: Ingredient) => Promise<void>;
  onCreateIngredient: (name: string) => Promise<Ingredient>;
};

export default function IngredientPicker({
  ingredients,
  usedIds,
  onAdd,
  onCreateIngredient,
}: Props) {
  const [query, setQuery] = useState("");
  const [busy, setBusy] = useState(false);

  const available = useMemo(() => {
    const q = query.trim().toLowerCase();
    return ingredients
      .filter((item) => !usedIds.has(item.id))
      .filter((item) => !q || item.name.toLowerCase().includes(q))
      .slice(0, 20);
  }, [ingredients, query, usedIds]);

  const exactExists = ingredients.some(
    (item) => item.name.toLowerCase() === query.trim().toLowerCase()
  );

  async function add(item: Ingredient) {
    setBusy(true);
    try {
      await onAdd(item);
      setQuery("");
    } finally {
      setBusy(false);
    }
  }

  async function createAndAdd() {
    const name = query.trim();
    if (!name || exactExists) return;
    setBusy(true);
    try {
      const item = await onCreateIngredient(name);
      await onAdd(item);
      setQuery("");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="picker">
      <label htmlFor="ingredient-search">Add ingredient</label>
      <input
        id="ingredient-search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search bourbon, tonic, lime..."
      />

      {query && (
        <div className="picker-results">
          {available.map((item) => (
            <button key={item.id} disabled={busy} onClick={() => add(item)}>
              <span>{item.name}</span>
              <small>{item.category || "Other"}</small>
            </button>
          ))}

          {!exactExists && query.trim() && (
            <button className="manual-add" disabled={busy} onClick={createAndAdd}>
              <span>Add “{query.trim()}” manually</span>
              <small>User-created ingredient</small>
            </button>
          )}
        </div>
      )}
    </section>
  );
}
