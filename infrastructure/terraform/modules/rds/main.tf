resource "aws_db_subnet_group" "this" {
  name       = var.name
  subnet_ids = var.subnet_ids
}
resource "aws_db_parameter_group" "this" {
  name_prefix = "${var.name}-"
  family      = "postgres16"
  parameter {
    name  = "rds.force_ssl"
    value = "1"
  }
}
resource "aws_db_instance" "this" {
  identifier                            = var.name
  engine                                = "postgres"
  engine_version                        = "16"
  instance_class                        = var.instance_class
  allocated_storage                     = 30
  max_allocated_storage                 = 100
  storage_type                          = "gp3"
  storage_encrypted                     = true
  db_name                               = "secureops"
  username                              = "secureops_admin"
  manage_master_user_password           = true
  port                                  = 5432
  db_subnet_group_name                  = aws_db_subnet_group.this.name
  vpc_security_group_ids                = [var.security_group_id]
  parameter_group_name                  = aws_db_parameter_group.this.name
  publicly_accessible                   = false
  multi_az                              = var.production
  backup_retention_period               = var.production ? 14 : 7
  backup_window                         = "03:00-04:00"
  maintenance_window                    = "sun:04:30-sun:05:30"
  auto_minor_version_upgrade            = true
  deletion_protection                   = var.production
  skip_final_snapshot                   = false
  final_snapshot_identifier             = "${var.name}-final"
  copy_tags_to_snapshot                 = true
  enabled_cloudwatch_logs_exports       = ["postgresql", "upgrade"]
  performance_insights_enabled          = true
  performance_insights_retention_period = 7
  apply_immediately                     = false
}
output "endpoint" { value = aws_db_instance.this.address }
output "identifier" { value = aws_db_instance.this.identifier }
output "secret_arn" { value = aws_db_instance.this.master_user_secret[0].secret_arn }
