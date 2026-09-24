variable "name" {
  type = string
}
variable "alb_suffix" {
  type = string
}
variable "target_group_suffix" {
  type = string
}
variable "instance_ids" {
  type = list(string)
}
variable "database_identifier" {
  type = string
}
variable "alarm_email" {
  type = string
}
variable "vpc_id" {
  type = string
}

variable "enable_opensearch" { type = bool }
variable "subnet_ids" { type = list(string) }
variable "opensearch_security_group_id" { type = string }
variable "app_role_arn" { type = string }
variable "production" { type = bool }
