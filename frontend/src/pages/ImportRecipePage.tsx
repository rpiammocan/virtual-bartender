import { useEffect, useState } from "react";
import { api, type Ingredient } from "../api";
import AppHeader from "../components/AppHeader";

type Props = { onHome: () => void; openRecipe?: (id: number) => void };
type Mode = "manual" | "single" | "bulk";
type ManualIngredient = { quantity: number | null; unit: string | null; name: string };
type ManualDraft = { name: string; recipe_type: "cocktail" | "mocktail"; ingredients: ManualIngredient[]; instructions: string[] };

const newManualDraft = (): ManualDraft => ({
  name: "",
  recipe_type: "cocktail",
  ingredients: [{ quantity: 1, unit: "oz", name: "" }],
  instructions: [],
});

function IngredientNameInput({
  value,
  onChange,
  listId,
  ingredientNames,
}: {
  value: string;
  onChange: (value: string) => void;
  listId: string;
  ingredientNames: string[];
}) {
  return (
    <>
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Ingredient"
        list={listId}
        autoComplete="off"
      />
      <datalist id={listId}>
        {ingredientNames.map((name) => <option key={name} value={name} />)}
      </datalist>
    </>
  );
}

export default function ImportRecipePage({ onHome, openRecipe }: Props) {
  const [mode, setMode] = useState<Mode>("manual");
  const [url, setUrl] = useState("");
  const [draft, setDraft] = useState<any>(null);
  const [manual, setManual] = useState<ManualDraft>(newManualDraft());
  const [collection, setCollection] = useState<any>(null);
  const [selected, setSelected] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [progress, setProgress] = useState("");
  const [savedId, setSavedId] = useState<number | null>(null);
  const [knownIngredients, setKnownIngredients] = useState<Ingredient[]>([]);

  useEffect(() => {
    api.ingredients.list()
      .then((items) => setKnownIngredients(items.filter((item) => item.is_active).sort((a, b) => a.name.localeCompare(b.name))))
      .catch(() => setKnownIngredients([]));
  }, []);

  const ingredientNames = knownIngredients.map((item) => item.name);

  async function importRecipe(target = url) {
    setBusy(true);
    setError("");
    setDraft(null);
    setSavedId(null);
    try {
      setDraft(await api.importer.fromUrl(target));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Import failed.");
    } finally {
      setBusy(false);
    }
  }

  async function scan() {
    setBusy(true);
    setError("");
    setCollection(null);
    try {
      const result = await api.importer.scanCollection(url);
      setCollection(result);
      setSelected(result.recipes.map((recipe: any) => recipe.url));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Collection scan failed.");
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

  function updateManualIngredient(index: number, key: keyof ManualIngredient, value: string | number | null) {
    setManual((current) => {
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

  async function saveManual() {
    const ingredients = manual.ingredients.filter((item) => item.name.trim());
    if (!manual.name.trim() || ingredients.length === 0) {
      setError("Enter a recipe name and at least one ingredient.");
      return;
    }
    setBusy(true);
    setError("");
    setSavedId(null);
    try {
      const result = await api.importer.save({
        source_url: "local://manual-entry",
        source_name: "Manual Entry",
        name: manual.name.trim(),
        recipe_type: manual.recipe_type,
        instructions: manual.instructions,
        ingredients,
        warnings: [],
        extraction_method: "manual",
        description: null,
        image_path: null,
      });
      setSavedId(result.recipe_id);
      setManual(newManualDraft());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save recipe.");
    } finally {
      setBusy(false);
    }
  }

  async function bulkImport() {
    setBusy(true);
    setError("");
    let done = 0;
    let skipped = 0;
    for (const target of selected) {
      try {
        setProgress(`Importing ${done + skipped + 1} of ${selected.length}…`);
        const item = await api.importer.fromUrl(target);
        if (item.possible_duplicates?.some((duplicate: any) => duplicate.score >= 95)) {
          skipped += 1;
          continue;
        }
        await api.importer.save({
          source_url: item.source_url,
          source_name: item.source_name,
          name: item.name,
          recipe_type: "cocktail",
          instructions: item.instructions || [],
          ingredients: item.ingredients || [],
          warnings: item.warnings || [],
          extraction_method: item.extraction_method,
          description: null,
          image_path: null,
        });
        done += 1;
      } catch {
        skipped += 1;
      }
    }
    setProgress(`Finished: ${done} imported, ${skipped} skipped/review needed.`);
    setBusy(false);
  }

  return (
    <main className="page theme-recipes">
      <AppHeader title="Add / Import Recipe" onHome={onHome} />
      <div className="theme-prop recipe-ledger"><strong>Recipe Desk</strong><span>Type your own recipe or bring in recipes from the outside.</span></div>
      <div className="toolbar">
        <button className={mode === "manual" ? "primary" : ""} onClick={() => setMode("manual")}>Add Recipe Manually</button>
        <button className={mode === "single" ? "primary" : ""} onClick={() => setMode("single")}>Import One Recipe</button>
        <button className={mode === "bulk" ? "primary" : ""} onClick={() => setMode("bulk")}>Bulk Import from Website</button>
      </div>
      <p className="lede">{mode === "manual" ? "Enter the same recipe details you would review after an import, but type them in yourself." : mode === "single" ? "Paste one recipe URL. Review and edit everything before saving it locally." : "Paste a recipe collection page. Scan it, select recipes, and save them to your offline Virtual Bartender database."}</p>

      {mode !== "manual" && <div className="toolbar"><input className="wide-input" placeholder="https://..." value={url} onChange={(event) => setUrl(event.target.value)} /><button className="primary" disabled={busy || !url.trim()} onClick={() => mode === "single" ? importRecipe() : scan()}>{busy ? "Working…" : mode === "single" ? "Import & Review" : "Scan Website"}</button></div>}
      {error && <p className="error">{error}</p>}

      {mode === "manual" && <section className="detail-card">
        <p className="eyebrow">Add Recipe Manually</p>
        <label>Recipe name<input className="wide-input" value={manual.name} onChange={(event) => setManual({ ...manual, name: event.target.value })} placeholder="Recipe name" /></label>
        <label>Type <select value={manual.recipe_type} onChange={(event) => setManual({ ...manual, recipe_type: event.target.value as "cocktail" | "mocktail" })}><option value="cocktail">Cocktail</option><option value="mocktail">Mocktail</option></select></label>
        <h3>Ingredients</h3>
        <div className="import-ingredients">{manual.ingredients.map((item, index) => <div className="import-row" key={index}>
          <input value={item.quantity ?? ""} onChange={(event) => updateManualIngredient(index, "quantity", event.target.value === "" ? null : Number(event.target.value))} placeholder="Qty" />
          <select value={item.unit ?? ""} onChange={(event) => updateManualIngredient(index, "unit", event.target.value || null)}><option value="">Unit</option><option value="oz">oz</option><option value="ml">ml</option><option value="tsp">tsp</option><option value="tbsp">tbsp</option><option value="dash">dash</option><option value="pc">pc</option><option value="cup">cup</option></select>
          <IngredientNameInput value={item.name} onChange={(value) => updateManualIngredient(index, "name", value)} listId={`manual-ingredient-${index}`} ingredientNames={ingredientNames} />
          <button className="danger-link" type="button" onClick={() => setManual((current) => ({ ...current, ingredients: current.ingredients.filter((_, itemIndex) => itemIndex !== index) }))}>Remove</button>
        </div>)}</div>
        <div className="toolbar"><button type="button" onClick={() => setManual((current) => ({ ...current, ingredients: [...current.ingredients, { quantity: 1, unit: "oz", name: "" }] }))}>+ Ingredient</button></div>
        <h3>Instructions</h3>
        <textarea rows={8} value={manual.instructions.join("\n")} onChange={(event) => setManual({ ...manual, instructions: event.target.value.split("\n").filter((line) => line.trim()) })} placeholder="Enter each step on a new line" />
        <div className="toolbar"><button className="primary" disabled={busy || !manual.name.trim()} onClick={saveManual}>{busy ? "Saving…" : "Save Recipe"}</button></div>
        {savedId !== null && <p className="success">Recipe saved successfully. {openRecipe && <button className="link-button" onClick={() => openRecipe(savedId)}>View Recipe</button>}</p>}
      </section>}

      {mode === "bulk" && collection && <section className="detail-card">
        <h2>{collection.count} recipes found</h2>
        <div className="toolbar"><button onClick={() => setSelected(collection.recipes.map((recipe: any) => recipe.url))}>Select All</button><button onClick={() => setSelected([])}>Clear</button><button className="primary" disabled={busy || selected.length === 0} onClick={bulkImport}>Import Selected ({selected.length})</button></div>
        <div className="result-list">{collection.recipes.map((item: any) => <label className="recipe-card" key={item.url}><span><input type="checkbox" checked={selected.includes(item.url)} onChange={(event) => setSelected((current) => event.target.checked ? [...current, item.url] : current.filter((value) => value !== item.url))} /> {item.name}</span><small>{item.url}</small></label>)}</div>
        {progress && <p className="success">{progress}</p>}
      </section>}

      {mode === "single" && draft && <section className="detail-card">
        <p className="eyebrow">Review import</p>
        <label>Recipe name<input className="wide-input" value={draft.name || ""} onChange={(event) => setDraft({ ...draft, name: event.target.value })} /></label>
        <label>Type <select value={draft.recipe_type || "cocktail"} onChange={(event) => setDraft({ ...draft, recipe_type: event.target.value })}><option value="cocktail">Cocktail</option><option value="mocktail">Mocktail</option></select></label>
        <p><strong>Source:</strong> {draft.source_name}</p>
        <h3>Ingredients</h3>
        <div className="import-ingredients">{draft.ingredients?.map((item: any, index: number) => <div className="import-row" key={index}>
          <input value={item.quantity ?? ""} onChange={(event) => updateIngredient(index, "quantity", event.target.value === "" ? null : Number(event.target.value))} placeholder="Qty" />
          <select value={item.unit || ""} onChange={(event) => updateIngredient(index, "unit", event.target.value || null)}><option value="">Unit</option><option value="oz">oz</option><option value="ml">ml</option><option value="tsp">tsp</option><option value="tbsp">tbsp</option><option value="dash">dash</option><option value="pc">pc</option><option value="cup">cup</option></select>
          <IngredientNameInput value={item.name || ""} onChange={(value) => updateIngredient(index, "name", value)} listId={`import-ingredient-${index}`} ingredientNames={ingredientNames} />
        </div>)}</div>
        <h3>Instructions</h3>
        <textarea rows={8} value={(draft.instructions || []).join("\n")} onChange={(event) => setDraft({ ...draft, instructions: event.target.value.split("\n").filter((line: string) => line.trim()) })} />
        <div className="toolbar"><button className="primary" disabled={busy || !draft.name?.trim()} onClick={saveRecipe}>Save Recipe</button></div>
        {savedId !== null && <p className="success">Recipe saved successfully. {openRecipe && <button className="link-button" onClick={() => openRecipe(savedId)}>View Recipe</button>}</p>}
      </section>}
    </main>
  );
}
