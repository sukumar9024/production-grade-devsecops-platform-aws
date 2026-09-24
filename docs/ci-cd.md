# Jenkins setup and release gates

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

Each build creates disposable PostgreSQL/Redis test services, runs application tests, scans source/dependencies/history/IaC/images, and archives `reports/`. The history scan currently intentionally blocks on the former JWT example. Image scanning also blocks on the current base-image findings. Do not add blanket exclusions to get a green pipeline.

After gates pass, build images are pushed with the full Git SHA, resolved to ECR digests and passed through Ansible over SSM. Immutable ECR tags reject overwrites; a repeated publication needs an explicit reuse policy or a new commit, not deletion of an existing release tag. The same local scanned images are promoted to production repositories. No `latest` deployment is supported.

Staging runs authenticated smoke checks and a time-bounded ZAP baseline/safe API scan. API discovery includes authentication and business endpoints. Safe mode does not constitute a full destructive penetration test. High-risk ZAP alerts block; medium findings require recorded review. Tokens use the default 15-minute lifetime and scans time out after ten minutes; shorter configured token lifetimes need corresponding authentication automation.

Production approval precedes serial host deployment. Per-host deployment failures restore the host's active release when possible. A failed final public smoke after all hosts deploy invokes rollback across the environment. A failure partway through a multi-host rollout can leave earlier hosts on the new healthy version; follow the deployment runbook to reconcile all hosts. First deployment has no prior version to restore. Database changes must support the previous app version.

Validate the Jenkinsfile on your Jenkins installation with its Declarative Pipeline linter, then run a complete staging build. No Jenkins run or linter validation was possible in this session.

References: [Jenkins Pipeline syntax](https://www.jenkins.io/doc/book/pipeline/syntax/), [ZAP API scan](https://www.zaproxy.org/docs/docker/api-scan/), [ZAP scan hooks](https://www.zaproxy.org/docs/docker/scan-hooks/).
