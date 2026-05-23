data "aws_caller_identity" "current" {}

data "aws_iam_role" "glue_service_role" {
  name = var.glue_role_name
}

resource "random_string" "suffix" {
  length  = 6
  lower   = true
  numeric = true
  special = false
  upper   = false
}

resource "aws_s3_bucket" "data_lake" {
  bucket        = local.bucket_name
  force_destroy = true
  tags          = local.common_tags
}

resource "aws_s3_bucket_public_access_block" "data_lake" {
  bucket                  = aws_s3_bucket.data_lake.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_object" "glue_etl_script" {
  bucket       = aws_s3_bucket.data_lake.id
  key          = local.glue_script_key
  source       = "${path.module}/../scripts/glue_taxi_etl.py"
  etag         = filemd5("${path.module}/../scripts/glue_taxi_etl.py")
  content_type = "text/x-python"
}

resource "aws_glue_catalog_database" "raw" {
  name = local.raw_database
}

resource "aws_glue_catalog_database" "processed" {
  name = local.processed_database
}

resource "aws_glue_crawler" "raw" {
  name          = "${local.bucket_name}-raw-crawler"
  role          = data.aws_iam_role.glue_service_role.arn
  database_name = aws_glue_catalog_database.raw.name
  description   = "Cataloga os dados raw do NYC Taxi."

  s3_target {
    path = "s3://${aws_s3_bucket.data_lake.bucket}/raw/nyc_taxi/"
  }

  tags = local.common_tags
}

resource "aws_glue_crawler" "processed" {
  name          = "${local.bucket_name}-processed-crawler"
  role          = data.aws_iam_role.glue_service_role.arn
  database_name = aws_glue_catalog_database.processed.name
  description   = "Cataloga os dados processed do NYC Taxi."

  s3_target {
    path = "s3://${aws_s3_bucket.data_lake.bucket}/processed/taxi_trips_clean/"
  }

  s3_target {
    path = "s3://${aws_s3_bucket.data_lake.bucket}/processed/taxi_monthly_metrics/"
  }

  tags = local.common_tags
}

resource "aws_glue_job" "main" {
  name              = "${local.bucket_name}-taxi-etl"
  role_arn          = data.aws_iam_role.glue_service_role.arn
  description       = "ETL serverless do NYC Taxi."
  glue_version      = "4.0"
  max_retries       = 0
  number_of_workers = 2
  timeout           = 10
  worker_type       = "G.1X"

  command {
    python_version  = "3"
    script_location = "s3://${aws_s3_bucket.data_lake.bucket}/${aws_s3_object.glue_etl_script.key}"
  }

  default_arguments = {
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-metrics"                   = "true"
    "--job-language"                     = "python"
    "--processed_bucket"                 = aws_s3_bucket.data_lake.bucket
    "--raw_database"                     = aws_glue_catalog_database.raw.name
  }

  tags = local.common_tags
}

resource "aws_athena_workgroup" "main" {
  name          = "${local.bucket_name}-wg"
  force_destroy = true

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = "s3://${aws_s3_bucket.data_lake.bucket}/${local.athena_results_prefix}/"
    }
  }

  tags = local.common_tags
}
