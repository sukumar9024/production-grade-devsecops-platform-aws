variable "name" {
  type = string
}
variable "subnet_ids" {
  type = list(string)
}
variable "security_group_ids" {
  type = map(string)
}
variable "app_profile" {
  type = string
}
variable "jenkins_profile" {
  type = string
}
variable "enable_jenkins" {
  type = bool
}
variable "instance_count" {
  type = number
}
variable "instance_type" {
  type = string
}
