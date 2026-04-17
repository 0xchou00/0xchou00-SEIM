# 0xchou00 platform: engineering a branded SIEM instead of shipping another generic demo

## Introduction

There are a lot of cybersecurity projects that say “SIEM” but stop at a parser, a few hard-coded rules, and a generic admin dashboard. I wanted a different result.

I wanted a platform that was:

- technically coherent
- visually distinct
- installable by a Linux user with no prior context
- aligned with my own engineering identity

That became **0xchou00 platform**.

The project combines a real detection pipeline with a strict visual system built around a cyber-terminal aesthetic: black background, white primary text, neon green accenting, and a CRT mascot carrying the `[0xchou00]` signature.

## Why the identity mattered

Branding is often treated as decoration. In this project it was structural.

I wanted the repository, the dashboard, the landing page, the README, the deployment assets, and the publication material to feel like parts of the same system. That forced me to clean up inconsistencies that usually survive in technical projects:

- naming drift
- documentation tone mismatch
- frontend/backend disconnect
- “temporary” visuals that become permanent

The identity layer improved the engineering layer because it forced consistency.

## Core architecture

The architecture stays intentionally direct:

1. ingest raw SSH or web logs
2. normalize them into structured events
3. evaluate the detection stack
4. persist logs and alerts
5. append them to an integrity chain
6. expose the results through API and dashboard

That simplicity is important. A SIEM project becomes much more valuable when the path from raw log line to alert is traceable.

## Normalization as the control point

The platform normalizes SSH and web logs into a shared event structure before detection starts.

That matters because detectors should operate on intent-level fields:

- source IP
- event type
- username
- HTTP method
- path
- status

Once those fields are stable, the detection engine becomes source-aware only where it needs to be, rather than source-coupled everywhere.

## Detection design

### Heuristic detectors

Two detectors are intentionally direct:

- SSH brute-force detection
- suspicious web-source detection

The brute-force detector uses a rolling time window keyed by source IP. The suspicious-IP detector looks for:

- bursty request rates
- abnormal HTTP error ratios
- sensitive path access

These are explainable and operationally useful.

### YAML detection rules

I added a YAML rule layer because custom detection content should not require Python edits every time.

Rules support:

- source and event matching
- direct field comparison
- substring matching
- regex matching
- windowed aggregation by grouping field

That makes the platform more realistic from a detection-engineering perspective. Analysts and engineers can extend logic without reopening core modules.

### Real anomaly detection

I did not want fake “AI” in this project.

The anomaly detector is frequency-based. It monitors event volume from each source over fixed windows, maintains a short baseline history, and alerts when the current count materially exceeds prior behavior.

This approach is simple, testable, and honest. It solves a real problem without pretending to be something else.

## Integrity as a first-class feature

One of the strongest parts of the project is the integrity chain.

Each persisted log and each persisted alert is:

- hashed
- linked to the previous entry
- stored with chain metadata

Verification recalculates:

- chain linkage
- entry hashes
- current payload hashes from the database

That means the platform can detect tampering not only in the chain itself, but also in the live stored entities.

For a SIEM-oriented project, that matters. Security telemetry is more credible when its persistence model can defend itself.

## Frontend transformation

The UI changed from a simple dashboard into a complete branded surface:

- landing page at `/`
- dashboard at `/dashboard`
- CRT mascot as the visual anchor
- terminal typography and neon-green styling

This was not just for aesthetics. It created:

- a clearer first impression
- a stronger repository identity
- a more memorable project story for portfolio and GitHub presentation

The dashboard still stays simple:

- live logs stream
- alerts feed
- severity, source, and time filters
- API-key session input

No frontend framework was necessary for that scope, and plain HTML/CSS/JS kept the delivery fast to install and easy to audit.

## Linux operator experience

A project like this only becomes credible when someone else can run it.

That is why finalization mattered as much as feature work:

- `install.sh` prepares the environment
- `.env` is generated with sensible defaults
- systemd runs the platform as a service
- `README.md` explains architecture and usage
- `TESTING.md` walks through brute-force and rule simulations

The result is a project that a Linux user can actually pick up and operate.

## Developer identity

This platform is also personal by design.

I wanted it to clearly represent:

- Omar CHOUHANI
- cybersecurity engineering student
- focused on SOC, SIEM, and detection engineering
- building under the `0xchou00` identity

That alignment between engineering and authorship is important. Strong projects do not only prove technical skill. They also prove ownership and point of view.

## Closing

0xchou00 platform is not trying to imitate a giant enterprise SIEM feature for feature.

It is trying to do something more honest and, for a portfolio, more useful:

- show a real detection pipeline
- show practical defensive engineering
- show tamper-evident telemetry handling
- show installable operator workflows
- show a strong identity carried consistently across the whole project

GitHub:
https://github.com/0xchou00
