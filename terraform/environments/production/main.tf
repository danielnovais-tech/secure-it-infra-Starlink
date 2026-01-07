# Production Environment Configuration

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Uncomment and configure when using remote backend
  # backend "s3" {
  #   bucket         = "secure-it-starlink-terraform-state"
  #   key            = "production/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-state-lock"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = "production"
      Project     = "secure-it-starlink"
      ManagedBy   = "terraform"
    }
  }
}

# Network Module
module "network" {
  source = "../../modules/network"

  environment  = "production"
  vpc_cidr     = var.vpc_cidr
  project_name = var.project_name
}

# Security Module
module "security" {
  source = "../../modules/security"

  environment  = "production"
  vpc_id       = module.network.vpc_id
  project_name = var.project_name
}
