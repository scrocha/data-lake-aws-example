variable "aws_region" {
  description = "Região AWS da demo."
  type        = string
  default     = "us-east-1"
}

variable "glue_role_name" {
  description = "Nome de uma role IAM já existente e compatível com AWS Glue."
  type        = string
  default     = "LabRole"
}

variable "project_name" {
  description = "Prefixo para nomear os recursos."
  type        = string
  default     = "nyc-taxi-lake"
}

variable "tags" {
  description = "Tags comuns dos recursos."
  type        = map(string)

  default = {
    project = "data-lake-aws-example"
  }
}
