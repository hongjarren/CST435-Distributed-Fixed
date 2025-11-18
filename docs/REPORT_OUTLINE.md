# CST 435 Distributed Experiment — Report Outline (≤ 10 pages)

This outline maps directly to your assignment objectives and report guidelines. Keep prose concise and use figures/tables to stay within the page limit.

## Mapping to Guidelines
- Motivation/problem → Section 2
- Activities (installation, task division) → Sections 3 and 11
- Algorithm/codes → Sections 5 and 6 (with code refs)
- Deployment environment (# machines) → Section 7
- Output → Section 9
- Findings/experiences → Section 10
- Attach source code → Section 13 (Appendix or repo links)
- References → Section 12

## Page Budget (suggested)
- 1: Executive Summary — 0.5 page
- 2: Motivation & Problem — 0.5 page
- 3: Background & Technologies — 0.5–1 page
- 4: System Design — 1–1.5 pages
- 5: Implementation (gRPC + RMI) — 1–1.5 pages
- 6: Environment & Deployment — 0.75 page
- 7: Experiment Methodology — 1 page
- 8: Results — 1–1.5 pages
- 9: Discussion — 0.75–1 page
- 10: Conclusion & Future Work — 0.5 page
- 11: Team & Task Division — 0.5 page
- 12: References — 0.25 page
- 13: Appendix (optional, may be excluded from page count)

> Tip: If the 10-page cap is strict including everything, shrink Section 3 and move details into Appendix.

---

## 1. Executive Summary
- Objective: Install and use Docker with gRPC (Python) and RMI (Java) to solve a multi-invocation problem, and compare single-node vs distributed performance.
- Approach: Implement and evaluate a 5-stage business-logic pipeline across both stacks and deployments. The services perform realistic operations:
  - Service A — Inventory: value + 100
  - Service B — Sales tax: int(value × 1.15)
  - Service C — Shipping: 50 + (value // 10)
  - Service D — Processing fee: int(value × 1.025)
  - Service E — Currency rounding: (value // 5) × 5
- Headline Result (example run): For input 5, pipeline yields final result 60 (5 → 105 → 120 → 62 → 63 → 60).
- Key Findings (example local run; replace with your measured data):
  - gRPC (300 req, concurrency 10, work_ms=10): Total time ≈ 1.76s, avg RTT ≈ 58ms.
  - RMI  (300 req, concurrency 10, work_ms=10): Total time ≈ 1.97s, avg RTT ≈ 66ms.

## 2. Motivation & Problem Statement
- Why distributed invocation? Real-time processing, scalability, latency trade-offs.
- Problem definition: Compute/transform/aggregate pipeline with multiple RPCs; need to compare single-node vs multi-node/container performance.

## 3. Background & Technologies
- Docker: containerization for reproducible deployments.
- gRPC: IDL-first RPC (Protocol Buffers), bidirectional streaming (if used), client/server stubs.
- Java RMI: Java-native remote invocation for comparison.
- MapReduce/pipeline pattern context (brief).

## 4. System Design
- Architecture overview diagram: client → Service A → Service B → Service C → Service D → Service E.
- Sequence diagram or call flow: request/response across A/B/C/D/E. Each stage implements a distinct business operation (Inventory, Tax, Shipping, Fee, Round), making the flow resemble a compact commerce/invoicing pipeline.
- Data model/API summary: `Grpc/proto/compute.proto` messages and RPCs; RMI interface. All services exchange integers and accept `work_ms` to simulate server-side work.
- Work simulation knobs: `work_ms` delay; client-side `concurrency` and `requests`.

## 5. Implementation Summary (gRPC and RMI)
- gRPC (Python):
  - Server: `Grpc/server/main.py` implements the five service methods with the operations above. Environment: `SERVICE_NAME` (A–E), `PORT` (default 50051).
  - Client: `Grpc/client/main.py` executes A→B→C→D→E, writes per-request CSV, prints summary (total, time, avg/min/max RTT).
  - Proto/stubs: `Grpc/proto/compute.proto` defines `Compute`, `Transform`, `Aggregate`, `Refine`, `Finalize`.
- RMI (Java):
  - Interface/impl: `RMI/src/main/java/com/cst435/ComputeService*.java` implements the same five-stage semantics.
  - Server bootstrap: `ComputeServer.java` binds services A–E to registry 1099.
  - Load tester: `LoadTestClient.java` drives the pipeline and writes CSV/summary.
- Notable design choices: keep types simple (ints) for apples-to-apples comparison; use `work_ms` to control server work; identical client load parameters across stacks.

## 6. Environment & Deployment
- Hardware: CPU, RAM, network (Wi‑Fi/LAN), OS versions.
- Software: Python 3.11 venv; Maven/Java 11; Docker & Compose versions.
- Local (compose) vs Distributed (multiple hosts): IPs, ports, firewall rules.
- Commands used (brief): activation, build, run. Link to Appendix for full commands.

## 7. Experiment Methodology
- Variables: number of requests, concurrency, `work_ms`, payload size (if varied).
- Scenarios: single machine vs multiple machines/containers; gRPC vs RMI.
- Runs: trial count, warm-up, how timing is measured (send_ts/recv_ts, RTT).
- Metrics: RTT (avg/min/max), throughput (req/s), resource usage (optional).
- Validity: controlling noise, repeated runs, outlier handling.

## 8. Results
- Tables: summary stats per scenario (single-node vs distributed, gRPC vs RMI).
- Figures: bar/line charts for RTT and throughput; error rate if applicable.
- Representative logs/CSV snippet: paths to CSVs. Example first row (input=5):

  input,computed,transformed,aggregated,refined,final_result,...
  5,105,120,62,63,60,...

This reflects the updated business-logic pipeline and the final result 60.

## 9. Discussion
- Interpretation: when/why distributed helps; overheads (network, Docker).
- gRPC vs RMI comparison: portability, performance, developer experience.
- Bottlenecks and scaling behavior; limitations and threats to validity.

## 10. Conclusion & Future Work
- What was learned; practical recommendations.
- Next steps: streaming RPCs, batching, autoscaling, observability.

## 11. Team & Task Division
- Roles and responsibilities; who did what (installation, coding, experiments, analysis, documentation, video).
- Timeline and collaboration tools.

## 12. References
- gRPC docs, Protocol Buffers, RMI docs, Docker docs, any tutorials/labs used.

## 13. Appendix (optional)
- A. Setup & Commands
  - Python venv and installs.
  - Docker build/compose and distributed run commands.
  - Firewall rules and connectivity checks.
- B. Configuration
  - `docker-compose.yml` (local), env vars.
  - `proto/compute.proto` and service endpoints.
- C. Raw Results
  - Full CSV files, run logs.
- D. Source Code Links
  - Repo structure and key file paths.

---

## Figures & Tables (suggested)
- Fig 1: Architecture (client → A → B → C → D → E).
- Fig 2: Sequence diagram of RPC invocations across 5 services.
- Fig 3: Average RTT by scenario (single vs multi; gRPC vs RMI).
- Fig 4: Throughput vs concurrency.
- Table 1: Environment matrix (hardware/software versions).
- Table 2: Experiment matrix (scenarios × variables × runs).
