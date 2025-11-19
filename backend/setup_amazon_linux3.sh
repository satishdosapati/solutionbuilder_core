#!/bin/bash
# Amazon Linux 3 Setup Script for Nebula.AI
# This script automates the setup process on Amazon Linux 3

set -e  # Exit on error

echo "=========================================="
echo "Nebula.AI - Amazon Linux 3 Setup"
echo "=========================================="
echo ""

# Check if running on Amazon Linux
if [ ! -f /etc/os-release ] || ! grep -q "Amazon Linux" /etc/os-release; then
    echo "Warning: This script is designed for Amazon Linux 3"
    echo "Continue anyway? (y/n)"
    read -r response
    if [ "$response" != "y" ]; then
        exit 1
    fi
fi

# Step 1: Update system
echo "[1/7] Updating system packages..."
sudo yum update -y

# Step 2: Install Python 3.12
echo ""
echo "[2/7] Installing Python 3.12..."
if ! command -v python3.12 &> /dev/null; then
    sudo yum install -y python3.12 python3.12-pip python3.12-devel
else
    echo "Python 3.12 already installed"
fi

# Verify Python version
PYTHON_VERSION=$(python3.12 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Step 3: Install Node.js 18+
echo ""
echo "[3/7] Installing Node.js 18+..."
if ! command -v node &> /dev/null || [ "$(node --version | cut -d'v' -f2 | cut -d'.' -f1)" -lt 18 ]; then
    echo "Installing Node.js from NodeSource..."
    curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
    sudo yum install -y nodejs
else
    echo "Node.js $(node --version) already installed"
fi

# Step 4: Install Graphviz
echo ""
echo "[4/7] Installing Graphviz..."
if ! command -v dot &> /dev/null; then
    sudo yum install -y graphviz graphviz-devel
else
    echo "Graphviz already installed"
fi

# Step 5: Install build tools
echo ""
echo "[5/7] Installing build tools..."
sudo yum install -y gcc gcc-c++ make git

# Step 6: Setup Python virtual environment
echo ""
echo "[6/7] Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3.12 -m venv venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install uv for MCP server management
echo "Installing uv..."
pip install uv

# Step 7: Setup environment file
echo ""
echo "[7/7] Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "Created .env file from template"
        echo ""
        echo "⚠️  IMPORTANT: Please edit .env file with your AWS credentials:"
        echo "   nano .env"
        echo ""
        echo "Required variables:"
        echo "  - AWS_REGION"
        echo "  - AWS_ACCESS_KEY_ID"
        echo "  - AWS_SECRET_ACCESS_KEY"
        echo "  - BEDROCK_MODEL_ID (optional, has default)"
        echo ""
    else
        echo "Warning: env.example not found"
    fi
else
    echo ".env file already exists"
fi

# Install MCP servers (optional, can be done separately)
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your AWS credentials:"
echo "   nano .env"
echo ""
echo "2. Install MCP servers (optional, improves performance):"
echo "   bash install_mcp_servers.sh"
echo ""
echo "3. Start the backend server:"
echo "   source venv/bin/activate"
echo "   bash start.sh"
echo ""
echo "Or use systemd for production deployment (see docs/AMAZON_LINUX_3_SETUP.md)"
echo ""

