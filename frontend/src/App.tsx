import { useState } from "react";
import HomePage from "./pages/HomePage";
import MyBarPage from "./pages/MyBarPage";
import TonightsBarPage from "./pages/TonightsBarPage";
import MatchesPage from "./pages/MatchesPage";
import RecipesPage from "./pages/RecipesPage";
import RecipeDetailPage from "./pages/RecipeDetailPage";
import ShoppingPage from "./pages/ShoppingPage";
import FavoritesPage from "./pages/FavoritesPage";
import HistoryPage from "./pages/HistoryPage";
import SurprisePage from "./pages/SurprisePage";
import ImportRecipePage from "./pages/ImportRecipePage";
import SettingsPage from "./pages/SettingsPage";

export default function App() {
  const [page, setPage] = useState("home");
  const [recipeId, setRecipeId] = useState<number | null>(null);

  function openRecipe(id: number) {
    setRecipeId(id);
    setPage("recipe-detail");
  }

  const home = () => setPage("home");

  if (page === "home") return <HomePage navigate={setPage} />;
  if (page === "mybar") return <div className="theme-mybar"><MyBarPage onHome={home} /></div>;
  if (page === "tonight") return <div className="theme-tonight"><TonightsBarPage onHome={home} /></div>;
  if (page === "matches") return <div className="theme-matches"><MatchesPage onHome={home} /></div>;
  if (page === "recipes") return <RecipesPage onHome={home} openRecipe={openRecipe} manageRecipes={() => setPage("import")} />;
  if (page === "recipe-detail" && recipeId !== null) return <div className="theme-recipes"><RecipeDetailPage recipeId={recipeId} onHome={() => setPage("recipes")} /></div>;
  if (page === "shopping") return <div className="theme-shopping"><ShoppingPage onHome={home} /></div>;
  if (page === "favorites") return <div className="theme-favorites"><FavoritesPage onHome={home} openRecipe={openRecipe} /></div>;
  if (page === "history") return <div className="theme-history"><HistoryPage onHome={home} /></div>;
  if (page === "surprise") return <div className="theme-surprise"><SurprisePage onHome={home} openRecipe={openRecipe} /></div>;
  if (page === "import") return <div className="theme-recipes"><ImportRecipePage onHome={() => setPage("recipes")} openRecipe={openRecipe} /></div>;
  if (page === "settings") return <div className="theme-settings"><SettingsPage onHome={home} /></div>;
  if (page === "display") return <div className="theme-display"><RecipesPage onHome={home} openRecipe={openRecipe} /></div>;

  return <HomePage navigate={setPage} />;
}
