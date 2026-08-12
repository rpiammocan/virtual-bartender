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
  if (page === "mybar") return <MyBarPage onHome={home} />;
  if (page === "tonight") return <TonightsBarPage onHome={home} />;
  if (page === "matches") return <MatchesPage onHome={home} />;
  if (page === "recipes") return <RecipesPage onHome={home} openRecipe={openRecipe} />;
  if (page === "recipe-detail" && recipeId !== null) return <RecipeDetailPage recipeId={recipeId} onHome={home} />;
  if (page === "shopping") return <ShoppingPage onHome={home} />;
  if (page === "favorites") return <FavoritesPage onHome={home} openRecipe={openRecipe} />;
  if (page === "history") return <HistoryPage onHome={home} />;
  if (page === "surprise") return <SurprisePage onHome={home} openRecipe={openRecipe} />;
  if (page === "import") return <ImportRecipePage onHome={home} openRecipe={openRecipe} />;
  if (page === "settings") return <SettingsPage onHome={home} />;

  return <HomePage navigate={setPage} />;
}
