type Props = {
  title: string;
  onHome: () => void;
};

export default function AppHeader({ title, onHome }: Props) {
  return (
    <header className="app-header">
      <button className="link-button" onClick={onHome}>← Home</button>
      <h1>{title}</h1>
    </header>
  );
}
