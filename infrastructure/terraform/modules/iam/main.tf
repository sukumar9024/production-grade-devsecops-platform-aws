locals {
  assume_ec2 = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Principal = { Service = "ec2.amazonaws.com" }, Action = "sts:AssumeRole" }] })
}
resource "aws_iam_role" "app" {
  name               = "${var.name}-app"
  assume_role_policy = local.assume_ec2
}
resource "aws_iam_role_policy_attachment" "ssm_app" {
  role       = aws_iam_role.app.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}
resource "aws_iam_role_policy" "app" {
  role = aws_iam_role.app.id
  policy = jsonencode({ Version = "2012-10-17", Statement = [
    { Effect = "Allow", Action = ["ecr:GetAuthorizationToken", "elasticloadbalancing:DescribeTargetHealth"], Resource = "*" },
    { Effect = "Allow", Action = ["ecr:BatchCheckLayerAvailability", "ecr:GetDownloadUrlForLayer", "ecr:BatchGetImage"], Resource = var.repository_arns },
    { Effect = "Allow", Action = ["secretsmanager:GetSecretValue"], Resource = var.secret_arns },
    { Effect = "Allow", Action = ["logs:CreateLogStream", "logs:PutLogEvents", "logs:DescribeLogStreams"], Resource = "${var.log_group_arn}:*" },
    { Effect = "Allow", Action = ["kms:Decrypt", "kms:GenerateDataKey"], Resource = var.bucket_kms_key_arn, Condition = { StringEquals = { "kms:ViaService" = "s3.${var.region}.amazonaws.com" } } },
    { Effect = "Allow", Action = ["s3:ListBucket"], Resource = var.bucket_arn },
    { Effect = "Allow", Action = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"], Resource = "${var.bucket_arn}/uploads/*" }
  ] })
}
resource "aws_iam_instance_profile" "app" {
  name = "${var.name}-app"
  role = aws_iam_role.app.name
}
resource "aws_iam_role" "jenkins" {
  count              = var.enable_jenkins ? 1 : 0
  name               = "${var.name}-jenkins"
  assume_role_policy = local.assume_ec2
}
resource "aws_iam_role_policy_attachment" "ssm_jenkins" {
  count      = var.enable_jenkins ? 1 : 0
  role       = aws_iam_role.jenkins[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}
resource "aws_iam_role_policy" "jenkins" {
  count = var.enable_jenkins ? 1 : 0
  role  = aws_iam_role.jenkins[0].id
  policy = jsonencode({ Version = "2012-10-17", Statement = [
    { Effect = "Allow", Action = ["ecr:GetAuthorizationToken", "ssm:GetCommandInvocation", "ec2:DescribeInstances", "elasticloadbalancing:DescribeTargetHealth"], Resource = "*" },
    { Effect = "Allow", Action = ["ecr:BatchCheckLayerAvailability", "ecr:GetDownloadUrlForLayer", "ecr:BatchGetImage", "ecr:InitiateLayerUpload", "ecr:UploadLayerPart", "ecr:CompleteLayerUpload", "ecr:PutImage", "ecr:DescribeImages"], Resource = var.repository_arns },
    { Effect = "Allow", Action = ["ssm:SendCommand"], Resource = "arn:aws:ssm:${var.region}::document/AWS-RunShellScript" },
    { Effect = "Allow", Action = ["ssm:SendCommand"], Resource = "arn:aws:ec2:${var.region}:${var.account_id}:instance/*", Condition = { StringEquals = { "ssm:resourceTag/Project" = "secureops", "ssm:resourceTag/Environment" = var.environment, "ssm:resourceTag/Role" = "app" } } }
  ] })
}
resource "aws_iam_instance_profile" "jenkins" {
  count = var.enable_jenkins ? 1 : 0
  name  = "${var.name}-jenkins"
  role  = aws_iam_role.jenkins[0].name
}
output "app_profile" { value = aws_iam_instance_profile.app.name }
output "jenkins_profile" { value = try(aws_iam_instance_profile.jenkins[0].name, null) }

output "app_role_arn" { value = aws_iam_role.app.arn }
resource "aws_iam_role_policy" "logs_search" {
  count  = var.enable_opensearch ? 1 : 0
  role   = aws_iam_role.app.id
  policy = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["es:ESHttpPost", "es:ESHttpPut", "es:ESHttpGet", "es:ESHttpHead", "es:ESHttpDelete"], Resource = "${var.opensearch_arn}/*" }] })
}
