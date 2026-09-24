# Disaster recovery

Planning objectives: **RPO 24 hours; RTO 2 hours**. These are project targets, not measured guarantees. RDS point-in-time recovery may provide a smaller actual RPO, but prove it through a timed drill. A complete regional outage is outside the currently implemented single-region design.

1. Declare the incident and choose a recovery point with the data owner. Preserve source data and release evidence.
2. Retrieve the secured Terraform backend and locks. Review/apply infrastructure in the intended recovery environment; avoid overwriting a still-running environment accidentally.
3. Configure private compute through Ansible/SSM.
4. Restore RDS into private subnets. Validate data and provision the correct runtime secret references.
5. Restore supporting S3 object versions and cache data if needed; Redis may instead be rebuilt from authoritative data.
6. Deploy the last known compatible, scanned image digests. Apply only reviewed schema migrations.
7. Verify authentication, business APIs, frontend, readiness, metrics, logs, alerts and backup schedules. Validate DNS/HTTPS before directing users to the recovered service.
8. Record timestamps, recovered data cutoff, actual RPO/RTO, missing data, failed steps and corrective work. Retire temporary recovery resources only after review.

Test loss of an application host, a failed deployment and a database restore before claiming this procedure meets the objectives. The local restore evidence does not establish the two-hour AWS recovery target.
