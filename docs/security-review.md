# Security review — 2026-09-24

Container remediation is implemented and awaiting the new GitHub Security workflow's built-image scans and runtime smoke checks. Repository changes alone do not establish production readiness.

| Check | Observed result | Action |
|---|---|---|
| Backend dependency audit | No known vulnerabilities in pinned runtime requirements | Rerun on every build |
| npm audit | Zero reported vulnerabilities | Rerun on every build |
| Trivy filesystem | Zero HIGH/CRITICAL findings after upgrading Ansible core to 2.19.13 | Keep pinned tooling current |
| Trivy IaC | Zero unsuppressed HIGH/CRITICAL findings | Two narrow architecture exceptions below |
| Semgrep | Zero blocking findings; one partial-parse warning on Python 3.14 exception syntax | Converted to scanner-compatible syntax; strict rescan blocked by Docker storage |
| Backend image | Previous Debian 12 image had 63 HIGH/CRITICAL package/CVE findings | Rebased to digest-pinned Python 3.14.7/Alpine 3.23, vendor packages updated, pip/ensurepip removed from runtime; built-image scan pending |
| Frontend and gateway images | Updated to digest-pinned Nginx 1.30.5 with vendor package updates | Gateway reuses the scanned frontend image; built-image scan pending |
| Staged source snapshot | No leaks found with checksum-verified native Gitleaks 8.30.1 | Private runtime files excluded |
| Git history | Passes with one narrowly documented retired-secret fingerprint | Reintroduction regression test confirms that a new occurrence still fails |
| ZAP | Staging scan not run | Requires reachable staging HTTPS and credentials |

The repository owner confirmed that the application has only run locally, with no external deployment using the old example JWT. The private `backend/.env` was previously rotated; both current local env files and the running application container were checked and do not use the retired value. Startup now rejects its SHA256 fingerprint in every environment. The exposed value is not reproduced in current source or tests.

`.gitleaksignore` records only `a9bb74f641db1473d19f98c65adeb4f4e3384a6a:backend/.env.example:generic-api-key:9`. This is an explicitly retired historical credential, not a path-wide/rule-wide exclusion. Gitleaks still scans full history; a regression check recreated the leak in a new temporary Git repository and confirmed it fails. History and branch ancestry have not been rewritten, and no force push is needed. This exception does not authorize reuse of that credential.

The original Debian report contains repeated CVEs across util-linux, perl, ncurses, SQLite, zlib and PCRE2; 63 is a package/finding count, not 63 distinct exploitable paths. Most had no vendor fix for that Debian release. The replacement supported Alpine base removes that package set. Native registry scans found vulnerable pip-vendored tooling in Python's base and an Expat update needed in Nginx's base; the Dockerfiles remove runtime packaging tools and install vendor updates. No `--ignore-unfixed`, severity reduction or CVE allowlist is used. Both image scans run even when one fails.

The GitHub Security workflow builds linux/amd64 images, scans their actual contents, and starts disposable PostgreSQL/Redis plus the application and gateway to verify registration, login, readiness, a database-backed API and logout. Source jobs run strict Semgrep, dependency, filesystem, IaC and full-history secret checks. Local Docker storage remains unrepaired at the user's request; its daemon and existing containers were not restarted.

## Scoped scan decisions

- `AWS-0053` is suppressed only on the public ALB resource because public HTTPS is an explicit requirement. Its targets and databases remain private.
- `AWS-0104` is suppressed only on private app/Jenkins outbound TCP443, used for SSM, ECR, AWS APIs and package repositories through NAT. This grants no inbound access.
- The Semgrep subprocess warning on `scripts/dast.py` is suppressed at one call: a validated HTTPS URL is passed as a single element of a fixed Docker argument array; no shell executes the input.

S3 application and transfer buckets were changed to customer-managed KMS encryption. The application IAM role receives only S3-mediated access to its own bucket's key. SNS notifications have a rotating KMS key with a CloudWatch publisher grant. Actual AWS IAM/KMS execution still needs live verification.

Remaining hardening: separate RDS application/migration DB users (the supplied runtime currently uses the managed master login), configure trusted CI roles and Jenkins, verify webhook delivery, install OpenSearch retention, review medium-severity reports, and test invalid-secret/failure recovery. Do not publish the project as production-complete until these and the acceptance checklist pass.
