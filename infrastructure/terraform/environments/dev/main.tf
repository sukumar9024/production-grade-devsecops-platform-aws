provider "aws" {
  region = var.region
  default_tags { tags = { Project = "secureops", Environment = "dev", ManagedBy = "terraform" } }
}
module "platform" {
  enable_opensearch = var.enable_opensearch
  source            = "../../modules/platform"
  environment       = "dev"
  region            = var.region
  domain_name       = var.domain_name
  zone_id           = var.zone_id
  vpc_cidr          = "10.20.0.0/16"
  redis_auth_token  = var.redis_auth_token
  enable_jenkins    = var.enable_jenkins
  alarm_email       = var.alarm_email
}
