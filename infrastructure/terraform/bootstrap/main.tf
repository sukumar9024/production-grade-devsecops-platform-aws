variable "region" {
  type    = string
  default = "ap-south-1"
}
variable "state_bucket_name" { type = string }
provider "aws" { region = var.region }
resource "aws_kms_key" "state" {
  description             = "SecureOps Terraform state encryption"
  enable_key_rotation     = true
  deletion_window_in_days = 30
  lifecycle { prevent_destroy = true }
}
resource "aws_kms_alias" "state" {
  name          = "alias/secureops-terraform-state"
  target_key_id = aws_kms_key.state.key_id
}
resource "aws_s3_bucket" "state" {
  bucket = var.state_bucket_name
  lifecycle { prevent_destroy = true }
}
resource "aws_s3_bucket_public_access_block" "state" {
  bucket                  = aws_s3_bucket.state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id
  versioning_configuration { status = "Enabled" }
}
resource "aws_s3_bucket_server_side_encryption_configuration" "state" {
  bucket = aws_s3_bucket.state.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.state.arn
    }
    bucket_key_enabled = true
  }
}
resource "aws_s3_bucket_policy" "state" {
  bucket = aws_s3_bucket.state.id
  policy = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Deny", Principal = "*", Action = "s3:*", Resource = [aws_s3_bucket.state.arn, "${aws_s3_bucket.state.arn}/*"], Condition = { Bool = { "aws:SecureTransport" = "false" } } }] })
}
# Separate short-lived transfer bucket: never use versioned state/application buckets for Ansible modules.
resource "aws_s3_bucket" "ansible" { bucket = "${var.state_bucket_name}-ansible" }
resource "aws_s3_bucket_public_access_block" "ansible" {
  bucket                  = aws_s3_bucket.ansible.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
resource "aws_s3_bucket_server_side_encryption_configuration" "ansible" {
  bucket = aws_s3_bucket.ansible.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.state.arn
    }
  }
}
resource "aws_s3_bucket_lifecycle_configuration" "ansible" {
  bucket = aws_s3_bucket.ansible.id
  rule {
    id     = "expire-transfer-artifacts"
    status = "Enabled"
    filter {}
    expiration { days = 1 }
    abort_incomplete_multipart_upload { days_after_initiation = 1 }
  }
}
resource "aws_s3_bucket_policy" "ansible" {
  bucket = aws_s3_bucket.ansible.id
  policy = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Deny", Principal = "*", Action = "s3:*", Resource = [aws_s3_bucket.ansible.arn, "${aws_s3_bucket.ansible.arn}/*"], Condition = { Bool = { "aws:SecureTransport" = "false" } } }] })
}
output "state_bucket" { value = aws_s3_bucket.state.id }
output "kms_key_arn" { value = aws_kms_key.state.arn }
output "ansible_transfer_bucket" { value = aws_s3_bucket.ansible.id }
