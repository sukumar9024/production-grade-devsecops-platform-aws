resource "aws_opensearch_domain" "logs" {
  count          = var.enable_opensearch ? 1 : 0
  domain_name    = "${var.name}-logs"
  engine_version = "OpenSearch_2.19"
  cluster_config {
    instance_type          = "t3.small.search"
    instance_count         = var.production ? 2 : 1
    zone_awareness_enabled = var.production
    dynamic "zone_awareness_config" {
      for_each = var.production ? [1] : []
      content { availability_zone_count = 2 }
    }
  }
  ebs_options {
    ebs_enabled = true
    volume_type = "gp3"
    volume_size = 20
  }
  vpc_options {
    subnet_ids         = var.production ? var.subnet_ids : [var.subnet_ids[0]]
    security_group_ids = [var.opensearch_security_group_id]
  }
  encrypt_at_rest { enabled = true }
  node_to_node_encryption { enabled = true }
  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-PFS-2023-10"
  }
  auto_tune_options { desired_state = "DISABLED" }
  access_policies = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Principal = { AWS = var.app_role_arn }, Action = ["es:ESHttpPost", "es:ESHttpPut", "es:ESHttpGet", "es:ESHttpHead", "es:ESHttpDelete"], Resource = "arn:aws:es:${data.aws_region.current.region}:${data.aws_caller_identity.current.account_id}:domain/${var.name}-logs/*" }] })
}
data "aws_region" "current" {}
data "aws_caller_identity" "current" {}
output "opensearch_endpoint" { value = try(aws_opensearch_domain.logs[0].endpoint, "") }
output "opensearch_arn" { value = try(aws_opensearch_domain.logs[0].arn, "") }
