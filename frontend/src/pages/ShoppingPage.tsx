import { useEffect, useState } from "react";
import { api, type ShoppingItem } from "../api";
import AppHeader from "../components/AppHeader";

type Props = { onHome: () => void };

export default function ShoppingPage({ onHome }: Props) {
  const [items, setItems] = useState<ShoppingItem[]>([]);
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [name, setName] = useState("");

  async function load() {
    const [shopping, suggested] = await Promise.all([
      api.shopping.list(),
      api.shoppingSuggestions.myBar(),
    ]);
    setItems(shopping);
    const existingIds = new Set(shopping.map((item) => item.ingredient_id).filter(Boolean));
    const existingNames = new Set(shopping.map((item) => (item.custom_name || "").toLowerCase()).filter(Boolean));
    setSuggestions(suggested.filter((item: any) =>
      !existingIds.has(item.ingredient_id) &&
      !existingNames.has(item.ingredient_name.toLowerCase())
    ));
  }

  useEffect(() => { load(); }, []);

  const grouped = items.reduce<Record<string, ShoppingItem[]>>((acc, item) => {
    const category = item.category || "Other";
    (acc[category] ||= []).push(item);
    return acc;
  }, {});

  return (
    <main className="page">
      <AppHeader title="Shopping List" onHome={onHome} />
      <div className="toolbar no-print">
        <input className="wide-input" placeholder="Add item manually..." value={name} onChange={(e) => setName(e.target.value)} />
        <button className="primary" onClick={async () => {
          if (!name.trim()) return;
          await api.shopping.addManual(name.trim());
          setName("");
          await load();
        }}>Add</button>
        <button onClick={() => window.print()}>Print Shopping List</button>
      </div>

      <section className="shopping-list-print-area">
        <h1 className="print-only">Shopping List</h1>
        {items.length === 0 ? <p className="empty-state">Your shopping list is empty.</p> : Object.entries(grouped).map(([category, categoryItems]) => (
          <section className="result-section" key={category}>
            <h2>{category}</h2>
            <div className="inventory-list">
              {categoryItems.map((item) => (
                <article className="inventory-row" key={item.id}>
                  <label className="shopping-label">
                    <input
                      type="checkbox"
                      checked={item.purchased}
                      onChange={async (e) => {
                        await api.shopping.markPurchased(item.id, e.target.checked);
                        await load();
                      }}
                    />
                    <span className={item.purchased ? "purchased" : ""}>{item.custom_name || `Ingredient #${item.ingredient_id}`}</span>
                  </label>
                  <button className="danger-link no-print" onClick={async () => { await api.shopping.remove(item.id); await load(); }}>Remove</button>
                </article>
              ))}
            </div>
          </section>
        ))}
      </section>

      <section className="result-section no-print">
        <h2>Suggested Items</h2>
        <div className="result-list">
          {suggestions.length === 0 ? (
            <p className="empty-state">No smart suggestions yet.</p>
          ) : suggestions.map((item) => (
            <article className="recipe-card" key={item.ingredient_name}>
              <div>
                <strong>{item.ingredient_name}</strong>
                <p>Unlocks {item.unlock_count} recipe{item.unlock_count === 1 ? "" : "s"}</p>
                <small>{item.unlocks.map((r: any) => r.recipe_name).join(", ")}</small>
              </div>
              <button onClick={async () => {
                if (item.ingredient_id) await api.shopping.addIngredient(item.ingredient_id, item.category);
                else await api.shopping.addManual(item.ingredient_name, item.category);
                await load();
              }}>+ Add</button>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
