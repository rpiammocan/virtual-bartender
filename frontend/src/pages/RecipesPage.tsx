import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import AppHeader from "../components/AppHeader";

type Props = {
  onHome: () => void;
  openRecipe: (id: number) => void;
  manageRecipes?: () => void;
};

function normalizeSearch(value: string) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

export default function RecipesPage({ onHome, openRecipe, manageRecipes }: Props) {
  const [recipes, setRecipes] = useState<any[]>([]);
  const [query, setQuery] = useState("");
  const [type, setType] = useState("all");
  const [sort, setSort] = useState("name");

  useEffect(() => {
    api.recipes.list().then(setRecipes);
  }, []);

  const filtered = useMemo(() => {
    const q = normalizeSearch(query.trim());
    let rows = recipes.filter((r) => !q || normalizeSearch(r.name).includes(q));
    if (type !== "all") rows = rows.filter((r) => r.recipe_type === type);
    rows = [...rows].sort((a, b) => {
      if (sort === "type") return (a.recipe_type || "").localeCompare(b.recipe_type || "") || a.name.localeCompare(b.name);
      return a.name.localeCompare(b.name);
    });
    return rows;
  }, [recipes, query, type, sort]);

  return (
    <main className="page theme-recipes">
      <AppHeader title="Recipes" onHome={onHome} />

      <div className="theme-prop recipe-ledger" aria-hidden="true">
        <strong>Bootlegger's Recipe Book</strong>
        <span>House formulas • private stock</span>
      </div>

      <div className="toolbar">
        <input className="wide-input" placeholder="Search recipes..." value={query} onChange={(e) => setQuery(e.target.value)} />
        <select value={type} onChange={(e) => setType(e.target.value)}>
          <option value="all">All</option>
          <option value="cocktail">Cocktails</option>
          <option value="mocktail">Mocktails</option>
        </select>
        <select value={sort} onChange={(e) => setSort(e.target.value)}>
          <option value="name">Sort: Name</option>
          <option value="type">Sort: Type</option>
        </select>
        {manageRecipes && <button className="primary" onClick={manageRecipes}>＋ Add / Import Recipe</button>}
      </div>

      <p className="lede">{filtered.length} recipes</p>

      <section className="result-list">
        {filtered.map((recipe) => (
          <button className="recipe-list-button" key={recipe.id} onClick={() => openRecipe(recipe.id)}>
            <strong>{recipe.name}</strong>
            <span>{recipe.recipe_type} • {recipe.source_type === "built_in" ? "Built-in" : recipe.source_type === "imported" ? "Imported" : "User Added"}</span>
          </button>
        ))}
      </section>
    </main>
  );
}
