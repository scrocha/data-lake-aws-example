locals {
  athena_results_prefix = "athena-results"
  bucket_name           = "${var.project_name}-${random_string.suffix.result}"
  glue_script_key       = "scripts/glue_taxi_etl.py"
  processed_database    = "${replace(var.project_name, "-", "_")}_processed"
  raw_database          = "${replace(var.project_name, "-", "_")}_raw"

  common_tags = merge(var.tags, {
    managed_by = "terraform"
    project    = var.project_name
  })
}
