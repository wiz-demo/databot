provider "aws" {
  region                      = "us-east-1"
  access_key                  = "AKIAIOSFODNN7EXAMPLE"
  secret_key                  = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true
}

variable "access_log_bucket_id" {
  description = "ID of the S3 bucket to receive access logs"
  type        = string
  default     = ""
}

resource "aws_s3_bucket" "partner_portal_assets" {
  bucket              = "partner-portal-static-assets"
  object_lock_enabled = true
}

resource "aws_s3_bucket_versioning" "partner_portal_assets" {
  bucket = aws_s3_bucket.partner_portal_assets.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "partner_portal_assets" {
  bucket = aws_s3_bucket.partner_portal_assets.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "partner_portal_assets" {
  bucket                  = aws_s3_bucket.partner_portal_assets.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "partner_portal_assets" {
  bucket     = aws_s3_bucket.partner_portal_assets.id
  depends_on = [aws_s3_bucket_versioning.partner_portal_assets]
  rule {
    id     = "expire-old-assets"
    status = "Enabled"
    filter { prefix = "" }
    expiration { days = 365 }
  }
}

resource "aws_s3_bucket_logging" "partner_portal_assets" {
  bucket        = aws_s3_bucket.partner_portal_assets.id
  target_bucket = var.access_log_bucket_id
  target_prefix = "partner-portal-assets/"
}

resource "aws_s3_bucket_policy" "partner_portal_assets" {
  bucket     = aws_s3_bucket.partner_portal_assets.id
  depends_on = [aws_s3_bucket_public_access_block.partner_portal_assets]
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "DenyHTTP"
      Effect    = "Deny"
      Principal = "*"
      Action    = "s3:*"
      Resource  = [
        aws_s3_bucket.partner_portal_assets.arn,
        "${aws_s3_bucket.partner_portal_assets.arn}/*"
      ]
      Condition = { Bool = { "aws:SecureTransport" = "false" } }
    }]
  })
}

resource "aws_s3_bucket_cors_configuration" "partner_portal_assets" {
  bucket = aws_s3_bucket.partner_portal_assets.id
  cors_rule {
    allowed_methods = ["GET", "HEAD"]
    allowed_headers = ["Authorization", "Content-Type"]
    allowed_origins = ["*"] # triggers the CORS policy
  }
}
