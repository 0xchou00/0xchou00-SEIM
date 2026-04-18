import { documentationSections } from "../content/siteContent";

export function DocumentationPage() {
  return (
    <div className="page-stack">
      <section className="content-panel">
        <div className="panel-heading">
          <span className="eyebrow">documentation</span>
          <h1>Engineering references</h1>
        </div>
        <p className="support-copy">
          The canonical documentation lives in the repository and follows the runtime
          boundaries of the tool rather than marketing sections.
        </p>
      </section>

      <section className="content-panel">
        <div className="card-grid two-up">
          {documentationSections.map((section) => (
            <article className="info-card doc-card" key={section.title}>
              <h2>{section.title}</h2>
              <p>{section.body}</p>
              <a
                className="text-link"
                href={section.href}
                target="_blank"
                rel="noreferrer"
              >
                Open on GitHub
              </a>
            </article>
          ))}
        </div>
      </section>

      <section className="content-panel split-panel">
        <div>
          <div className="panel-heading">
            <span className="eyebrow">doc layout</span>
            <h2>Sectioning mirrors the code</h2>
          </div>
        </div>
        <div className="console-card">
          <pre>
{`docs/
  ARCHITECTURE.md
  DETECTION.md
  AGENT.md
  TESTING.md
  LAB.md
  LIMITATIONS.md`}
          </pre>
        </div>
      </section>
    </div>
  );
}
