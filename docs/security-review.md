# Security review — 2026-09-24

The production release gate is **blocked**. Repository changes do not establish production readiness.

| Check | Observed result | Action |
|---|---|---|
| Backend dependency audit | No known vulnerabilities in pinned runtime requirements | Rerun on every build |
| npm audit | Zero reported vulnerabilities | Rerun on every build |
| Trivy filesystem | Zero HIGH/CRITICAL findings after upgrading Ansible core to 2.19.13 | Keep pinned tooling current |
| Trivy IaC | Zero unsuppressed HIGH/CRITICAL findings | Two narrow architecture exceptions below |
| Semgrep | Zero blocking findings; one partial-parse warning on Python 3.14 exception syntax | Converted to scanner-compatible syntax; strict rescan blocked by Docker storage |
| Backend image | 63 HIGH/CRITICAL package/CVE findings in Debian 12 base | Rebase/update, rebuild, validate and rescan; do not bypass gate |
| Frontend image | Not reached after backend image gate failed | Run after Docker recovery |
| Staged source snapshot | No leaks found with checksum-verified native Gitleaks 8.30.1 | Private runtime files excluded |
| Git history | One historical secret in `backend/.env.example` | Rotate every deployment that used it; reviewed history cleanup/baseline decision remains |
| ZAP | Staging scan not run | Requires reachable staging HTTPS and credentials |

The old example JWT secret was removed from the current template. It matched the local `backend/.env`, which was rotated to a fresh random value (the private file is not committed). Existing signed access/refresh tokens from that secret become invalid after process restart. No claim is made that an unknown external deployment was rotated. The local backend process was not restarted because Docker recovery was declined. History was not rewritten and the finding is deliberately not allowlisted. Jenkins must continue to fail its history gate until this is resolved through the repository owner's rotation/history procedure.

The image report contains repeated CVEs across Debian packages, including util-linux, perl, ncurses, SQLite, zlib and PCRE2; 63 is the package/finding count, not 63 distinct exploitable paths. Most entries had no vendor fix version in the scan. Reachability/exploitability was not established. The backend image was not silently marked safe with `--ignore-unfixed`. A base-image change still needs runtime tests and a clean scan. Docker's metadata storage became read-only after host disk exhaustion during observability pulls; the user requested leaving Docker running, so no restart or further image mutation was attempted.

## Scoped scan decisions

- `AWS-0053` is suppressed only on the public ALB resource because public HTTPS is an explicit requirement. Its targets and databases remain private.
- `AWS-0104` is suppressed only on private app/Jenkins outbound TCP443, used for SSM, ECR, AWS APIs and package repositories through NAT. This grants no inbound access.
- The Semgrep subprocess warning on `scripts/dast.py` is suppressed at one call: a validated HTTPS URL is passed as a single element of a fixed Docker argument array; no shell executes the input.

S3 application and transfer buckets were changed to customer-managed KMS encryption. The application IAM role receives only S3-mediated access to its own bucket's key. SNS notifications have a rotating KMS key with a CloudWatch publisher grant. Actual AWS IAM/KMS execution still needs live verification.

Remaining hardening: separate RDS application/migration DB users (the supplied runtime currently uses the managed master login), configure trusted CI roles and Jenkins, verify webhook delivery, install OpenSearch retention, review medium-severity reports, and test invalid-secret/failure recovery. Do not publish the project as production-complete until these and the acceptance checklist pass.
