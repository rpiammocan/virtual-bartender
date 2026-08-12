import { useEffect, useMemo, useState } from "react";
import { api, type BarSession, type Ingredient, type InventoryItem } from "../api";
import AppHeader from "../components/AppHeader";
import IngredientPicker from "../components/IngredientPicker";
import QuantityEditor from "../components/QuantityEditor";

type Props = { onHome: () => void };

function todayLocal() {
  return new Date().toISOString().slice(0, 10);
}

export default function TonightsBarPage({ onHome }: Props) {
  const [sessions, setSessions] = useState<BarSession[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [error, setError] = useState("");

  async function loadSessions() {
    const items = await api.bars.list();
    setSessions(items);
    if (selected === null && items.length) setSelected(items[0].id);
  }

  async function loadIngredients() {
    setIngredients(await api.ingredients.list());
  }

  async function loadInventory(sessionId: number | null) {
    setInventory(sessionId === null ? [] : await api.inventory.listSession(sessionId));
  }

  useEffect(() => {
    Promise.all([loadSessions(), loadIngredients()]).catch((err) =>
      setError(err instanceof Error ? err.message : "Unable to load Tonight's Bar.")
    );
  }, []);

  useEffect(() => {
    loadInventory(selected).catch((err) =>
      setError(err instanceof Error ? err.message : "Unable to load session inventory.")
    );
  }, [selected]);

  const byId = useMemo(() => new Map(ingredients.map((item) => [item.id, item])), [ingredients]);
  const usedIds = new Set(inventory.map((item) => item.ingredient_id));

  async function createSession() {
    const created = await api.bars.create("Tonight's Bar", todayLocal());
    await loadSessions();
    setSelected(created.id);
  }

  async function addIngredient(ingredient: Ingredient) {
    if (selected === null) return;
    await api.inventory.add({
      ingredient_id: ingredient.id,
      context_type: "tonight_bar",
      context_id: selected,
    });
    await loadInventory(selected);
  }

  async function createIngredient(name: string) {
    const created = await api.ingredients.create(name);
    setIngredients((current) => [...current, created]);
    return created;
  }

  return (
    <main className="page">
      <AppHeader title="Tonight's Bar" onHome={onHome} />
      <p className="lede">Persistent sessions that never change My Bar.</p>

      <div className="toolbar">
        <button className="primary" onClick={createSession}>+ New Tonight's Bar</button>
        {sessions.length > 0 && (
          <select value={selected ?? ""} onChange={(e) => setSelected(Number(e.target.value))}>
            {sessions.map((session) => (
              <option key={session.id} value={session.id}>
                {session.name} — {session.session_date}
              </option>
            ))}
          </select>
        )}
        {selected !== null && (
          <>
            <button onClick={async () => { await api.bars.copyMyBar(selected); await loadInventory(selected); }}>
              Copy My Bar
            </button>
            <button className="danger-link" onClick={async () => {
              if (!window.confirm("Delete this Tonight's Bar session? This cannot be undone.")) return;
              await api.bars.remove(selected);
              setSelected(null);
              setInventory([]);
              await loadSessions();
            }}>
              Delete Session
            </button>
          </>
        )}
      </div>

      {selected !== null ? (
        <>
          <IngredientPicker
            ingredients={ingredients}
            usedIds={usedIds}
            onAdd={addIngredient}
            onCreateIngredient={createIngredient}
          />
          <section className="inventory-list">
            {inventory.length === 0 ? (
              <p className="empty-state">This session is empty. Add what is available tonight.</p>
            ) : inventory.map((item) => (
              <article className="inventory-row" key={item.id}>
                <div className="inventory-main">
                  <strong>{byId.get(item.ingredient_id)?.name ?? `Ingredient #${item.ingredient_id}`}</strong>
                  <small>{byId.get(item.ingredient_id)?.category || "Other"}</small>
                </div>
                <QuantityEditor
                  quantity={item.quantity}
                  onSave={async (quantity) => { await api.inventory.updateQuantity(item.id, quantity); await loadInventory(selected); }}
                />
                <button className="danger-link" onClick={async () => { await api.inventory.remove(item.id); await loadInventory(selected); }}>
                  Remove
                </button>
              </article>
            ))}
          </section>
        </>
      ) : <p className="empty-state">Create a Tonight's Bar session to get started.</p>}

      {error && <p className="error">{error}</p>}
    </main>
  );
}
