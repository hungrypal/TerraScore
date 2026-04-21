const cards = [
  {
    title: "Repository",
    text: "Framework-based structure is now in place with frontend, backend, docs, schemas, and data folders."
  },
  {
    title: "Dataset",
    text: "Google Earth Engine access is blocked until student verification is completed."
  },
  {
    title: "Documentation",
    text: "ERD, flow, API docs, and schema definitions are committed and tracked."
  }
];

export default function App() {
  return (
    <div className="page">
      <header className="hero">
        <p className="eyebrow">TerraScore</p>
        <h1>AI-Powered Agricultural Credit Scoring</h1>
        <p className="subtitle">
          Geospatial scoring for project regions, backed by Earth observation data.
        </p>
      </header>

      <section className="grid">
        {cards.map((card) => (
          <article key={card.title} className="card">
            <h2>{card.title}</h2>
            <p>{card.text}</p>
          </article>
        ))}
      </section>
    </div>
  );
}
