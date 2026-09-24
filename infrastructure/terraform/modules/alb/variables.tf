variable "name" {
  type = string
}
variable "vpc_id" {
  type = string
}
variable "subnet_ids" {
  type = list(string)
}
variable "security_group_id" {
  type = string
}
variable "instance_ids" {
  type = list(string)
}
variable "domain_name" {
  type = string
}
variable "zone_id" {
  type = string
}
variable "production" {
  type = bool
}
