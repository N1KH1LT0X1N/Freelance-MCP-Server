#!/bin/bash
# Freelance MCP Server - Installation Script
# Automates setup process for quick deployment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Header
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}                                                              ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}   Freelance MCP Server - Installation Script                ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}   Version 2.0.0                                              ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}                                                              ${BLUE}║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Python version
print_step "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3.11+ required (found $PYTHON_VERSION)"
        exit 1
    fi
else
    print_error "Python3 not found. Please install Python 3.11+"
    exit 1
fi

# Check pip
print_step "Checking pip..."
if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
    print_success "pip found"
else
    print_error "pip not found. Please install pip"
    exit 1
fi

# Install virtualenv if not present
print_step "Checking virtual environment support..."
if python3 -m venv --help &> /dev/null; then
    print_success "venv module available"
else
    print_warning "venv module not found. Installing..."
    pip3 install virtualenv
fi

# Create virtual environment
print_step "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment
print_step "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
print_step "Upgrading pip..."
pip install --upgrade pip --quiet
print_success "pip upgraded"

# Install requirements
print_step "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    print_success "Dependencies installed"
else
    print_error "requirements.txt not found"
    exit 1
fi

# Create necessary directories
print_step "Creating directories..."
mkdir -p data logs
print_success "Directories created"

# Setup .env file
print_step "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success ".env file created from template"
        print_warning "Please edit .env and add your GROQ_API_KEY"
    else
        print_error ".env.example not found"
    fi
else
    print_success ".env file already exists"
fi

# Run tests
print_step "Running validation tests..."
if python testcode/test_setup.py &> /dev/null; then
    print_success "Validation tests passed"
else
    print_warning "Some validation tests failed. Check configuration."
fi

# Final message
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}                                                              ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}   ✓ Installation Complete!                                  ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}                                                              ${GREEN}║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo -e "  1. Edit .env file and add your GROQ_API_KEY"
echo -e "     ${YELLOW}Get key from: https://console.groq.com/${NC}"
echo ""
echo -e "  2. Activate virtual environment:"
echo -e "     ${YELLOW}source venv/bin/activate${NC}"
echo ""
echo -e "  3. Run the server:"
echo -e "     ${YELLOW}python main.py${NC}"
echo ""
echo -e "  4. Or run comprehensive demo:"
echo -e "     ${YELLOW}python freelance_client.py --mode demo${NC}"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo -e "  • Quick Start: QUICKSTART.md"
echo -e "  • Usage Guide: USAGE.md"
echo -e "  • Deployment: DEPLOYMENT.md"
echo ""
