# Backend Configuration for Remote State Management
# This file configures Terraform to store state remotely in AWS S3
# with state locking via DynamoDB for safe concurrent operations

# Uncomment and configure the backend block below after creating the S3 bucket and DynamoDB table
# terraform {
#   backend "s3" {
#     # S3 bucket for storing Terraform state
#     bucket = "secure-it-starlink-terraform-state"
#     
#     # State file path within the bucket
#     key    = "foundation/terraform.tfstate"
#     
#     # AWS region where the S3 bucket is located
#     region = "us-west-2"
#     
#     # DynamoDB table for state locking
#     dynamodb_table = "secure-it-starlink-terraform-locks"
#     
#     # Enable encryption at rest
#     encrypt = true
#     
#     # Additional security settings
#     # acl     = "private"
#     # kms_key_id = "arn:aws:kms:us-west-2:ACCOUNT_ID:key/KEY_ID"
#   }
# }

# To initialize the backend:
# 1. Create an S3 bucket for state storage:
#    aws s3api create-bucket \
#      --bucket secure-it-starlink-terraform-state \
#      --region us-west-2 \
#      --create-bucket-configuration LocationConstraint=us-west-2
#
# 2. Enable versioning on the bucket:
#    aws s3api put-bucket-versioning \
#      --bucket secure-it-starlink-terraform-state \
#      --versioning-configuration Status=Enabled
#
# 3. Enable encryption:
#    aws s3api put-bucket-encryption \
#      --bucket secure-it-starlink-terraform-state \
#      --server-side-encryption-configuration \
#      '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
#
# 4. Create DynamoDB table for state locking:
#    aws dynamodb create-table \
#      --table-name secure-it-starlink-terraform-locks \
#      --attribute-definitions AttributeName=LockID,AttributeType=S \
#      --key-schema AttributeName=LockID,KeyType=HASH \
#      --billing-mode PAY_PER_REQUEST \
#      --region us-west-2
#
# 5. Uncomment the backend block above
# 6. Run: terraform init -migrate-state
