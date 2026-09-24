data "aws_ssm_parameter" "ami" { name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64" }
resource "aws_instance" "app" {
  count                       = var.instance_count
  ami                         = data.aws_ssm_parameter.ami.value
  instance_type               = var.instance_type
  subnet_id                   = var.subnet_ids[count.index % length(var.subnet_ids)]
  associate_public_ip_address = false
  vpc_security_group_ids      = [var.security_group_ids["app"]]
  iam_instance_profile        = var.app_profile
  monitoring                  = true
  metadata_options {
    http_tokens                 = "required"
    http_put_response_hop_limit = 2
    http_endpoint               = "enabled"
  }
  root_block_device {
    volume_size = 40
    volume_type = "gp3"
    encrypted   = true
  }
  user_data = "#!/bin/bash\nset -eu\nsystemctl enable --now amazon-ssm-agent\n"
  tags      = { Name = "${var.name}-app-${count.index + 1}", Role = "app" }
}
resource "aws_instance" "jenkins" {
  count                       = var.enable_jenkins ? 1 : 0
  ami                         = data.aws_ssm_parameter.ami.value
  instance_type               = "t3.large"
  subnet_id                   = var.subnet_ids[0]
  associate_public_ip_address = false
  vpc_security_group_ids      = [var.security_group_ids["jenkins"]]
  iam_instance_profile        = var.jenkins_profile
  monitoring                  = true
  metadata_options {
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }
  root_block_device {
    volume_size = 80
    volume_type = "gp3"
    encrypted   = true
  }
  tags = { Name = "${var.name}-jenkins", Role = "jenkins" }
}
output "instance_ids" { value = aws_instance.app[*].id }
output "jenkins_id" { value = try(aws_instance.jenkins[0].id, null) }
