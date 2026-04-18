import { Link } from "react-router-dom";
import {
  architectureFlow,
  featureCards,
  identity,
} from "../content/siteContent";
import { SectionIntro } from "../components/SectionIntro";

export function HomePage() {
  return (
    <div className="page-stack">
      <SectionIntro
        eyebrow="tool overview"
        title={identity.name}
        body="The tool ingests SSH and web access logs, normalizes them into one event schema, enriches source IPs, applies stateful detectors, correlates related alerts, and stores the result in SQLite with a hash-linked integrity trail."
        actions={
          <>
            <Link className="button button-primary" to="/features">
              Inspect features
            </Link>
            <Link className="button button-secondary" to="/lab">
              Open lab workflow
            </Link>
          </>
        }
      />

      <section className="content-panel">
        <div className="panel-heading">
          <span className="eyebrow">what it does</span>
          <h2>Operational scope</h2>
        </div>
        <p className="support-copy">{identity.tagline}</p>
        <div className="card-grid four-up">
          {featureCards.map((card) => (
            <article className="info-card" key={card.title}>
              <h3>{card.title}</h3>
              <p>{card.body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="content-panel split-panel">
        <div>
          <div className="panel-heading">
            <span className="eyebrow">architecture</span>
            <h2>Pipeline order is fixed</h2>
          </div>
          <p className="support-copy">
            Every stage depends on the previous one. Correlation does not inspect raw logs.
            It evaluates stored detector alerts. Integrity is applied after persistence so
            the API exposes records that can be checked against the local chain.
          </p>
        </div>
        <div className="flow-panel">
          {architectureFlow.map((step, index) => (
            <div className="flow-step" key={step}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <strong>{step}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="content-panel split-panel">
        <div>
          <div className="panel-heading">
            <span className="eyebrow">key features</span>
            <h2>Built for a small, inspectable deployment model</h2>
          </div>
        </div>
        <ul className="signal-list">
          <li>FastAPI backend with a single SQLite data store</li>
          <li>Stateful SSH and web detectors with YAML-backed rules</li>
          <li>Optional IP enrichment and post-alert correlation</li>
          <li>Hash-linked event and alert integrity verification</li>
        </ul>
      </section>
    </div>
  );
}
