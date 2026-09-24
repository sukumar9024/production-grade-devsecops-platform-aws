# Continuous integration and release gates

## GitHub Actions

`.github/workflows/ci.yml` validates pushes and pull requests targeting `develop` or `main` on Ubuntu 24.04. Backend checks use Python 3.14, development dependencies, disposable PostgreSQL and Redis services, Ruff, ORM registration, Alembic migrations and the full pytest suite. Frontend checks use Node 24.15.0 and the committed npm lockfile, then run lint, tests and a production build. A third job tests deployment failure handling and AWS runtime configuration and checks operational script syntax. Test results and the frontend build are uploaded as artifacts. CI service passwords are disposable test values; no AWS credentials or deployment are involved.

The original develop run failed before tests because the branch lacked the frontend lockfile and complete backend implementation. Consolidating the application branches supplies those files. The workflow now also installs `requirements-dev.txt` and provides Redis for readiness tests. Pinning Ubuntu 24.04 avoids the announced `ubuntu-latest` image migration affecting this workflow.

`.github/workflows/security.yml` adds full-history secret scanning, strict Semgrep, dependency/filesystem/IaC security checks, Docker builds and HIGH/CRITICAL image gates. It starts the built images with disposable PostgreSQL/Redis and verifies authenticated application behavior through the gateway. Both image reports are retained even if one fails. This workflow runs on pushes/PRs, manual dispatch and a weekly schedule on the default branch; enable it on the protected release branch as well. Configure both workflows' checks as required in repository rules. Neither workflow deploys to AWS.

The recorded source/image blockers are resolved; see the [security review](security-review.md) for the exact retired-secret exception and verification evidence. AWS promotion below still requires Jenkins and live staging acceptance. Use the [AWS hosting guide](aws-hosting.md) for private input templates and the first deployment.

## Jenkins setup and release gates

Configure a secured Jenkins multibranch pipeline with script path `pipelines/Jenkinsfile`. The optional Terraform Jenkins instance supplies private compute and a scoped IAM role only; controller installation, users, TLS/access, agents, credentials and cross-environment role trust remain operator setup. An existing secure controller is supported. Never run untrusted PR code on an agent with production credentials or a production Docker socket.

The `secureops-linux` agent needs Docker/Compose 2.30+, Python 3.14, Node 24.15+, Terraform 1.16.1, AWS CLI v2, Session Manager plugin, Ansible dependencies/collection from `infrastructure/ansible`, and connectivity to staging. Configure EC2/SSM/S3/KMS permissions for the intended deployment roles. The environment-local Jenkins IAM example cannot automatically access another environment.

Create Jenkins credentials with these IDs:

| ID | Type | Purpose |
|---|---|---|
| `secureops-staging-runtime` | Secret file | Private Ansible YAML matching `runtime.example.yml` |
| `secureops-prod-runtime` | Secret file | Production resource identifiers |
| `secureops-staging-smoke` | Username/password | Dedicated staging test account |
| `secureops-prod-smoke` | Username/password | Dedicated production smoke account |

Set pipeline parameters for region, ECR registry, staging/production HTTPS URLs, the SSM transfer bucket and its KMS key. Define the `secureops-release-managers` Jenkins group. Production must come from a protected `main` branch. Repository rules and Jenkins group membership are not created by a Jenkinsfile.

Each build creates disposable PostgreSQL/Redis test services, runs application tests, scans source/dependencies/history/IaC/images, and archives `reports/`. The original JWT is retired and rejected at startup; only its original historical fingerprint is excepted. The replacement backend/frontend images pass the HIGH/CRITICAL gate. New findings still fail the pipeline; do not add blanket exclusions.

After gates pass, build images are pushed with the full Git SHA, resolved to ECR digests and passed through Ansible over SSM. Immutable ECR tags reject overwrites; a repeated publication needs an explicit reuse policy or a new commit, not deletion of an existing release tag. The same local scanned images are promoted to production repositories. No `latest` deployment is supported.

Staging runs authenticated smoke checks and a time-bounded ZAP baseline/safe API scan. API discovery includes authentication and business endpoints. Safe mode does not constitute a full destructive penetration test. High-risk ZAP alerts block; medium findings require recorded review. Tokens use the default 15-minute lifetime and scans time out after ten minutes; shorter configured token lifetimes need corresponding authentication automation.

Production approval precedes serial host deployment. Per-host deployment failures restore the host's active release when possible. A failed final public smoke after all hosts deploy invokes rollback across the environment. A failure partway through a multi-host rollout can leave earlier hosts on the new healthy version; follow the deployment runbook to reconcile all hosts. First deployment has no prior version to restore. Database changes must support the previous app version.

Validate the Jenkinsfile on your Jenkins installation with its Declarative Pipeline linter, then run a complete staging build. No Jenkins run or linter validation was possible in this session.

References: [Jenkins Pipeline syntax](https://www.jenkins.io/doc/book/pipeline/syntax/), [ZAP API scan](https://www.zaproxy.org/docs/docker/api-scan/), [ZAP scan hooks](https://www.zaproxy.org/docs/docker/scan-hooks/).
