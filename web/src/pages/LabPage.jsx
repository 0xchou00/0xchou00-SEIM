import { labWorkflow } from "../content/siteContent";

export function LabPage() {
  return (
    <div className="page-stack">
      <section className="content-panel">
        <div className="panel-heading">
          <span className="eyebrow">lab</span>
          <h1>Local attack simulation workflow</h1>
        </div>
        <p className="support-copy">
          The lab uses Docker Compose with three roles: attacker, victim, and SIEM. The
          victim writes real SSH and Nginx logs into a shared volume, and the SIEM agent
          tails those logs into the same ingest API used outside the lab.
        </p>
      </section>

      <section className="content-panel">
        <div className="workflow-grid">
          {labWorkflow.map((item) => (
            <article className="workflow-card" key={item.step}>
              <span>{item.step}</span>
              <h2>{item.title}</h2>
              <p>{item.body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="content-panel split-panel">
        <div>
          <div className="panel-heading">
            <span className="eyebrow">scenarios</span>
            <h2>Shipped attack paths</h2>
          </div>
          <ul className="signal-list">
            <li>SSH brute-force attempts against the victim container</li>
            <li>Directory scans against sensitive HTTP paths</li>
            <li>High request flood for rate-based detections</li>
          </ul>
        </div>
        <div className="console-card">
          <pre>
{`docker compose -f lab/docker-compose.yml up -d
./scripts/simulate_ssh_attack.sh
./scripts/simulate_web_scan.sh scan
curl http://127.0.0.1:8000/alerts`}
          </pre>
        </div>
      </section>
    </div>
  );
}
