resource "aws_security_group" "this" {
  for_each    = toset(["alb", "app", "database", "redis", "jenkins", "opensearch"])
  name_prefix = "${var.name}-${each.key}-"
  description = "SecureOps ${each.key}; no SSH access"
  vpc_id      = var.vpc_id
}
resource "aws_vpc_security_group_ingress_rule" "web" {
  for_each          = toset(["80", "443"])
  security_group_id = aws_security_group.this["alb"].id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = tonumber(each.key)
  to_port           = tonumber(each.key)
  description       = "Public HTTPS and redirect-only HTTP"
}
resource "aws_vpc_security_group_ingress_rule" "app" {
  security_group_id            = aws_security_group.this["app"].id
  referenced_security_group_id = aws_security_group.this["alb"].id
  ip_protocol                  = "tcp"
  from_port                    = 8080
  to_port                      = 8080
}
resource "aws_vpc_security_group_egress_rule" "alb_app" {
  security_group_id            = aws_security_group.this["alb"].id
  referenced_security_group_id = aws_security_group.this["app"].id
  ip_protocol                  = "tcp"
  from_port                    = 8080
  to_port                      = 8080
}
resource "aws_vpc_security_group_ingress_rule" "data" {
  for_each                     = { database = 5432, redis = 6379, opensearch = 443 }
  security_group_id            = aws_security_group.this[each.key].id
  referenced_security_group_id = aws_security_group.this["app"].id
  ip_protocol                  = "tcp"
  from_port                    = each.value
  to_port                      = each.value
}
resource "aws_vpc_security_group_egress_rule" "app_data" {
  for_each                     = { database = 5432, redis = 6379, opensearch = 443 }
  security_group_id            = aws_security_group.this["app"].id
  referenced_security_group_id = aws_security_group.this[each.key].id
  ip_protocol                  = "tcp"
  from_port                    = each.value
  to_port                      = each.value
}
# Private hosts need HTTPS to SSM, ECR, package repositories and AWS APIs via NAT.
# Only TCP443 is allowed; inbound application traffic is restricted to the ALB.
#trivy:ignore:AWS-0104
resource "aws_vpc_security_group_egress_rule" "https" {
  for_each          = toset(["app", "jenkins"])
  security_group_id = aws_security_group.this[each.key].id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  description       = "HTTPS package, image, SSM, and AWS API access via NAT"
}
output "ids" { value = { for k, v in aws_security_group.this : k => v.id } }
