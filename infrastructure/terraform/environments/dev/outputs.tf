output "app_instance_ids" { value = module.platform.app_instance_ids }
output "jenkins_instance_id" { value = module.platform.jenkins_instance_id }
output "alb_dns_name" { value = module.platform.alb_dns_name }
output "target_group_arn" { value = module.platform.target_group_arn }
output "ecr_repository_urls" { value = module.platform.ecr_repository_urls }
output "database_endpoint" { value = module.platform.database_endpoint }
output "database_identifier" { value = module.platform.database_identifier }
output "database_secret_arn" { value = module.platform.database_secret_arn }
output "redis_endpoint" { value = module.platform.redis_endpoint }
output "redis_secret_arn" { value = module.platform.redis_secret_arn }
output "app_secret_arn" { value = module.platform.app_secret_arn }
output "application_bucket" { value = module.platform.application_bucket }
output "log_group_name" { value = module.platform.log_group_name }
output "alarm_topic_arn" { value = module.platform.alarm_topic_arn }
output "vpc_id" { value = module.platform.vpc_id }

output "opensearch_endpoint" { value = module.platform.opensearch_endpoint }
