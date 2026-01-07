#!/bin/bash
# Deployment script with safety checks for controlled environment deployment
# This script ensures safe deployment by validating infrastructure changes before applying

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
    echo "Usage: $0 <environment> [action]"
    echo "Environments: dev, staging, production"
    echo "Actions: plan (default), apply, destroy"
    exit 1
fi

ENVIRONMENT=$1
ACTION=${2:-plan}
TERRAFORM_DIR="$(dirname "$0")/../terraform/environments/${ENVIRONMENT}"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|production)$ ]]; then
    print_error "Invalid environment: $ENVIRONMENT"
    echo "Valid environments: dev, staging, production"
    exit 1
fi

# Validate action
if [[ ! "$ACTION" =~ ^(plan|apply|destroy)$ ]]; then
    print_error "Invalid action: $ACTION"
    echo "Valid actions: plan, apply, destroy"
    exit 1
fi

# Check if Terraform directory exists
if [ ! -d "$TERRAFORM_DIR" ]; then
    print_error "Terraform directory not found: $TERRAFORM_DIR"
    exit 1
fi

print_info "Deploying to environment: $ENVIRONMENT"
print_info "Action: $ACTION"

# Navigate to terraform directory
cd "$TERRAFORM_DIR"

# Safety check for production
if [ "$ENVIRONMENT" == "production" ]; then
    if [ "$ACTION" == "apply" ] || [ "$ACTION" == "destroy" ]; then
        # Skip confirmations in automation mode
        if [ "${TF_IN_AUTOMATION:-false}" == "true" ]; then
            print_warning "Running in automation mode - skipping interactive confirmations"
            print_warning "Proceeding with $ACTION to PRODUCTION environment"
        else
            print_warning "You are about to $ACTION changes to PRODUCTION environment!"
            read -p "Are you sure you want to continue? (yes/no): " confirmation
            if [ "$confirmation" != "yes" ]; then
                print_info "Deployment cancelled"
                exit 0
            fi
            
            # Require additional confirmation for destroy
            if [ "$ACTION" == "destroy" ]; then
                print_warning "DANGER: This will DESTROY production infrastructure!"
                read -p "Type 'DELETE-PRODUCTION' to confirm: " delete_confirm
                if [ "$delete_confirm" != "DELETE-PRODUCTION" ]; then
                    print_info "Deployment cancelled"
                    exit 0
                fi
            fi
        fi
    fi
fi

# Initialize Terraform
print_info "Initializing Terraform..."
terraform init

# Validate Terraform configuration
print_info "Validating Terraform configuration..."
if ! terraform validate; then
    print_error "Terraform validation failed"
    exit 1
fi

# Format check
print_info "Checking Terraform formatting..."
terraform fmt -check -recursive || {
    print_warning "Terraform files are not properly formatted"
    print_info "Running terraform fmt..."
    # Temporarily disable 'exit on error' to handle fmt failures explicitly
    set +e
    terraform fmt -recursive
    FMT_STATUS=$?
    set -e
    if [ "$FMT_STATUS" -ne 0 ]; then
        print_error "terraform fmt -recursive failed with exit code ${FMT_STATUS}; continuing without aborting deployment"
    fi
}

# Run Terraform action
case $ACTION in
    plan)
        print_info "Running Terraform plan..."
        terraform plan -out=tfplan
        print_info "Plan saved to tfplan"
        print_info "Review the plan above before applying"
        ;;
    apply)
        # Check if plan exists
        if [ -f "tfplan" ]; then
            print_info "Applying Terraform plan..."
            terraform apply tfplan
            rm -f tfplan
            print_info "Deployment completed successfully"
        else
            print_warning "No plan file found, creating and applying new plan..."
            terraform plan -out=tfplan
            
            # Auto-approve in automation mode, otherwise ask for confirmation
            if [ "${TF_IN_AUTOMATION:-false}" == "true" ]; then
                print_info "Running in automation mode - auto-approving plan"
                terraform apply tfplan
                rm -f tfplan
                print_info "Deployment completed successfully"
            else
                read -p "Apply this plan? (yes/no): " apply_confirm
                if [ "$apply_confirm" == "yes" ]; then
                    terraform apply tfplan
                    rm -f tfplan
                    print_info "Deployment completed successfully"
                else
                    print_info "Deployment cancelled"
                    rm -f tfplan
                    exit 0
                fi
            fi
        fi
        ;;
    destroy)
        print_info "Planning destruction..."
        terraform plan -destroy -out=tfplan
        print_warning "Review the destruction plan above"
        
        # Auto-approve in automation mode, otherwise ask for confirmation
        if [ "${TF_IN_AUTOMATION:-false}" == "true" ]; then
            print_warning "Running in automation mode - auto-approving destruction"
            terraform apply tfplan
            rm -f tfplan
            print_info "Destruction completed"
        else
            read -p "Proceed with destroy? (yes/no): " destroy_confirm
            if [ "$destroy_confirm" == "yes" ]; then
                terraform apply tfplan
                rm -f tfplan
                print_info "Destruction completed"
            else
                print_info "Destruction cancelled"
                rm -f tfplan
                exit 0
            fi
        fi
        ;;
esac

print_info "Script completed successfully"
