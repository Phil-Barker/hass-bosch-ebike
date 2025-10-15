#!/bin/bash
# Development deployment script for Bosch eBike Home Assistant integration
# Syncs the custom component to a remote Home Assistant instance via SSH

set -e  # Exit on error

# Configuration
HA_HOST="${HA_HOST:-homeassistant.local}"  # Set via environment or default
HA_USER="${HA_USER:-root}"                  # Home Assistant SSH user
HA_PORT="${HA_PORT:-22}"                    # SSH port
HA_CONFIG_DIR="/config"                     # Home Assistant config directory

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print with color
info() { echo -e "${BLUE}ℹ${NC} $1"; }
success() { echo -e "${GREEN}✓${NC} $1"; }
warning() { echo -e "${YELLOW}⚠${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; }

# Check if custom_components exists
if [ ! -d "custom_components/bosch_ebike" ]; then
    error "custom_components/bosch_ebike directory not found!"
    error "Run this script from the project root directory."
    exit 1
fi

echo ""
info "Bosch eBike - Development Deployment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Show configuration
info "Configuration:"
echo "  Host: ${HA_USER}@${HA_HOST}:${HA_PORT}"
echo "  Destination: ${HA_CONFIG_DIR}/custom_components/bosch_ebike"
echo ""

# Test SSH connection
info "Testing SSH connection..."
if ! ssh -p "${HA_PORT}" -o ConnectTimeout=5 "${HA_USER}@${HA_HOST}" "echo 'Connection successful'" >/dev/null 2>&1; then
    error "Cannot connect to Home Assistant via SSH"
    echo ""
    echo "Please check:"
    echo "  1. SSH add-on is running on Home Assistant"
    echo "  2. Host is correct: ${HA_HOST}"
    echo "  3. Port is correct: ${HA_PORT}"
    echo "  4. SSH keys are set up (or use password)"
    echo ""
    echo "You can override settings:"
    echo "  HA_HOST=192.168.1.100 HA_PORT=22222 ./deploy-dev.sh"
    exit 1
fi
success "SSH connection successful"
echo ""

# Check if rsync is available on remote
info "Checking sync method..."
if ssh -p "${HA_PORT}" "${HA_USER}@${HA_HOST}" "command -v rsync" >/dev/null 2>&1; then
    # Use rsync (faster, more efficient)
    info "Using rsync for file sync..."
    rsync -avz --delete \
        -e "ssh -p ${HA_PORT}" \
        --exclude="__pycache__" \
        --exclude="*.pyc" \
        --exclude=".DS_Store" \
        custom_components/bosch_ebike/ \
        "${HA_USER}@${HA_HOST}:${HA_CONFIG_DIR}/custom_components/bosch_ebike/"
    
    if [ $? -eq 0 ]; then
        success "Files synced successfully (rsync)"
    else
        error "Failed to sync files"
        exit 1
    fi
else
    # Fallback to scp (available on all systems)
    warning "rsync not available, using scp..."
    
    # Create remote directory
    ssh -p "${HA_PORT}" "${HA_USER}@${HA_HOST}" "mkdir -p ${HA_CONFIG_DIR}/custom_components/bosch_ebike/translations"
    
    # Copy files using scp
    scp -P "${HA_PORT}" -r \
        custom_components/bosch_ebike/* \
        "${HA_USER}@${HA_HOST}:${HA_CONFIG_DIR}/custom_components/bosch_ebike/"
    
    if [ $? -eq 0 ]; then
        success "Files synced successfully (scp)"
    else
        error "Failed to sync files"
        exit 1
    fi
fi
echo ""

# Check if Home Assistant is running
info "Checking Home Assistant status..."
if ssh -p "${HA_PORT}" "${HA_USER}@${HA_HOST}" "ha core info" >/dev/null 2>&1; then
    success "Home Assistant is running"
    echo ""
    
    # Ask if they want to restart
    read -p "$(echo -e ${YELLOW}⚠${NC}) Restart Home Assistant to load changes? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        info "Restarting Home Assistant..."
        ssh -p "${HA_PORT}" "${HA_USER}@${HA_HOST}" "ha core restart"
        success "Restart command sent"
        echo ""
        warning "Home Assistant is restarting... (this takes ~30 seconds)"
        warning "Wait for it to come back online before testing"
    else
        echo ""
        warning "Remember to restart Home Assistant manually to load changes:"
        echo "  - Settings → System → Restart"
        echo "  - Or via SSH: ha core restart"
    fi
else
    warning "Could not check Home Assistant status"
    warning "You may need to restart manually to load changes"
fi

echo ""
success "Deployment complete!"
echo ""
info "Next steps:"
echo "  1. Wait for Home Assistant to restart (if you chose to)"
echo "  2. Go to: Settings → Devices & Services"
echo "  3. Add Integration → Search for 'Bosch eBike'"
echo "  4. Follow the OAuth setup flow"
echo ""
info "To redeploy after changes, just run: ./deploy-dev.sh"
echo ""

