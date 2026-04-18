export const primaryNav = [
  { to: "/", label: "Home" },
  { to: "/features", label: "Features" },
  { to: "/documentation", label: "Documentation" },
  { to: "/lab", label: "Lab" },
  { to: "/about", label: "About" },
];

export const identity = {
  name: "0xchou00 — Lightweight Security Detection Tool",
  tagline: "Local logs. Typed events. Bounded detections.",
};

export const featureCards = [
  {
    title: "Detection engine",
    body:
      "Stateful SSH and web detectors run on normalized events, then hand derived alerts to rule-based correlation.",
  },
  {
    title: "IP enrichment",
    body:
      "Events gain country, blacklist, and cached reputation context before severity is assigned or correlation rules run.",
  },
  {
    title: "Correlation layer",
    body:
      "Alert combinations are evaluated in bounded time windows so short attack sequences are visible without a separate analytics stack.",
  },
  {
    title: "Integrity chain",
    body:
      "Every stored event and alert is sealed into a hash-linked record chain and revalidated through the API.",
  },
];

export const architectureFlow = [
  "raw logs",
  "normalization",
  "enrichment",
  "detection",
  "correlation",
  "storage",
  "API",
];

export const documentationSections = [
  {
    title: "Architecture",
    href: "https://github.com/0xchou00/0xchou00-SEIM/blob/main/docs/ARCHITECTURE.md",
    body:
      "Pipeline order, data flow, in-process detector state, and the separation between event detection and alert correlation.",
  },
  {
    title: "Detection",
    href: "https://github.com/0xchou00/0xchou00-SEIM/blob/main/docs/DETECTION.md",
    body:
      "Thresholds, windows, aggregation logic, anomaly baselines, and why each detector is implemented the way it is.",
  },
  {
    title: "Agent",
    href: "https://github.com/0xchou00/0xchou00-SEIM/blob/main/docs/AGENT.md",
    body:
      "Offset persistence, batching, retry behavior, and the trust boundary between the collector and the backend.",
  },
  {
    title: "Lab",
    href: "https://github.com/0xchou00/0xchou00-SEIM/blob/main/docs/LAB.md",
    body:
      "Container topology, local attack scenarios, and the expected alerts for brute-force and scanning workflows.",
  },
  {
    title: "Limitations",
    href: "https://github.com/0xchou00/0xchou00-SEIM/blob/main/docs/LIMITATIONS.md",
    body:
      "Operational limits of a single-node design: no distributed ingestion, no shared detector state, and polling-based UI access.",
  },
];

export const detectionItems = [
  {
    title: "SSH brute force",
    body:
      "Counts failed SSH authentications per source IP over a 60-second sliding window and escalates when the threshold is reached repeatedly or the source is already flagged.",
    detail: "Default threshold: 5 failures in 60 seconds.",
  },
  {
    title: "Suspicious web behavior",
    body:
      "Tracks request rate, HTTP error ratio, and access to sensitive paths such as `/.env` or `/phpmyadmin`.",
    detail: "Sensitive-path probes are treated as high-signal even at low request volume.",
  },
  {
    title: "YAML rules",
    body:
      "Runs field matches and bounded aggregations from `rules/default_rules.yml` so new detections can be added without changing detector code.",
    detail: "Supports exact match, contains, regex, and time-window aggregation.",
  },
  {
    title: "Frequency anomaly",
    body:
      "Builds a rolling baseline per source type and IP, then raises an alert when the current bucket materially exceeds recent traffic history.",
    detail: "This is deterministic spike detection, not model inference.",
  },
];

export const enrichmentItems = [
  "Local blacklist hits are applied synchronously before remote lookups.",
  "GeoIP is optional and local-first when a MaxMind-compatible database exists.",
  "External reputation lookups are cached so ingest latency stays bounded.",
];

export const correlationItems = [
  "Correlation runs after detector alerts are stored.",
  "Rules are defined in `rules/correlation_rules.yml`.",
  "Derived alerts are written back into the same alerts table and exposed through the same API.",
];

export const labWorkflow = [
  {
    step: "01",
    title: "Launch the lab",
    body:
      "Docker Compose starts an attacker, a victim running SSH and Nginx, and a SIEM container running both the backend and the ingestion agent.",
  },
  {
    step: "02",
    title: "Generate traffic",
    body:
      "Shell scripts trigger SSH login failures, directory probes, or a request flood from the attacker container.",
  },
  {
    step: "03",
    title: "Collect victim logs",
    body:
      "The victim writes auth and access logs into a shared volume that the SIEM agent tails in near real time.",
  },
  {
    step: "04",
    title: "Verify output",
    body:
      "Use `/alerts`, `/logs`, and `/integrity/verify` to confirm the detectors, correlation rules, and storage path are behaving as expected.",
  },
];

export const profile = {
  name: "Omar Chouhani",
  handle: "0xchou00",
  bio:
    "Network security engineering student focused on building detection workflows that are easy to inspect, test, and operate on one host.",
  focus: [
    "SOC operations",
    "Blue team workflows",
    "Detection engineering",
  ],
  interests: [
    "SIEM internals",
    "Detection pipelines",
    "Network security",
  ],
  github: "https://github.com/0xchou00",
  linkedin: "https://www.linkedin.com/in/placeholder",
};
