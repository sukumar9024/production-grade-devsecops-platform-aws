#!/usr/bin/env bash
# Run from a reviewed operator session; this creates a billable temporary RDS instance.
set -euo pipefail
snapshot="${1:?Specify snapshot ID}"
target="${2:?Specify temporary target secureops-restore-*}"
subnet_group="${3:?Specify private DB subnet group}"
security_group="${4:?Specify private database security group ID}"
case "$target" in secureops-restore-*) ;; *) echo 'Target must start secureops-restore-' >&2; exit 2 ;; esac
mkdir -p reports
date -u +%FT%TZ > "reports/$target-start.txt"
aws rds restore-db-instance-from-db-snapshot --db-instance-identifier "$target" --db-snapshot-identifier "$snapshot" --db-subnet-group-name "$subnet_group" --vpc-security-group-ids "$security_group" --no-publicly-accessible --manage-master-user-password --tags Key=Purpose,Value=restore-drill --query 'DBInstance.DBInstanceIdentifier'
aws rds wait db-instance-available --db-instance-identifier "$target"
date -u +%FT%TZ > "reports/$target-available.txt"
aws rds describe-db-instances --db-instance-identifier "$target" --query 'DBInstances[0].{Endpoint:Endpoint.Address,Secret:MasterUserSecret.SecretArn,Public:PubliclyAccessible,Encrypted:StorageEncrypted}' > "reports/$target-resource.json"
echo 'Resource restored. Data validation and application smoke tests remain REQUIRED; see docs/runbooks/backup-restore.md.'
