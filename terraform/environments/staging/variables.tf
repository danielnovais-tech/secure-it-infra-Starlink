variable "aws_region" {
  type        = string
  description = "AWS region for resources"
  default     = "us-east-1"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for VPC"
  default     = "10.1.0.0/16"
}

variable "project_name" {
  type        = string
  description = "Project identifier"
  default     = "secure-it-starlink"
}
