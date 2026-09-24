# AWS hosting: account setup through first deployment

This guide uses the code consolidated in `develop`. All `********` values are placeholders: replace them only in private local copies. No AWS credentials are included. Commands below provision paid infrastructure when you run them; they have not been run against your AWS account. Start with **dev** and review each Terraform plan.

The application, infrastructure definitions and deployment tools are present. Application and source/image security checks pass in GitHub. Production acceptance is still pending: Jenkins needs a secured installation, and live AWS deployment, staging DAST, alerts, rollback and RDS restore have not been demonstrated. See [security review](security-review.md) and the [requirement audit](project-audit.md). Passing GitHub workflows are not a production release approval.

## 1. Prepare the account, workstation and private inputs

Use an AWS account with billing access, an operational contact and budget alerts. You need a delegated public Route 53 hosted zone, a hostname for each environment, and an email address that can confirm SNS subscriptions. The default region is `ap-south-1`; it must support the selected EC2, RDS, Redis and OpenSearch sizes in two availability zones. Allow for NAT, ALB, RDS, Redis, EC2 and optional OpenSearch costs.

Install Git, AWS CLI v2, the AWS Session Manager plugin, Terraform 1.16.1, Python 3.14, Node 24.15.0 and Docker with Compose 2.30+. Ansible dependencies and its collection are pinned in `infrastructure/ansible/requirements*`. AWS hosts use Amazon Linux 2023 and x86_64 images. Keep Docker running as requested; the current local read-only storage problem must be resolved before local image builds/scans can run. A healthy Linux build agent can perform those checks instead.

Prefer temporary IAM Identity Center credentials ([AWS CLI SSO setup](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html)):

```sh
aws configure sso --profile secureops
aws sso login --profile secureops
export AWS_PROFILE=secureops
export AWS_REGION=ap-south-1
aws sts get-caller-identity
```

Confirm the returned account and role. The provisioning role needs permissions for the resources in the Terraform modules, including IAM role creation/pass-role and service-linked roles. The deployment controller needs EC2 discovery, SSM sessions, scoped transfer-bucket S3/KMS access, ECR publishing and the resources its deployment checks inspect. Instance profiles are created by Terraform. The repository does not supply an account-wide provisioning policy or cross-account Jenkins trust; have the account administrator scope those identities to the intended account/environment. Do not use root credentials. If temporary access-key credentials are required, `infrastructure/aws/credentials.example` shows the format for `~/.aws/credentials`; never put the filled file in Git.

Run the workstation commands from the repository root in the same shell:

```sh
export PROJECT_ROOT="$PWD"
export PLATFORM_ENVIRONMENT=dev
umask 077
mkdir -p "$PROJECT_ROOT/.runtime/aws/$PLATFORM_ENVIRONMENT"
export PRIVATE_AWS_DIR="$PROJECT_ROOT/.runtime/aws/$PLATFORM_ENVIRONMENT"
cp infrastructure/aws/hosting.env.example "$PRIVATE_AWS_DIR/hosting.env"
cp infrastructure/aws/backend.hcl.example "$PRIVATE_AWS_DIR/backend.hcl"
cp infrastructure/aws/terraform.tfvars.example "$PRIVATE_AWS_DIR/terraform.tfvars"
cp infrastructure/aws/application-secret.example.json "$PRIVATE_AWS_DIR/application-secret.json"
cp infrastructure/aws/redis-secret.example.json "$PRIVATE_AWS_DIR/redis-secret.json"
```

Edit these private files before continuing. `.runtime/` is Git-ignored. `hosting.env` is shell syntax: quote values; source only a file you control. Set a globally unique state-bucket name (at most 55 characters, because the transfer bucket adds `-ansible`). Populate the account ID, domain, zone ID and operations email. Leave bootstrap output fields pending until step 2. Use the **same** domain/zone/email/region in `terraform.tfvars`. For another environment, change the backend state key to `secureops/staging/terraform.tfstate` or `secureops/prod/terraform.tfstate` and use that environment's Terraform directory/inventory. Never share state keys across environments.

Create distinct randomly generated secrets in your password manager. The JWT secret needs at least 32 characters; a 64-character random hexadecimal value works for both JWT and Redis AUTH (use different values). Redis AUTH must match `TF_VAR_redis_auth_token` in `hosting.env` and `password` in `redis-secret.json`. Use a real smoke-account email as `smoke_identity`, a password of at least 12 characters, a Grafana admin password of at least 16 characters, and a real Slack incoming webhook HTTPS URL/channel for alerting. Do not reuse credentials across environments. The smoke account will be created in step 7; it needs only Viewer access.

```sh
set -a
. "$PRIVATE_AWS_DIR/hosting.env"
set +a
aws sts get-caller-identity
```

Do not enable shell tracing or print these private files. Secret-bearing plan/state files and environment variables need access protection even though Terraform marks inputs sensitive.

## 2. Create encrypted Terraform state storage

Bootstrap runs once per administrative state setup. Use an existing approved bootstrap if one already exists; do not create another with the same names.

```sh
terraform -chdir=infrastructure/terraform/bootstrap init
terraform -chdir=infrastructure/terraform/bootstrap plan \
  -var="region=$AWS_REGION" -var="state_bucket_name=$STATE_BUCKET_NAME" \
  -out="$PRIVATE_AWS_DIR/bootstrap.plan"
# Review the resources and costs above before applying.
terraform -chdir=infrastructure/terraform/bootstrap apply "$PRIVATE_AWS_DIR/bootstrap.plan"
terraform -chdir=infrastructure/terraform/bootstrap output -json > "$PRIVATE_AWS_DIR/bootstrap-outputs.json"
```

Set `backend.hcl`'s `bucket` from output `state_bucket` and `kms_key_id` from `kms_key_arn`. Set `STATE_KMS_KEY_ARN`, `ANSIBLE_SSM_KMS_KEY` and `ANSIBLE_SSM_BUCKET` in private `hosting.env` from the same outputs (`ansible_transfer_bucket` for the latter). Reload that file. The state bucket is versioned and protected against destruction; the separate nonversioned SSM transfer bucket expires objects after one day. Securely back up bootstrap's local Terraform state or migrate it to an approved administrative backend; do not commit it.

## 3. Provision the selected environment

```sh
export TF_ENV_DIR="$PROJECT_ROOT/infrastructure/terraform/environments/$PLATFORM_ENVIRONMENT"
terraform -chdir="$TF_ENV_DIR" init -backend-config="$PRIVATE_AWS_DIR/backend.hcl"
terraform -chdir="$TF_ENV_DIR" plan -var-file="$PRIVATE_AWS_DIR/terraform.tfvars" \
  -out="$PRIVATE_AWS_DIR/environment.plan"
# Review the complete plan, including network ingress, deletions and costs.
terraform -chdir="$TF_ENV_DIR" apply "$PRIVATE_AWS_DIR/environment.plan"
terraform -chdir="$TF_ENV_DIR" output -json > "$PRIVATE_AWS_DIR/outputs.json"
```

This creates private EC2, isolated PostgreSQL/Redis, ECR, application storage, instance IAM profiles, Secrets Manager containers, ALB, DNS-validated ACM TLS, a Route 53 record and monitoring resources. It does not install the application. `enable_opensearch=true` also creates a private managed OpenSearch domain for centralized logs. ACM validation requires a working delegated public zone. `enable_jenkins=true` only creates an optional Jenkins instance/profile; it does not install or secure Jenkins.

Redis's sensitive AUTH input is stored in Terraform state: restrict access to the encrypted state and plan files. RDS owns and rotates its managed master-secret value; do not replace it. The current application uses that master credential; separate restricted runtime and migration database credentials remain required production hardening work.

## 4. Populate application and Redis secret values

Use Terraform outputs for the secret ARNs. Replace every placeholder in the two JSON files first; keep values on disk privately, not in command arguments or Git.

```sh
export APP_SECRET_ARN="$(terraform -chdir="$TF_ENV_DIR" output -raw app_secret_arn)"
export REDIS_SECRET_ARN="$(terraform -chdir="$TF_ENV_DIR" output -raw redis_secret_arn)"
aws secretsmanager put-secret-value --secret-id "$APP_SECRET_ARN" \
  --secret-string "file://$PRIVATE_AWS_DIR/application-secret.json" --query VersionId --output text
aws secretsmanager put-secret-value --secret-id "$REDIS_SECRET_ARN" \
  --secret-string "file://$PRIVATE_AWS_DIR/redis-secret.json" --query VersionId --output text
python3 scripts/aws-runtime-config.py --outputs "$PRIVATE_AWS_DIR/outputs.json" \
  --region "$AWS_REGION" --domain "$APPLICATION_DOMAIN" --output "$PRIVATE_AWS_DIR/runtime.json"
```

The helper maps Terraform identifiers to Ansible variables, includes the actual ECR repository names and refuses to overwrite an existing runtime file. `runtime.json` contains identifiers, not passwords. Remove temporary secret JSON files after verifying the versions were created and securing the values in your password manager. Never replace the RDS-managed secret with the application JSON.

## 5. Configure the private hosts over SSM

Check that the instances are online in Systems Manager. Inventory and group-variable files currently select `ap-south-1`; update them consistently if choosing another region. No public instance IP or SSH port is needed. On the workstation/controller:

```sh
cd "$PROJECT_ROOT/infrastructure/ansible"
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/ansible-galaxy collection install -r requirements.yml
.venv/bin/ansible-inventory -i "inventories/$PLATFORM_ENVIRONMENT/aws_ec2.yml" --graph
.venv/bin/ansible-playbook -i "inventories/$PLATFORM_ENVIRONMENT/aws_ec2.yml" \
  playbooks/site.yml -e "@$PRIVATE_AWS_DIR/runtime.json"
cd "$PROJECT_ROOT"
```

The roles install Docker/Compose, AWS CLI, host Python dependencies, hardening, runtime scripts and the RDS CA bundle. Resource identifiers go to `/opt/secureops/.env.aws`; application secrets are fetched on the instance into a root-only `.env.runtime`. Re-run `site.yml` from the approved commit when deployment scripts/configuration change. Check whether OS updates require a controlled reboot.

## 6. Build, scan and publish immutable images

Use a healthy build host. Run application tests and all source gates in [CI setup](ci-cd.md) before publishing. The previous source/image findings are resolved in [security review](security-review.md); rerun every gate for the actual release and do not suppress or skip failures. Build the x86_64 platform used by EC2 (especially on an Apple Silicon workstation):

```sh
cd "$PROJECT_ROOT"
export RELEASE_SHA="$(git rev-parse HEAD)"
docker build --platform linux/amd64 -t "secureops-backend:$RELEASE_SHA" backend
docker build --platform linux/amd64 -t "secureops-frontend:$RELEASE_SHA" frontend
IMAGE_TAG="$RELEASE_SHA" bash scripts/security-scan.sh images
# Continue only after all required gates pass.
export ECR_REGISTRY="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["ecr_registry"])' "$PRIVATE_AWS_DIR/runtime.json")"
python3 scripts/publish-images.py --registry "$ECR_REGISTRY" \
  --environment "$PLATFORM_ENVIRONMENT" --sha "$RELEASE_SHA"
```

The publisher pushes the scanned local images, resolves their ECR SHA256 digests and writes `reports/release-dev.json` (or the selected environment). The gateway reuses the patched frontend runtime by digest; `deploy.py` persists `GATEWAY_IMAGE` in `.runtime/gateway.env` on the host. Reapply `site.yml` for the updated gateway systemd unit. A gateway image change may recreate that container. ECR tags are immutable; use a new commit for changed images. A production promotion should reuse the verified release images, not rebuild untested content.

## 7. First deployment only: migrate and create accounts

Authenticated deployment checks need an account before the first release. Obtain one application instance ID from `app_instance_ids` in the Terraform output. Open a terminal session with `aws ssm start-session --target '********'` (replace the instance-ID placeholder). On that instance:

```sh
sudo -i
cd /opt/secureops
set -a
. ./.env.aws
set +a
python3.11 scripts/fetch-secrets.py
aws ecr get-login-password --region "$AWS_REGION" | \
  docker login --username AWS --password-stdin "$ECR_REGISTRY"
# Copy the exact digest values from reports/release-ENVIRONMENT.json.
export BACKEND_IMAGE='********'
export FRONTEND_IMAGE='********'
export APP_PORT=18080 METRICS_PORT=18000 RUNTIME_ENV_FILE=/opt/secureops/.env.runtime
docker compose -p secureops-bootstrap -f compose.prod.yaml pull
docker compose -p secureops-bootstrap -f compose.prod.yaml run --rm --no-deps backend alembic upgrade head
docker compose -p secureops-bootstrap -f compose.prod.yaml run --rm --no-deps backend python -m scripts.seed_roles
docker compose -p secureops-bootstrap -f compose.prod.yaml run --rm --no-deps backend python -m scripts.create_viewer
docker compose -p secureops-bootstrap -f compose.prod.yaml run --rm --no-deps backend python -m scripts.create_admin
```

The account scripts prompt interactively without showing passwords. Give the Viewer the email/password stored as `smoke_identity`/`smoke_password` in the application secret. Use separate administrator credentials. These one-off containers do not publish service ports. Run this once per environment database, not once per application host. Existing installations should use their established accounts; duplicate account creation fails instead of resetting credentials.

## 8. Deploy, verify and configure observability

Return to the workstation/controller:

```sh
cd "$PROJECT_ROOT/infrastructure/ansible"
.venv/bin/ansible-playbook -i "inventories/$PLATFORM_ENVIRONMENT/aws_ec2.yml" \
  playbooks/deploy.yml -e "@$PRIVATE_AWS_DIR/runtime.json" \
  -e "@$PROJECT_ROOT/reports/release-$PLATFORM_ENVIRONMENT.json"
curl -I "http://$APPLICATION_DOMAIN"
curl --fail "https://$APPLICATION_DOMAIN/health/ready"
.venv/bin/ansible-playbook -i "inventories/$PLATFORM_ENVIRONMENT/aws_ec2.yml" \
  playbooks/observability.yml -e "@$PRIVATE_AWS_DIR/runtime.json"
cd "$PROJECT_ROOT"
```

Deployment verifies immutable metadata, fetches secrets, migrates, checks a candidate slot with authenticated smoke tests, switches the gateway and verifies ALB targets. A failed switch restores the previous release. Confirm the HTTP redirect, valid HTTPS certificate, healthy targets, browser login/RBAC and API mutation/audit behavior. Do not treat `curl` alone as acceptance. Run staging authenticated ZAP DAST through the Jenkins pipeline and retain its report.

Observability requires the OpenSearch endpoint, Grafana password and alert webhook configured earlier. Keep Grafana/Prometheus private; forward a port using SSM when needed:

```sh
aws ssm start-session --target '********' \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["3000"],"localPortNumber":["3000"]}'
```

Open `http://127.0.0.1:3000` while the session runs and sign in with the Grafana admin secret. Use port 9090 for Prometheus in a separate session. Verify scrape targets, all dashboards and log ingestion. Apply `logging/retention-policy.json` to OpenSearch using an IAM-signed request and verify policy attachment; saving the file in Git does not install it. Confirm SNS email subscriptions and deliver a real test alert through both configured notification paths. OpenSearch dashboard SSO/fine-grained users and centralized multi-host metric aggregation are follow-up work.

## 9. Jenkins, promotion and operation

GitHub's `.github/workflows/ci.yml` runs backend/frontend/platform checks on `develop` and `main`; it has no AWS deployment credentials and does not deploy. For continuous delivery, configure a secured Jenkins controller and Linux Docker agents, repository access, tools and per-environment IAM roles using [CI setup](ci-cd.md), then point the job at `pipelines/Jenkinsfile`. The optional Terraform Jenkins instance alone is insufficient. Production approval is restricted to the configured release-manager identity/group; verify that authorization before enabling promotion.

Repeat environment provisioning with independent staging/prod state keys, domains, secrets, inventory and runtime/release files. `develop` is the complete integration branch; Jenkins production promotion requires a reviewed `main` commit. Set required checks and branch protections in GitHub. Do not change the pipeline to deploy every development push into production.

Before calling the platform production-ready, retain evidence for these checks:

- Application tests and every source/image security gate pass for the deployed commit.
- Staging authenticated smoke/DAST, real alert delivery, log search/retention and TLS/DNS checks pass.
- A failed deployment and an explicit rollback preserve service and compatible database state.
- RDS snapshot/restore into an isolated environment passes integrity checks; record actual RPO/RTO.
- Production runtime DB access is least privilege; Jenkins, rotation, IAM and recovery procedures are reviewed.

Use the [deployment](runbooks/deployment.md), [backup/restore](runbooks/backup-restore.md), [incident](runbooks/incidents.md) and [disaster recovery](runbooks/disaster-recovery.md) runbooks. Keep snapshots and data retention requirements in mind before any teardown; production deletion protection and final snapshots are intentional. No live AWS deployment or production acceptance evidence is claimed by this guide.
