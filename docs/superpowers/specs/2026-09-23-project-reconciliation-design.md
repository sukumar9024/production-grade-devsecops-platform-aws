# Project reconciliation design

The user supplied the architecture and authorized implementing missing requirements and fixing errors. Preserve FastAPI, React, PostgreSQL, Redis, Docker, private EC2, Terraform, Ansible, Jenkins, Prometheus, Grafana, Fluent Bit and OpenSearch. The authoritative scope is [project-requirements.txt](../../project-requirements.txt).

Repair the application before deployment automation. Use dedicated disposable services for tests, never the developer's existing database. Keep frontend and backend interfaces aligned with existing `/api/v1` routes. Require both PostgreSQL and Redis for readiness.

Provide a reproducible local Compose stack and separate AWS runtime configuration. Production uses immutable image digests, two local deployment slots behind a stable gateway, serialized deployments, migration-before-switch, candidate health and smoke tests, and restoration of the previous gateway on failure. Schema changes must remain backward compatible; an application rollback does not reverse database migrations.

Provision dev, staging and production through shared Terraform modules and separate encrypted, locked states. EC2, PostgreSQL and Redis remain private. TLS terminates at an ACM-backed ALB. Configuration reaches private instances via Ansible over Systems Manager. Secret values are read at runtime, excluded from source control, and never printed in CI.

Central monitoring and logging are opt-in locally because they need substantial memory. The Linux observability stack has explicit retention, dashboards, alert rules, and a configurable notification receiver. CI must fail closed on tests/security gates and require explicit production approval after staging verification.

Completion requires evidence. No AWS apply, public DNS change, production interruption or destructive drill is implied by local validation. Live acceptance requires the user's intended account/domain and a reviewed resource plan. Every unexecuted scan or drill remains pending in the audit.
