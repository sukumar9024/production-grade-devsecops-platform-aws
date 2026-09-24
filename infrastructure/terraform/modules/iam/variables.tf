variable "name" {
  type = string
}
variable "repository_arns" {
  type = list(string)
}
variable "secret_arns" {
  type = list(string)
}
variable "bucket_arn" {
  type = string
}
variable "bucket_kms_key_arn" { type = string }
variable "log_group_arn" {
  type = string
}
variable "enable_jenkins" {
  type = bool
}
variable "region" {
  type = string
}
variable "account_id" {
  type = string
}
variable "environment" {
  type = string
}

variable "enable_opensearch" { type = bool }
variable "opensearch_arn" { type = string }
