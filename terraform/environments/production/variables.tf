variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.2.0.0/16"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "secure-it-starlink"
}
