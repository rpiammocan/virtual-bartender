import { useEffect, useMemo, useState } from "react";
import { api, type Ingredient, type InventoryItem } from "../api";
import AppHeader from "../components/AppHeader";
import IngredientPicker from "../components/IngredientPicker";
import QuantityEditor from "../components/QuantityEditor";

type Props = { onHome: () => void };

export default function MyBarPage({ onHome }: Props) {
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [error, setError] = useState("");

  async function load() {
    try {
      setError("");
      const [allIngredients, items] = await Promise.all([
        api.ingredients.list(),
        api.inventory.listMyBar(),
      ]);
      setIngredients(allIngredients);
      setInventory(items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load My Bar.");
    }
  }

  useEffect(() => { load(); }, []);

  const byId = useMemo(() => new Map(ingredients.map((item) => [item.id, item])), [ingredients]);
  const usedIds = new Set(inventory.map((item) => item.ingredient_id));

  async function addIngredient(ingredient: Ingredient) {
    await api.inventory.add({ ingredient_id: ingredient.id, context_type: "my_bar", context_id: null });
    await load();
  }

  async function createIngredient(name: string) {
    const created = await api.ingredients.create(name);
    setIngredients((current) => [...current, created]);
    return created;
  }

  return (
    <main className="page">
      <AppHeader title="My Bar" onHome={onHome} />
      <p className="lede">Your permanent inventory. Quantities are optional.</p>

      <IngredientPicker
        ingredients={ingredients}
        usedIds={usedIds}
        onAdd={addIngredient}
        onCreateIngredient={createIngredient}
      />

      {error && <p className="error">{error}</p>}

      <section className="inventory-list">
        {inventory.length === 0 ? (
          <p className="empty-state">Your bar is empty. Add your first ingredient above.</p>
        ) : inventory.map((item) => (
          <article className="inventory-row" key={item.id}>
            <div className="inventory-main">
              <strong>{byId.get(item.ingredient_id)?.name ?? `Ingredient #${item.ingredient_id}`}</strong>
              <small>{byId.get(item.ingredient_id)?.category || "Other"}</small>
            </div>
            <QuantityEditor
              quantity={item.quantity}
              onSave={async (quantity) => { await api.inventory.updateQuantity(item.id, quantity); await load(); }}
            />
            <button className="danger-link" onClick={async () => { await api.inventory.remove(item.id); await load(); }}>
              Remove
            </button>
          </article>
        ))}
      </section>
    </main>
  );
}
