export function SectionIntro({ eyebrow, title, body, actions }) {
  return (
    <section className="hero-panel">
      <div className="hero-copy">
        <span className="eyebrow">{eyebrow}</span>
        <h1>{title}</h1>
        <p>{body}</p>
        {actions ? <div className="hero-actions">{actions}</div> : null}
      </div>
      <div className="hero-console">
        <div className="console-headline">
          <span className="eyebrow">pipeline</span>
          <span>{">_"} operator view</span>
        </div>
        <pre>
{`agent/api
  -> normalize
  -> enrich
  -> detect
  -> correlate
  -> sqlite
  -> integrity
  -> API`}
        </pre>
      </div>
    </section>
  );
}
