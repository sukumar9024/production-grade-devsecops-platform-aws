output "app_instance_ids" { value = module.compute.instance_ids }
output "jenkins_instance_id" { value = module.compute.jenkins_id }
output "alb_dns_name" { value = module.alb.dns_name }
output "target_group_arn" { value = module.alb.target_group_arn }
output "ecr_repository_urls" { value = module.ecr.urls }
output "database_endpoint" { value = module.rds.endpoint }
output "database_identifier" { value = module.rds.identifier }
output "database_secret_arn" { value = module.rds.secret_arn }
output "redis_endpoint" { value = module.redis.endpoint }
output "redis_secret_arn" { value = module.redis.secret_arn }
output "app_secret_arn" { value = aws_secretsmanager_secret.app.arn }
output "application_bucket" { value = module.s3.id }
output "log_group_name" { value = module.monitoring.log_group_name }
output "alarm_topic_arn" { value = module.monitoring.sns_topic_arn }
output "vpc_id" { value = module.vpc.id }

output "opensearch_endpoint" { value = module.monitoring.opensearch_endpoint }
