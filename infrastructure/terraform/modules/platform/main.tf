data "aws_caller_identity" "current" {}
data "aws_availability_zones" "available" { state = "available" }
locals {
  name       = "secureops-${var.environment}"
  production = var.environment == "prod"
}
module "vpc" {
  source     = "../vpc"
  name       = local.name
  cidr       = var.vpc_cidr
  azs        = slice(data.aws_availability_zones.available.names, 0, 2)
  single_nat = !local.production
}
module "security_groups" {
  source = "../security-groups"
  name   = local.name
  vpc_id = module.vpc.id
}
module "s3" {
  source = "../s3"
  name   = "${local.name}-${data.aws_caller_identity.current.account_id}-${var.region}"
}
module "ecr" {
  source = "../ecr"
  name   = local.name
}
module "rds" {
  source            = "../rds"
  name              = local.name
  subnet_ids        = module.vpc.data_subnet_ids
  security_group_id = module.security_groups.ids["database"]
  production        = local.production
  instance_class    = local.production ? "db.t4g.small" : "db.t4g.micro"
}
module "redis" {
  source            = "../redis"
  name              = local.name
  subnet_ids        = module.vpc.data_subnet_ids
  security_group_id = module.security_groups.ids["redis"]
  production        = local.production
  auth_token        = var.redis_auth_token
}
resource "aws_secretsmanager_secret" "app" {
  name                    = "${local.name}/application"
  description             = "JWT_SECRET and integration secrets: populate a JSON version outside Terraform"
  recovery_window_in_days = 30
}
module "iam" {
  enable_opensearch  = var.enable_opensearch
  opensearch_arn     = module.monitoring.opensearch_arn
  source             = "../iam"
  name               = local.name
  repository_arns    = module.ecr.arns
  secret_arns        = [module.rds.secret_arn, module.redis.secret_arn, aws_secretsmanager_secret.app.arn]
  bucket_arn         = module.s3.arn
  bucket_kms_key_arn = module.s3.kms_key_arn
  log_group_arn      = module.monitoring.log_group_arn
  enable_jenkins     = var.enable_jenkins
  region             = var.region
  account_id         = data.aws_caller_identity.current.account_id
  environment        = var.environment
}
module "compute" {
  source             = "../compute"
  name               = local.name
  subnet_ids         = module.vpc.app_subnet_ids
  security_group_ids = module.security_groups.ids
  app_profile        = module.iam.app_profile
  jenkins_profile    = module.iam.jenkins_profile
  enable_jenkins     = var.enable_jenkins
  instance_count     = local.production ? 2 : 1
  instance_type      = local.production ? "t3.large" : "t3.medium"
}
module "alb" {
  source            = "../alb"
  name              = local.name
  vpc_id            = module.vpc.id
  subnet_ids        = module.vpc.public_subnet_ids
  security_group_id = module.security_groups.ids["alb"]
  instance_ids      = module.compute.instance_ids
  domain_name       = var.domain_name
  zone_id           = var.zone_id
  production        = local.production
}
module "monitoring" {
  enable_opensearch            = var.enable_opensearch
  subnet_ids                   = module.vpc.app_subnet_ids
  opensearch_security_group_id = module.security_groups.ids["opensearch"]
  app_role_arn                 = module.iam.app_role_arn
  production                   = local.production
  source                       = "../monitoring"
  name                         = local.name
  alb_suffix                   = module.alb.arn_suffix
  target_group_suffix          = module.alb.target_group_suffix
  instance_ids                 = module.compute.instance_ids
  database_identifier          = module.rds.identifier
  alarm_email                  = var.alarm_email
  vpc_id                       = module.vpc.id
}
