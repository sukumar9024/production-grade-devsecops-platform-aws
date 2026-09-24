variable "auth_token" {
  type      = string
  sensitive = true
  validation {
    condition     = can(regex("^[A-Za-z0-9]{32,128}$", var.auth_token))
    error_message = "Supply a cryptographically random 32-128 character alphanumeric Redis token through TF_VAR_redis_auth_token."

  }
}
