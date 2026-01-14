#!/bin/bash
# Rollback script for infrastructure deployment
# This script helps rollback infrastructure changes in case of issues

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if environment is provided
if [ $# -eq 0 ]; then
    print_error "Environment not specified"
    echo "Usage: $0 <environment>"
    echo "Environments: dev, staging, production"
    exit 1
fi

ENVIRONMENT=$1
TERRAFORM_DIR="$(dirname "$0")/../terraform/environments/${ENVIRONMENT}"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|production)$ ]]; then
    print_error "Invalid environment: $ENVIRONMENT"
    echo "Valid environments: dev, staging, production"
    exit 1
fi

# Check if Terraform directory exists
if [ ! -d "$TERRAFORM_DIR" ]; then
    print_error "Terraform directory not found: $TERRAFORM_DIR"
    exit 1
fi

print_warning "Rollback for environment: $ENVIRONMENT"

# Navigate to terraform directory
cd "$TERRAFORM_DIR"

# Safety check for production
if [ "$ENVIRONMENT" == "production" ]; then
    print_warning "You are about to rollback PRODUCTION environment!"
    read -p "Are you sure you want to continue? (yes/no): " confirmation
    if [ "$confirmation" != "yes" ]; then
        print_info "Rollback cancelled"
        exit 0
    fi
fi

# Check if state file exists
if [ ! -f "terraform.tfstate" ] && [ ! -f ".terraform/terraform.tfstate" ]; then
    print_error "No Terraform state found. Cannot perform rollback."
    exit 1
fi

# Initialize Terraform
print_info "Initializing Terraform..."
terraform init

# Show current state
print_info "Current infrastructure state:"
terraform show

# List available state backups
print_info "Available state backups:"
ls -lh terraform.tfstate.backup* 2>/dev/null || print_warning "No backup state files found"

# Provide options
echo ""
print_warning "Rollback options:"
echo "1. Restore from state backup (terraform.tfstate.backup)"
echo "2. Manually revert to previous configuration (requires manual intervention)"
echo "3. Cancel rollback"
read -p "Select option (1-3): " option

case $option in
    1)
        if [ -f "terraform.tfstate.backup" ]; then
            print_info "Backing up current state..."
            cp terraform.tfstate terraform.tfstate.pre-rollback-$(date +%Y%m%d-%H%M%S)
            
            print_info "Restoring from backup..."
            cp terraform.tfstate.backup terraform.tfstate
            
            print_info "Applying restored state..."
            terraform apply -refresh-only
            
            print_info "Rollback completed successfully"
        else
            print_error "No backup state file found"
            exit 1
        fi
        ;;
    2)
        print_info "Manual rollback selected"
        print_info "Please:"
        print_info "1. Revert your infrastructure code to the previous version"
        print_info "2. Run: ./scripts/deploy.sh $ENVIRONMENT plan"
        print_info "3. Review the plan"
        print_info "4. Run: ./scripts/deploy.sh $ENVIRONMENT apply"
        ;;
    3)
        print_info "Rollback cancelled"
        exit 0
        ;;
    *)
        print_error "Invalid option"
        exit 1
        ;;
esac
