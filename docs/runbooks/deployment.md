# Deploy, verify and roll back

1. Review the security/audit blockers. Select the AWS account/profile, region and domain. Authenticate and inspect `aws sts get-caller-identity`.
2. Follow `infrastructure/README.md` to bootstrap encrypted state, review/apply an environment plan, provision secrets and configure private hosts through SSM. Provision the dedicated smoke account before the first gated deployment; do not disable authentication checks.
3. Run the complete Jenkins staging chain. Use immutable Git SHA tags and ECR digests; preserve image reports and release JSON. Approve production only after staging smoke and DAST results have been reviewed.
4. Confirm `/health/ready`, frontend, login, current-user and projects API responses. Check the target group's healthy targets, request/error rates and correlated logs. Verify both hosts agree on `.runtime/current.json` and the pipeline's SHA/digests.

On each Linux host, `scripts/deploy.py` uses an exclusive file lock. It snapshots private runtime configuration by release SHA, deploys the inactive slot, runs backward-compatible Alembic migrations and role seeding, waits for containers, performs authenticated smoke checks, changes the Nginx upstream, verifies the stable gateway and waits for ALB health. Current/previous release metadata includes SHA, image digests, timestamp, environment and pipeline ID. Monitoring follows the active metrics port.

Automatic failure handling stops the candidate and restores the current gateway when one exists. Failed restoration is reported as a failure requiring intervention. Rollback does not reverse database migrations. Never use automatic `alembic downgrade` as a substitute for compatible schema design.

Manual rollback:

```sh
cd infrastructure/ansible
ansible-playbook -i inventories/prod/aws_ec2.yml playbooks/rollback.yml
```

The installed private `.env.aws` file supplies identifiers and the wrapper fetches secrets on each host. Inspect current/previous release JSON and container health afterward. For a partial multi-host rollout, compare versions first; avoid blindly toggling already-rolled-back hosts, since rollback swaps current and previous. Select affected hosts with Ansible `--limit` and verify the environment again.

After secret rotation, retrieve runtime configuration and deploy/restart the application. Existing processes do not automatically reload a changed `.env` file. Retain only the required current/previous private runtime snapshots and remove older snapshots through a reviewed retention procedure.
