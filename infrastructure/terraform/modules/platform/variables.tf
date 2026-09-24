variable "environment" { type = string }
variable "region" { type = string }
variable "domain_name" { type = string }
variable "zone_id" { type = string }
variable "vpc_cidr" { type = string }
variable "enable_jenkins" { type = bool }
variable "alarm_email" { type = string }
variable "redis_auth_token" {
  type      = string
  sensitive = true
}

variable "enable_opensearch" { type = bool }
