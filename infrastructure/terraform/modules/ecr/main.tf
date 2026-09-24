resource "aws_ecr_repository" "this" {
  for_each             = toset(["frontend", "backend"])
  name                 = "${var.name}-${each.key}"
  image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration { scan_on_push = true }
  encryption_configuration { encryption_type = "AES256" }
}
# Tagged releases are never expired automatically: keep previous releases rollback-safe.
resource "aws_ecr_lifecycle_policy" "this" {
  for_each   = aws_ecr_repository.this
  repository = each.value.name
  policy     = jsonencode({ rules = [{ rulePriority = 1, description = "Expire only untagged layers after 14 days", selection = { tagStatus = "untagged", countType = "sinceImagePushed", countUnit = "days", countNumber = 14 }, action = { type = "expire" } }] })
}
output "urls" { value = { for k, v in aws_ecr_repository.this : k => v.repository_url } }
output "arns" { value = [for v in aws_ecr_repository.this : v.arn] }
