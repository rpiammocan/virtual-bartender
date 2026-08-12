type Props = {
  navigate: (page: string) => void;
};

const actions = [
  ["What Can I Make?", "Find drinks based on your current bar", "matches"],
  ["Surprise Me", "Random makeable drink selection", "surprise"],
  ["My Bar", "Manage your permanent inventory", "mybar"],
  ["Tonight's Bar", "Create and manage bar sessions", "tonight"],
  ["Recipes", "Browse and search recipes", "recipes"],
  ["Shopping List", "Manage what to buy", "shopping"],
  ["Favorites", "Your saved drinks", "favorites"],
  ["History", "Drinks you confirmed making", "history"],
  ["Import Recipe", "Import a recipe from a URL", "import"],
  ["Settings", "Backups and application settings", "settings"],
];

export default function HomePage({ navigate }: Props) {
  return (
    <main className="page">
      <header className="hero">
        <p className="eyebrow">Offline-first</p>
        <h1>Virtual Bartender</h1>
        <p className="subtitle">What would you like to do?</p>
      </header>

      <section className="home-grid" aria-label="Main actions">
        {actions.map(([title, description, target]) => (
          <button className="home-card" key={title} onClick={() => navigate(target)}>
            <strong>{title}</strong>
            <span>{description}</span>
          </button>
        ))}
      </section>
    </main>
  );
}
