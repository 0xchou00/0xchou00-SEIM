import {
  correlationItems,
  detectionItems,
  enrichmentItems,
} from "../content/siteContent";

export function FeaturesPage() {
  return (
    <div className="page-stack">
      <section className="content-panel">
        <div className="panel-heading">
          <span className="eyebrow">features</span>
          <h1>Detection and storage components</h1>
        </div>
        <p className="support-copy">
          The tool stays small by separating event detectors, alert correlation, and
          persistence responsibilities instead of pushing every decision into one layer.
        </p>
      </section>

      <section className="content-panel">
        <div className="panel-heading">
          <span className="eyebrow">detection engine</span>
          <h2>Stateful detectors</h2>
        </div>
        <div className="card-grid two-up">
          {detectionItems.map((item) => (
            <article className="info-card" key={item.title}>
              <h3>{item.title}</h3>
              <p>{item.body}</p>
              <code className="inline-note">{item.detail}</code>
            </article>
          ))}
        </div>
      </section>

      <section className="content-panel split-panel">
        <div>
          <div className="panel-heading">
            <span className="eyebrow">enrichment</span>
            <h2>Context before severity</h2>
          </div>
          <p className="support-copy">
            Enrichment happens before detector logic so blacklist and reputation context can
            influence severity without turning the detectors into network clients.
          </p>
        </div>
        <ul className="signal-list">
          {enrichmentItems.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="content-panel split-panel">
        <div>
          <div className="panel-heading">
            <span className="eyebrow">correlation</span>
            <h2>Alert-level joins</h2>
          </div>
          <p className="support-copy">
            Correlation operates on recent detector alerts rather than raw events. That keeps
            the event path predictable and makes the resulting correlations queryable through
            the same alert API.
          </p>
        </div>
        <ul className="signal-list">
          {correlationItems.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="content-panel split-panel">
        <div>
          <div className="panel-heading">
            <span className="eyebrow">integrity chain</span>
            <h2>Local tamper evidence</h2>
          </div>
        </div>
        <div className="console-card">
          <p>
            Persisted events and alerts are written into a hash-linked chain. Verification
            replays stored payload hashes against the current database state and returns the
            current chain head through the API.
          </p>
          <pre>{`GET /integrity/verify\n-> valid\n-> entries\n-> chain_head`}</pre>
        </div>
      </section>
    </div>
  );
}
