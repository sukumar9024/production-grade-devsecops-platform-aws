# Incident response and controlled failure drills

Use SSM for private host access. Record incident start, symptoms, current release SHA, affected environment, request IDs and each recovery action. Do not paste credentials, environment files or bearer tokens into incident reports.

| Symptom | Investigate | Recover and verify |
|---|---|---|
| Application unavailable | ALB target health, gateway config, slot container health, readiness dependencies | Restore last healthy release or recover dependency; rerun authenticated smoke |
| Database unavailable | RDS status/events, connections, SG rules, TLS trust and secret rotation | Restore connectivity or execute reviewed RDS recovery; verify readiness and critical queries |
| High CPU | Host/container metrics, traffic, slow requests/query duration | Remove load source or scale after diagnosis; verify latency and error rate |
| Disk nearly full | Filesystem metric, bounded Docker logs, Fluent Bit buffer and Prometheus retention | Remove identified disposable caches or expand storage; never delete DB volumes blindly |
| Deployment failure | `.runtime/last-attempt.json`, current/previous metadata, pipeline artifacts | Confirm rollback result on each host and public smoke; reconcile partial rollouts |
| Invalid secrets | Secret version/access, URL encoding, TLS verification, token expiry | Rotate/retrieve correct values and redeploy; verify old credentials no longer authorize |
| Missing logs/alerts | Fluent Bit buffer/output errors, OpenSearch access/retention, Prometheus targets/rules, Alertmanager receiver | Restore delivery and execute a synthetic test; record receipt and resolution |

Run failure drills in disposable staging, one at a time with a recovery owner. Record actual detection time, notification receipt, recovery action and verification; configuration files alone are not evidence.

- Stop a backend container and verify restart/alert behavior.
- Stop the backend service and separately block database access; readiness must return 503 and the probe must alert.
- Generate bounded CPU load and fill a dedicated small test filesystem (never the real root filesystem); confirm threshold alerts.
- Deploy an intentionally unhealthy disposable image; verify the prior release remains reachable and recorded metadata does not advance.
- Supply invalid JWT/Redis/DB secrets to an isolated candidate; verify it cannot become healthy/active.
- Restore a backup using the backup runbook and compare data.

These live production-style failure drills remain pending. Backend automated tests cover failed DB/Redis readiness and invalid/expired/disabled-user tokens; deployment unit tests cover candidate and gateway failures. Those tests do not demonstrate real alert delivery or AWS rollback.
