# Main Terraform Configuration for Secure IT Infrastructure - Starlink
# This file contains the core infrastructure setup and data sources

# Data source to get current AWS account information
data "aws_caller_identity" "current" {}

# Data source to get current AWS region information
data "aws_region" "current" {}

# Data source to get available AWS availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# Local variables for common configurations
locals {
  # Common name prefix for resources
  name_prefix = "secure-it-starlink-${var.environment}"

  # Combined tags
  common_tags = merge(
    {
      Project     = "secure-it-infra-Starlink"
      ManagedBy   = "Terraform"
      Environment = var.environment
      Owner       = var.owner
      CostCenter  = var.cost_center
    },
    var.additional_tags
  )

  # Account and region information
  account_id = data.aws_caller_identity.current.account_id
  region     = data.aws_region.current.name

  # Availability zones (up to 3, or fewer if region has less)
  azs = slice(data.aws_availability_zones.available.names, 0, min(3, length(data.aws_availability_zones.available.names)))
}
