resource "aws_elasticache_subnet_group" "this" {
  name       = var.name
  subnet_ids = var.subnet_ids
}
resource "aws_elasticache_replication_group" "this" {
  replication_group_id       = var.name
  description                = "Private TLS Redis for SecureOps"
  engine                     = "redis"
  engine_version             = "7.1"
  node_type                  = var.production ? "cache.t4g.small" : "cache.t4g.micro"
  num_cache_clusters         = var.production ? 2 : 1
  automatic_failover_enabled = var.production
  multi_az_enabled           = var.production
  port                       = 6379
  subnet_group_name          = aws_elasticache_subnet_group.this.name
  security_group_ids         = [var.security_group_id]
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  transit_encryption_mode    = "required"
  auth_token                 = var.auth_token
  auth_token_update_strategy = "SET"
  snapshot_retention_limit   = var.production ? 7 : 1
  snapshot_window            = "02:00-03:00"
  maintenance_window         = "sun:05:30-sun:06:30"
  auto_minor_version_upgrade = true
}
resource "aws_secretsmanager_secret" "this" {
  name                    = "${var.name}/redis"
  description             = "Provision JSON password using the same auth token outside Terraform; never put values in tfvars"
  recovery_window_in_days = 30
}
output "endpoint" { value = aws_elasticache_replication_group.this.primary_endpoint_address }
output "secret_arn" { value = aws_secretsmanager_secret.this.arn }
