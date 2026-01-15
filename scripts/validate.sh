#!/bin/bash
# Validation script to test infrastructure setup
# This script performs basic validation of the deployment infrastructure

set -eo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(dirname "$0")"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Counters
TESTS_PASSED=0
TESTS_FAILED=0

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

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
    ((TESTS_PASSED++))
}

print_failure() {
    echo -e "${RED}[✗]${NC} $1"
    ((TESTS_FAILED++))
}

# Test function
test_file_exists() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ]; then
        print_success "$description"
    else
        print_failure "$description - File not found: $file"
    fi
}

test_directory_exists() {
    local dir=$1
    local description=$2
    
    if [ -d "$dir" ]; then
        print_success "$description"
    else
        print_failure "$description - Directory not found: $dir"
    fi
}

test_script_executable() {
    local script=$1
    local description=$2
    
    if [ -x "$script" ]; then
        print_success "$description"
    else
        print_failure "$description - Script not executable: $script"
    fi
}

print_info "Starting infrastructure validation..."
echo ""

# Test directory structure
print_info "Checking directory structure..."
test_directory_exists "$REPO_ROOT/terraform" "Terraform directory exists"
test_directory_exists "$REPO_ROOT/terraform/modules" "Terraform modules directory exists"
test_directory_exists "$REPO_ROOT/terraform/modules/network" "Network module directory exists"
test_directory_exists "$REPO_ROOT/terraform/modules/security" "Security module directory exists"
test_directory_exists "$REPO_ROOT/terraform/environments" "Environments directory exists"
test_directory_exists "$REPO_ROOT/terraform/environments/dev" "Dev environment directory exists"
test_directory_exists "$REPO_ROOT/terraform/environments/staging" "Staging environment directory exists"
test_directory_exists "$REPO_ROOT/terraform/environments/production" "Production environment directory exists"
test_directory_exists "$REPO_ROOT/scripts" "Scripts directory exists"
test_directory_exists "$REPO_ROOT/docs" "Documentation directory exists"
test_directory_exists "$REPO_ROOT/.github/workflows" "GitHub workflows directory exists"
echo ""

# Test Terraform files
print_info "Checking Terraform configuration files..."
test_file_exists "$REPO_ROOT/terraform/modules/network/main.tf" "Network module main.tf exists"
test_file_exists "$REPO_ROOT/terraform/modules/security/main.tf" "Security module main.tf exists"

for env in dev staging production; do
    test_file_exists "$REPO_ROOT/terraform/environments/$env/main.tf" "$env environment main.tf exists"
    test_file_exists "$REPO_ROOT/terraform/environments/$env/variables.tf" "$env environment variables.tf exists"
    test_file_exists "$REPO_ROOT/terraform/environments/$env/outputs.tf" "$env environment outputs.tf exists"
done
echo ""

# Test scripts
print_info "Checking deployment scripts..."
test_file_exists "$REPO_ROOT/scripts/deploy.sh" "Deploy script exists"
test_file_exists "$REPO_ROOT/scripts/rollback.sh" "Rollback script exists"
test_script_executable "$REPO_ROOT/scripts/deploy.sh" "Deploy script is executable"
test_script_executable "$REPO_ROOT/scripts/rollback.sh" "Rollback script is executable"
echo ""

# Test documentation
print_info "Checking documentation..."
test_file_exists "$REPO_ROOT/README.md" "README.md exists"
test_file_exists "$REPO_ROOT/docs/DEPLOYMENT.md" "Deployment guide exists"
test_file_exists "$REPO_ROOT/docs/TESTING_CHECKLIST.md" "Testing checklist exists"
echo ""

# Test GitHub Actions workflows
print_info "Checking GitHub Actions workflows..."
test_file_exists "$REPO_ROOT/.github/workflows/terraform-validate.yml" "Terraform validation workflow exists"
test_file_exists "$REPO_ROOT/.github/workflows/deploy.yml" "Deployment workflow exists"
echo ""

# Validate Terraform syntax (if Terraform is installed)
if command -v terraform &> /dev/null; then
    print_info "Validating Terraform configurations..."
    
    for env in dev staging production; do
        ENV_DIR="$REPO_ROOT/terraform/environments/$env"
        cd "$ENV_DIR"
        
        if terraform init -backend=false > /dev/null 2>&1; then
            if terraform validate > /dev/null 2>&1; then
                print_success "$env environment Terraform config is valid"
            else
                print_failure "$env environment Terraform validation failed"
            fi
        else
            print_failure "$env environment Terraform init failed"
        fi
    done
    echo ""
else
    print_warning "Terraform not installed, skipping Terraform validation"
    echo ""
fi

# Print summary
echo "=================================="
print_info "Validation Summary"
echo "=================================="
echo -e "${GREEN}Tests Passed:${NC} $TESTS_PASSED"
echo -e "${RED}Tests Failed:${NC} $TESTS_FAILED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    print_success "All validation checks passed!"
    exit 0
else
    print_error "Some validation checks failed. Please review the errors above."
    exit 1
fi
