# Project reconciliation implementation plan

> **For agentic workers:** Use systematic debugging and verification before completion. Independent backend, frontend, and infrastructure work follows the dispatching-parallel-agents skill; the root integrates and verifies.

**Goal:** Reconcile this checkout with the user's 41-phase project plan and repair verified defects.

**Architecture:** Preserve the supplied architecture. Separate repository implementation from live AWS acceptance; use dedicated test services and document remaining external prerequisites.

**Tech Stack:** FastAPI, React/TypeScript, PostgreSQL, Redis, Docker, AWS, Terraform, Ansible, Jenkins, Prometheus, Grafana, Fluent Bit, OpenSearch.

**Spec:** [Design](../specs/2026-09-23-project-reconciliation-design.md), [user requirements](../../project-requirements.txt).

## Global constraints

- Production deployment originates from main; images are immutable.
- No secrets in Git; no public database, Redis or application instances.
- Backup/restore and live production requirements remain unverified until actually demonstrated.
- No modifications to unrelated running containers or existing developer data.

## Review focus

- Expired, forged, reused or disabled-user tokens must not authorize access.
- Concurrent 401 responses must not cause repeated frontend refresh requests.
- Dependency failures must make readiness fail without leaking credentials.
- Failed migration/candidate/switch checks must retain or restore the previous application.
- Failed security tools or absent evidence must never be reported as successful validation.

## Tasks

- [x] Backend: reproduce startup failures; restore JWT helpers/model registry/database metrics; fix app initialization, auth/RBAC, error correlation, Redis readiness and isolated PostgreSQL tests. Verify complete pytest suite and migration round trip. Create production Dockerfile.
- [x] Frontend: reproduce TypeScript failures; implement missing service/deployment/incident/audit pages and registration; correct projects editing, auth imports/refresh, API errors and dashboard counts. Verify tests, lint and build. Create nonroot Nginx image.
- [x] Infrastructure: implement shared Terraform modules and three environments; validate encrypted state bootstrap, network boundaries, managed data, private EC2, ALB/TLS, ECR, secrets metadata and least privilege. Implement Ansible SSM configuration. Run format, init/validate and syntax checks without apply.
- [ ] Runtime: implement local and production Compose, Nginx security/rate limiting, runtime secret retrieval, immutable deployment metadata, blue/green gateway switch and rollback. Run Compose config and real local application smoke checks.
- [ ] Operations: implement metrics/logging/alerts/dashboards, CI security gates and artifact retention, backup/restore tools and failure-drill runbooks. Validate config and exercise safe local tests.
- [ ] Evidence: produce phase-by-phase checklist, architecture diagrams and README; record exact executed checks and remaining live prerequisites. Review integrated diff and rerun relevant checks.

## Recorded outcome

Application repair and static infrastructure work are verified. Runtime/operations completion is blocked by expired AWS authentication, Docker storage failure, historical-secret and backend-image security gates, and missing live Jenkins/staging/production evidence. See `docs/project-audit.md` and `docs/security-review.md`. No claim of full production completion is made.
