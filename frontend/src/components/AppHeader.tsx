type Props = {
  title: string;
  onHome: () => void;
};

const pageIcons: Record<string, string> = {
  "What Can I Make?": "🍸",
  "Surprise Me": "🎲",
  "My Bar": "🍾",
  "Tonight's Bar": "🌙",
  "Recipes": "📖",
  "Favorites": "♥",
  "Shopping List": "🛒",
  "History": "◷",
  "Display Mode": "▣",
  "Settings": "⚙",
  "Admin / Settings": "⚙",
  "Import Recipe": "📜",
};

export default function AppHeader({ title, onHome }: Props) {
  return (
    <header className="app-header">
      <button className="back-button" onClick={onHome}>‹ Back</button>
      <div className="page-heading">
        <span className="page-heading-icon" aria-hidden="true">{pageIcons[title] || "🍸"}</span>
        <h1>{title}</h1>
      </div>
    </header>
  );
}
