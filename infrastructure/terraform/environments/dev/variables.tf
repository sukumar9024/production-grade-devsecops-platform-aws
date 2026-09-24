variable "region" {
  type    = string
  default = "ap-south-1"
}
variable "domain_name" {
  type        = string
  description = "Existing public DNS zone subdomain used for the HTTPS application."
}
variable "zone_id" {
  type        = string
  description = "Public Route53 hosted zone ID; must be delegated at the registrar."
}
variable "redis_auth_token" {
  type        = string
  sensitive   = true
  description = "Pass via TF_VAR_redis_auth_token, never commit. Present in encrypted Terraform state."
}
variable "enable_jenkins" {
  type    = bool
  default = false
}
variable "alarm_email" {
  type    = string
  default = ""
}

variable "enable_opensearch" {
  type        = bool
  default     = false
  description = "Create a managed private OpenSearch logging domain; adds ongoing AWS costs."
}
