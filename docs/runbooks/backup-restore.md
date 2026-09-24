# Backup and restore

RDS automated backups are configured for 7 days in dev/staging and 14 in production; backup and maintenance windows are distinct. Production deletion protection and final snapshots are enabled. S3 has versioning, encryption and 90-day retention of superseded versions. Redis snapshots are supporting-cache recovery, not a substitute for PostgreSQL backups.

Manual RDS snapshot:

```sh
bash scripts/rds-snapshot.sh secureops-prod secureops-prod-before-release-YYYYMMDD
```

Restore a selected snapshot into a new private temporary instance (billable; use the reviewed account and VPC):

```sh
bash scripts/rds-restore.sh SNAPSHOT_ID secureops-restore-YYYYMMDD PRIVATE_SUBNET_GROUP PRIVATE_DB_SECURITY_GROUP
```

The script records resource restore start/availability and endpoint metadata. **Availability is not data validation.** From a private operator host, retrieve the restored instance's new managed credential, connect using TLS hostname verification, check Alembic version/table presence, compare expected table counts/checksums with the backup's evidence, and point an isolated application instance at the restored database. Test login and representative projects/services/deployments/incidents. Record backup timestamp, start, resource-ready time, application-ready time, validation result, RPO/RTO and reviewer. Only then mark the RDS restore requirement complete. Remove only the temporary instance after preserving the evidence and checking its identifier; no cleanup script automatically deletes production resources.

Local drill:

```sh
python3 scripts/local-restore-drill.py
```

This briefly pauses only this Compose project's backend, dumps its database, restores a uniquely named temporary database, compares the SHA256 of every table's ordered JSON rows, resumes the backend and drops the temporary database. Backups stay in ignored `.runtime/backups` with private permissions. Evidence is written to `reports/local-restore.json`. The recorded local drill verified all nine tables; it proves local PostgreSQL dump/restore only.

If restore fails, retain the failure report and backup, verify the backend resumed, investigate version/extension/permission differences and rerun against a new temporary target. Never overwrite the original database to test a backup.
