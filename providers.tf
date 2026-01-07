# Primary AWS Provider Configuration
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "secure-it-infra-Starlink"
      ManagedBy   = "Terraform"
      Environment = var.environment
      Owner       = var.owner
      CostCenter  = var.cost_center
    }
  }
}

# Secondary AWS Provider for Cross-Region Resources (e.g., CloudFront, ACM)
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"

  default_tags {
    tags = {
      Project     = "secure-it-infra-Starlink"
      ManagedBy   = "Terraform"
      Environment = var.environment
      Owner       = var.owner
      CostCenter  = var.cost_center
    }
  }
}

# Random Provider for generating unique identifiers
provider "random" {}

# Null Provider for provisioners and local-exec
provider "null" {}

# Time Provider for time-based resources
provider "time" {}

# TLS Provider for certificate generation
provider "tls" {}
