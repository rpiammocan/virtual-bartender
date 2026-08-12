import { useEffect, useState } from "react";
import { api } from "../api";
import AppHeader from "../components/AppHeader";

type Props = {
  recipeId: number;
  onHome: () => void;
};

export default function RecipeDetailPage({ recipeId, onHome }: Props) {
  const [recipe, setRecipe] = useState<any>(null);
  const [metric, setMetric] = useState(false);
  const [favorite, setFavorite] = useState(false);
  const [rating, setRating] = useState("5");
  const [notes, setNotes] = useState("");

  async function load() {
    const [display, detail] = await Promise.all([
      api.display.recipe(recipeId, metric),
      api.recipes.get(recipeId),
    ]);
    setRecipe(display);
    setFavorite(detail.favorite);
  }

  useEffect(() => { load(); }, [recipeId, metric]);

  if (!recipe) return <main className="page"><p>Loading recipe…</p></main>;

  async function toggleFavorite() {
    favorite ? await api.favorites.remove(recipe.id) : await api.favorites.add(recipe.id);
    setFavorite(!favorite);
  }

  async function madeThis() {
    await api.history.add({
      recipe_id: recipe.id,
      rating: Number(rating),
      notes: notes || null,
    });
    setNotes("");
    window.alert("Added to drink history.");
  }

  return (
    <main className="page">
      <AppHeader title={recipe.name} onHome={onHome} />

      <div className="toolbar no-print">
        <button onClick={toggleFavorite}>{favorite ? "★ Favorite" : "☆ Add Favorite"}</button>
        <button onClick={() => setMetric(!metric)}>{metric ? "US Units" : "Metric"}</button>
        <button onClick={() => window.print()}>Print Recipe</button>
        <a className="button-link" href={api.exports.markdownUrl(recipe.id)}>Download .md</a>
        <a className="button-link" href={api.exports.textUrl(recipe.id)}>Download .txt</a>
      </div>

      {recipe.image_path && (
        <figure className="recipe-image-wrap">
          <img className="recipe-image" src={recipe.image_path} alt={recipe.name} />
          {recipe.image_ai_generated && <figcaption className="ai-label">AI-generated image</figcaption>}
        </figure>
      )}

      {recipe.description && <p className="lede">{recipe.description}</p>}

      <section className="detail-card">
        <h2>Ingredients</h2>
        <ul>
          {recipe.ingredients.map((item: any) => (
            <li key={item.ingredient_id}>
              {item.quantity ?? ""} {item.unit ?? ""} {item.name}
              {item.optional ? " (optional)" : ""}
            </li>
          ))}
        </ul>
      </section>

      <section className="detail-card">
        <h2>Instructions</h2>
        <p>{recipe.instructions || "No instructions yet."}</p>
      </section>

      {(recipe.image_source_url || recipe.image_license || recipe.image_attribution) && (
        <section className="image-credit">
          <small>
            Image: {recipe.image_attribution || "source"} {recipe.image_license ? `• ${recipe.image_license}` : ""}
          </small>
        </section>
      )}

      <section className="detail-card no-print">
        <h2>I Made This</h2>
        <label>
          Rating
          <select value={rating} onChange={(e) => setRating(e.target.value)}>
            {[5,4,3,2,1].map((n) => <option key={n} value={n}>{n} star{n === 1 ? "" : "s"}</option>)}
          </select>
        </label>
        <textarea value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Optional notes" rows={4} />
        <button className="primary" onClick={madeThis}>Confirm Made</button>
      </section>
    </main>
  );
}
