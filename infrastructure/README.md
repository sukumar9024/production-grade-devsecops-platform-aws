# AWS infrastructure and host automation

This code has been validated locally. No AWS resources have been created, and no live plan, deployment, restore, alarm delivery or failover test has been performed. Terraform validation checks configuration and provider schemas; it does not establish account permissions, quota availability, regional capacity or a working service.

## Layout and design

`terraform/modules` contains VPC, security groups, EC2, ALB, RDS, Redis, ECR, S3, IAM and monitoring modules, composed by `platform`. `terraform/environments/{dev,staging,prod}` have independent state keys. Terraform is pinned by `.terraform-version` to 1.16.1; the configuration supports >=1.10,<2. AWS provider 6.45.0 is pinned with checked-in dependency lockfiles.

| Setting | dev | staging | prod |
|---|---|---|---|
| VPC CIDR | 10.20.0.0/16 | 10.30.0.0/16 | 10.40.0.0/16 |
| Availability zones | 2 | 2 | 2 |
| NAT gateways | 1 | 1 | 2 |
| Private application instances | 1 | 1 | 2 |
| RDS Multi-AZ | off | off | on |
| Redis replicas / failover | off | off | on |
| RDS backup retention | 7 days | 7 days | 14 days |

Public ALB subnets use an Internet Gateway. Private application subnets use NAT; isolated database subnets have no default Internet route. Database and Redis ingress is restricted to the application security group. Instances have no public IP or SSH ingress, enforce IMDSv2 and use encrypted EBS. Container access to instance credentials requires IMDS hop limit 2; the host role must remain narrowly scoped.

ALB redirects HTTP to HTTPS, uses a DNS-validated ACM certificate and targets host port 8080 at `/health/ready`. The deployment gateway proxies the active local slot. PostgreSQL requires TLS; the runtime verifies its hostname using the official RDS CA bundle. Redis requires AUTH and TLS. Tagged ECR releases are immutable and never expired automatically; only untagged images older than 14 days are removed.

Managed OpenSearch is optional (`enable_opensearch=true`), private, encrypted, and HTTPS-only. The EC2 app role signs log-ingestion requests. This creates a paid domain; the supplied small topology is for the project, not a sizing guarantee. Its service-linked role must already exist or the applying identity must be allowed to create it. IAM-scoped access is used; fine-grained OpenSearch users and dashboard SSO are not configured. Without this flag the centralized logging acceptance criterion remains pending.

`enable_jenkins=true` creates a dedicated private instance and ECR/SSM role scoped to this environment. It does **not** install Jenkins or configure its users, agents, credentials or cross-environment promotion trust. Use an existing secured Jenkins controller or complete that setup separately. Jenkins should assume distinct staging/production deployment roles; the supplied role cannot deploy to other environments.

## Bootstrap state, then plan an environment

Use an explicitly selected AWS profile/account and confirm it with `aws sts get-caller-identity`. Provide a delegated public Route53 zone and subdomain. Do not execute the commands below against an unreviewed account.

```sh
cd infrastructure/terraform/bootstrap
terraform init
terraform plan -var='state_bucket_name=YOUR-GLOBALLY-UNIQUE-STATE-BUCKET' -out=bootstrap.plan
# Review the plan, then apply it in your selected AWS account.
terraform apply bootstrap.plan
terraform output
```

Bootstrap creates a private, versioned, KMS-encrypted state bucket and a separate encrypted, nonversioned Ansible transfer bucket with one-day expiration. Keep bootstrap's local state securely backed up until you migrate it to an administrative remote state location. The state bucket/KMS key have `prevent_destroy`; deleting them is not a routine teardown step.

Copy `backend.hcl.example` to an untracked `backend.hcl`, populate bootstrap outputs, and copy `terraform.tfvars.example` to an untracked `terraform.tfvars`. Use a separate backend key per environment. Backend encryption and native S3 lockfiles are enabled; deployment identities need Get/Put state, Get/Put/Delete `.tflock`, scoped ListBucket and KMS encrypt/decrypt access. Do not put AWS credentials in backend files.

```sh
cd ../environments/dev
terraform init -backend-config=backend.hcl
# Set TF_VAR_redis_auth_token through a secret manager/secure terminal, never a committed tfvars file.
terraform plan -out=reviewed.plan
terraform apply reviewed.plan
terraform output -json > /tmp/secureops-dev-outputs.json
```

Plan files, state files and crash logs can contain secrets: keep them out of Git and limit access. The Redis AUTH token is a sensitive Terraform input but **is persisted in Terraform state** by the provider. Encrypted state does not remove the need for strict access control. RDS manages its own master password in Secrets Manager, so Terraform does not receive that password. App and Redis secret containers have no versions until you provision them outside Terraform.

Populate the application secret with JSON keys `jwt_secret`, `smoke_identity`, `smoke_password`. For observability also add `grafana_admin_password`, `alert_webhook_url` (a Slack incoming webhook HTTPS URL) and optional `alert_channel`. Populate Redis JSON `{"password":"..."}` with the exact token used for Terraform. Use `aws secretsmanager put-secret-value --secret-string file://...` with a private temporary file or your organization's secret provisioning workflow; never pass secrets in a command line. Destroy private temporary files promptly. Do not replace the RDS-managed secret.

The default runtime uses the RDS master login for migrations and the application. Before broad production use, provision a restricted application DB user and a separate migration credential, and adapt the runtime/role secret references accordingly. JWT, Redis and app-secret rotation require coordinated runtime refresh/redeployment; automated rotation is not implemented for those values.

## Configure private hosts with Ansible over SSM

On the controller install Python dependencies, the pinned collection, AWS CLI and AWS Session Manager plugin. The controller identity needs EC2 DescribeInstances, SSM StartSession/TerminateSession and scoped S3 transfer-object permissions and KMS GenerateDataKey/Decrypt on the bootstrap key. The host requires outbound HTTPS to SSM, package repositories, registry and trust-bundle endpoints. The transfer bucket is for automation artifacts, never state or persistent secrets.

```sh
cd infrastructure/ansible
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/ansible-galaxy collection install -r requirements.yml
export ANSIBLE_SSM_BUCKET=YOUR-BOOTSTRAP-TRANSFER-BUCKET
export ANSIBLE_SSM_KMS_KEY=YOUR-BOOTSTRAP-KMS-KEY-ARN
cp runtime.example.yml runtime.yml
# Populate runtime.yml from Terraform outputs; this file contains identifiers, not passwords.
.venv/bin/ansible-playbook -i inventories/dev/aws_ec2.yml playbooks/site.yml -e @runtime.yml
```

Set the same region in Terraform, inventory and group vars. Inventory filters `Project=secureops`, the exact environment and `Role=app`; AWS instance IDs are SSM destinations. Roles require Amazon Linux 2023, install Docker plus checksum-verified Compose, Python 3.11, security updates, disable SSH, bound container/journal logs and configure `/opt/secureops`. Security groups are the network firewall; Docker's firewall chains are not overwritten. Security updates can require a controlled reboot; reboot need and workload recovery must be checked by the operator.

Ansible downloads the official RDS CA bundle into `docker/certs/rds-global-bundle.pem`. `.env.aws` contains resource identifiers; secrets are retrieved on EC2 into root-only `.env.runtime`. The gateway upstream is initialized without overwriting an active slot. Docker restart policies recover containers on reboot after an initial release.

Before first deployment, bootstrap a real smoke-test account in the database using the application's admin/bootstrap procedure and store the matching credentials in the app secret. This is required: authentication checks must not be bypassed to make the first release appear successful. Supply images already pushed to this environment's ECR repositories, pinned to SHA256 digests.

```sh
.venv/bin/ansible-playbook -i inventories/dev/aws_ec2.yml playbooks/deploy.yml \
  -e git_commit=FULL_40_CHARACTER_GIT_SHA -e pipeline_id=PIPELINE_ID \
  -e backend_image=ACCOUNT.dkr.ecr.REGION.amazonaws.com/secureops-dev-backend@sha256:DIGEST \
  -e frontend_image=ACCOUNT.dkr.ecr.REGION.amazonaws.com/secureops-dev-frontend@sha256:DIGEST
.venv/bin/ansible-playbook -i inventories/dev/aws_ec2.yml playbooks/rollback.yml
.venv/bin/ansible-playbook -i inventories/dev/aws_ec2.yml playbooks/observability.yml
```

Deployment is serial, stops on a failed host, logs into ECR via stdin, retrieves secrets on the host, runs migrations and authenticated smoke checks, and verifies ALB targets. Production's inventory name is `prod`; its application environment is `production`. `.env.aws` contains the target group ARN and the host's instance ID. The observability playbook requires a configured OpenSearch endpoint and the notification/Grafana secret values. Apply `logging/retention-policy.json` to OpenSearch via an IAM-signed request and verify index-policy attachment. Merely storing that JSON does not activate retention. Confirm SNS email subscriptions and send real test alerts before claiming delivery.

## Validation and operational limits

Local checks: `terraform fmt -check -recursive infrastructure/terraform`; each environment and bootstrap accepts `terraform init -backend=false` and `terraform validate`. All four Ansible playbooks support `--syntax-check` with an offline inventory. These checks do not connect to EC2 or test SSM, certificates, DNS, AWS APIs, quotas, image pulls, application availability or recovery.

Restore an RDS backup into an isolated temporary environment and record actual backup time, restore duration, integrity checks and cleanup. No backup restore or disaster recovery objective is proven by this code. RDS final snapshots and production deletion protection are enabled; the fixed final-snapshot name must be changed if a snapshot with that name already exists during teardown. EC2 replacement needs a controlled roll and configuration; there is no Auto Scaling Group. Dev/staging intentionally use a single NAT and lack database/cache failover. ALB access-log archival, a WAF, fine-grained DB application credentials, hardened Jenkins setup and cross-account CI trust remain operational follow-ups.

References: [Terraform AWS provider 6.45.0](https://registry.terraform.io/providers/hashicorp/aws/6.45.0/docs), [S3 state backend and locking](https://developer.hashicorp.com/terraform/language/backend/s3), [SSM Ansible connection](https://docs.ansible.com/projects/ansible/latest/collections/amazon/aws/aws_ssm_connection.html), [Redis AUTH behavior](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/elasticache_replication_group.html).
