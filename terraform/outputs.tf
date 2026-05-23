output "athena_results_s3_uri" {
  description = "Prefixo S3 usado pelos resultados do Athena."
  value       = "s3://${aws_s3_bucket.data_lake.bucket}/${local.athena_results_prefix}/"
}

output "athena_workgroup_name" {
  description = "Nome do workgroup Athena."
  value       = aws_athena_workgroup.main.name
}

output "aws_account_id" {
  description = "ID da conta AWS em uso."
  value       = data.aws_caller_identity.current.account_id
}

output "aws_region" {
  description = "Região AWS usada no deploy."
  value       = var.aws_region
}

output "data_lake_bucket_arn" {
  description = "ARN do bucket principal do data lake."
  value       = aws_s3_bucket.data_lake.arn
}

output "data_lake_bucket_name" {
  description = "Nome do bucket principal do data lake."
  value       = aws_s3_bucket.data_lake.bucket
}

output "glue_job_name" {
  description = "Nome do Glue job principal."
  value       = aws_glue_job.main.name
}

output "glue_processed_crawler_name" {
  description = "Nome do crawler da zona processed."
  value       = aws_glue_crawler.processed.name
}

output "glue_processed_database_name" {
  description = "Nome do database Glue da zona processed."
  value       = aws_glue_catalog_database.processed.name
}

output "glue_raw_crawler_name" {
  description = "Nome do crawler da zona raw."
  value       = aws_glue_crawler.raw.name
}

output "glue_raw_database_name" {
  description = "Nome do database Glue da zona raw."
  value       = aws_glue_catalog_database.raw.name
}

output "glue_role_arn" {
  description = "ARN da role existente usada pelo Glue."
  value       = data.aws_iam_role.glue_service_role.arn
}
