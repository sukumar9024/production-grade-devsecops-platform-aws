#!/usr/bin/env bash
set -euo pipefail
database="${1:?Specify the source RDS instance identifier}"
snapshot="${2:?Specify a unique snapshot identifier}"
aws rds create-db-snapshot --db-instance-identifier "$database" --db-snapshot-identifier "$snapshot" --query 'DBSnapshot.{Snapshot:DBSnapshotIdentifier,Status:Status}'
aws rds wait db-snapshot-available --db-snapshot-identifier "$snapshot"
aws rds describe-db-snapshots --db-snapshot-identifier "$snapshot" --query 'DBSnapshots[0].{Snapshot:DBSnapshotIdentifier,Time:SnapshotCreateTime,Encrypted:Encrypted,Status:Status}'
