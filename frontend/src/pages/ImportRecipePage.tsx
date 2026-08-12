import { useState } from "react";
import { api } from "../api";
import AppHeader from "../components/AppHeader";

type Props = {
  onHome: () => void;
  openRecipe?: (id: number) => void;
};

export default function ImportRecipePage({ onHome, openRecipe }: Props) {
  const [url, setUrl] = useState("");
  const [draft, setDraft] = useState<any>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [savedId, setSavedId] = useState<number | null>(null);

  async function importRecipe() {
    setBusy(true);
    setError("");
    setDraft(null);
    setSavedId(null);
    try {
      setDraft(await api.importer.fromUrl(url));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Import failed.");
    } finally {
      setBusy(false);
    }
  }

  function updateIngredient(index: number, key: string, value: any) {
    setDraft((current: any) => {
      const ingredients = [...current.ingredients];
      ingredients[index] = { ...ingredients[index], [key]: value };
      return { ...current, ingredients };
    });
  }

  async function saveRecipe() {
    setBusy(true);
    setError("");
    try {
      const result = await api.importer.save({
        source_url: draft.source_url,
        source_name: draft.source_name,
        name: draft.name,
        recipe_type: draft.recipe_type || "cocktail",
        instructions: draft.instructions || [],
        ingredients: draft.ingredients || [],
        warnings: draft.warnings || [],
        extraction_method: draft.extraction_method,
        description: null,
        image_path: null,
      });
      setSavedId(result.recipe_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save recipe.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="page">
      <AppHeader title="Import Recipe" onHome={onHome} />

      <p className="lede">
        Paste a recipe URL. Virtual Bartender extracts what it can, then lets you review and edit everything before saving.
      </p>

      <div className="toolbar">
        <input
          className="wide-input"
          placeholder="https://..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button className="primary" disabled={busy || !url.trim()} onClick={importRecipe}>
          {busy ? "Working…" : "Import"}
        </button>
      </div>

      {error && <p className="error">{error}</p>}

      {draft && (
        <section className="detail-card">
          <p className="eyebrow">Review import</p>

          <label>
            Recipe name
            <input
              className="wide-input"
              value={draft.name || ""}
              onChange={(e) => setDraft({ ...draft, name: e.target.value })}
            />
          </label>

          <label>
            Type
            <select
              value={draft.recipe_type || "cocktail"}
              onChange={(e) => setDraft({ ...draft, recipe_type: e.target.value })}
            >
              <option value="cocktail">Cocktail</option>
              <option value="mocktail">Mocktail</option>
            </select>
          </label>

          <p><strong>Source:</strong> {draft.source_name}</p>
          <p><strong>Extraction:</strong> {draft.extraction_method}</p>

          <h3>Ingredients</h3>
          <div className="import-ingredients">
            {draft.ingredients?.map((item: any, index: number) => (
              <div className="import-row" key={index}>
                <input
                  value={item.quantity ?? ""}
                  onChange={(e) => updateIngredient(index, "quantity", e.target.value === "" ? null : Number(e.target.value))}
                  placeholder="Qty"
                />
                <select
                  value={item.unit || ""}
                  onChange={(e) => updateIngredient(index, "unit", e.target.value || null)}
                >
                  <option value="">Unit</option>
                  <option value="oz">oz</option>
                  <option value="tsp">tsp</option>
                  <option value="tbsp">tbsp</option>
                  <option value="dash">dash</option>
                  <option value="pc">pc</option>
                </select>
                <input
                  value={item.name || ""}
                  onChange={(e) => updateIngredient(index, "name", e.target.value)}
                  placeholder="Ingredient"
                />
              </div>
            ))}
          </div>

          <h3>Instructions</h3>
          <textarea
            rows={8}
            value={(draft.instructions || []).join("\n")}
            onChange={(e) => setDraft({
              ...draft,
              instructions: e.target.value.split("\n").filter((x: string) => x.trim()),
            })}
          />

          {draft.possible_duplicates?.length > 0 && (
            <>
              <h3>Possible duplicates</h3>
              <div className="result-list">
                {draft.possible_duplicates.map((dup: any) => (
                  <article className="recipe-card" key={dup.recipe_id}>
                    <div>
                      <strong>{dup.name}</strong>
                      <p>Similarity score: {dup.score}%</p>
                    </div>
                  </article>
                ))}
              </div>
            </>
          )}

          {draft.warnings?.length > 0 && (
            <>
              <h3>Warnings</h3>
              <ul>
                {draft.warnings.map((warning: string, index: number) => (
                  <li key={index}>{warning}</li>
                ))}
              </ul>
            </>
          )}

          <div className="toolbar">
            <button className="primary" disabled={busy || !draft.name?.trim()} onClick={saveRecipe}>
              Save Recipe
            </button>
          </div>

          {savedId !== null && (
            <p className="success">
              Recipe saved successfully.
              {openRecipe && (
                <>
                  {" "}
                  <button className="link-button" onClick={() => openRecipe(savedId)}>
                    View Recipe
                  </button>
                </>
              )}
            </p>
          )}
        </section>
      )}
    </main>
  );
}
