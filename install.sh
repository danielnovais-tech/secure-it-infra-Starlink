#!/bin/bash
#
# Starlink Security Auditor - Installation Script
# This script installs and configures the security auditor
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/starlink-security"
CONFIG_DIR="/etc/starlink-security"
LOG_DIR="/var/log/starlink-security"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Starlink Security Auditor Installation${NC}"
echo -e "${GREEN}========================================${NC}"
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Error: This script must be run as root${NC}"
    echo "Please run: sudo $0"
    exit 1
fi

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.7 or later"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Create directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$LOG_DIR"
echo -e "${GREEN}✓ Directories created${NC}"

# Copy files
echo -e "${YELLOW}Installing files...${NC}"
if [ -f "starlink_security_auditor.py" ]; then
    cp starlink_security_auditor.py "$INSTALL_DIR/"
    chmod +x "$INSTALL_DIR/starlink_security_auditor.py"
    echo -e "${GREEN}✓ Main script installed${NC}"
else
    echo -e "${RED}Error: starlink_security_auditor.py not found${NC}"
    exit 1
fi

# Copy configuration
if [ -f "config.example.json" ]; then
    if [ ! -f "$CONFIG_DIR/config.json" ]; then
        cp config.example.json "$CONFIG_DIR/config.json"
        echo -e "${GREEN}✓ Configuration file installed${NC}"
    else
        echo -e "${YELLOW}! Configuration file already exists, skipping${NC}"
    fi
fi

# Copy documentation
echo -e "${YELLOW}Installing documentation...${NC}"
for doc in README.md ARCHITECTURE.md DEPLOYMENT.md SECURITY_BEST_PRACTICES.md QUICKSTART.md; do
    if [ -f "$doc" ]; then
        cp "$doc" "$INSTALL_DIR/"
    fi
done
echo -e "${GREEN}✓ Documentation installed${NC}"

# Set permissions
echo -e "${YELLOW}Setting permissions...${NC}"
chown -R root:root "$INSTALL_DIR"
chmod 755 "$INSTALL_DIR"
chmod 750 "$INSTALL_DIR/starlink_security_auditor.py"

chown -R root:root "$CONFIG_DIR"
chmod 750 "$CONFIG_DIR"
chmod 640 "$CONFIG_DIR/config.json"

chown root:adm "$LOG_DIR"
chmod 750 "$LOG_DIR"
echo -e "${GREEN}✓ Permissions set${NC}"

# Create symbolic link
echo -e "${YELLOW}Creating command alias...${NC}"
ln -sf "$INSTALL_DIR/starlink_security_auditor.py" /usr/local/bin/starlink-audit
echo -e "${GREEN}✓ Command 'starlink-audit' is now available${NC}"

# Update configuration paths
echo -e "${YELLOW}Updating configuration...${NC}"
if [ -f "$CONFIG_DIR/config.json" ]; then
    # Update log and report paths in config
    sed -i "s|\"file\": \"security_audit.log\"|\"file\": \"$LOG_DIR/security_audit.log\"|g" "$CONFIG_DIR/config.json"
    sed -i "s|\"output_file\": \"security_audit_report.json\"|\"output_file\": \"$LOG_DIR/security_audit_report.json\"|g" "$CONFIG_DIR/config.json"
    echo -e "${GREEN}✓ Configuration updated${NC}"
fi

# Offer to schedule cron job
echo
echo -e "${YELLOW}Would you like to schedule automatic daily audits? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Setting up daily audit at 2:00 AM...${NC}"
    
    # Create cron job
    CRON_CMD="0 2 * * * $INSTALL_DIR/starlink_security_auditor.py -c $CONFIG_DIR/config.json -q"
    
    # Check if cron job already exists (use exact path match)
    if ! crontab -l 2>/dev/null | grep -F "$INSTALL_DIR/starlink_security_auditor.py" > /dev/null 2>&1; then
        (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
        echo -e "${GREEN}✓ Daily audit scheduled${NC}"
    else
        echo -e "${YELLOW}! Cron job already exists${NC}"
    fi
fi

# Run initial audit
echo
echo -e "${YELLOW}Would you like to run an initial security audit now? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Running security audit...${NC}"
    echo
    "$INSTALL_DIR/starlink_security_auditor.py" -c "$CONFIG_DIR/config.json" || true
fi

# Installation complete
echo
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo
echo -e "Installation directory: ${GREEN}$INSTALL_DIR${NC}"
echo -e "Configuration file: ${GREEN}$CONFIG_DIR/config.json${NC}"
echo -e "Log directory: ${GREEN}$LOG_DIR${NC}"
echo
echo -e "Quick commands:"
echo -e "  Run audit: ${GREEN}sudo starlink-audit${NC}"
echo -e "  With config: ${GREEN}sudo starlink-audit -c $CONFIG_DIR/config.json${NC}"
echo -e "  View help: ${GREEN}starlink-audit --help${NC}"
echo
echo -e "Documentation:"
echo -e "  Quick Start: ${GREEN}cat $INSTALL_DIR/QUICKSTART.md${NC}"
echo -e "  Full README: ${GREEN}cat $INSTALL_DIR/README.md${NC}"
echo
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Review and customize: $CONFIG_DIR/config.json"
echo "2. Run your first audit: sudo starlink-audit"
echo "3. Address any FAIL or WARN findings"
echo "4. Read security best practices: $INSTALL_DIR/SECURITY_BEST_PRACTICES.md"
echo
