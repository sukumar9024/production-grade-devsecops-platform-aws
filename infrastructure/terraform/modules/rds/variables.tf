variable "name" {
  type = string
}
variable "subnet_ids" {
  type = list(string)
}
variable "security_group_id" {
  type = string
}
variable "production" {
  type = bool
}
variable "instance_class" {
  type = string
}
