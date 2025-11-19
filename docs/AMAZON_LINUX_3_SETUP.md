# Amazon Linux 3 Setup Guide

This guide will help you deploy Archai on an Amazon Linux 3 EC2 instance.

## Prerequisites

- Amazon Linux 3 EC2 instance (t3.medium or larger recommended)
- AWS credentials configured (IAM role or credentials file)
- Internet access for package installation
- Security group configured to allow:
  - Port 8000 (Backend API)
  - Port 5000 (Frontend - if serving directly)
  - Port 22 (SSH)

## Step 1: System Dependencies

```bash
# Update system packages
sudo yum update -y

# Install Python 3.12 and development tools
sudo yum install -y python3.12 python3.12-pip python3.12-devel
sudo yum install -y gcc gcc-c++ make

# Install Node.js 18+ (using NodeSource repository)
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# Install Graphviz for diagram generation
sudo yum install -y graphviz graphviz-devel

# Install Git
sudo yum install -y git

# Verify installations
python3.12 --version  # Should show Python 3.12.x
node --version         # Should show v18.x.x or higher
npm --version
dot -V                 # Should show Graphviz version
```

## Step 2: Clone and Setup Backend

```bash
# Clone repository (or upload your code)
cd /home/ec2-user
git clone <your-repository-url> solutionbuilder_core
cd solutionbuilder_core/backend

# Run setup script
bash setup.sh

# Configure environment variables
cp env.example .env
nano .env  # Edit with your AWS credentials
```

### Environment Variables (.env)

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# Bedrock Model Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0

# Optional: Anthropic API key (fallback)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# API Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Development Settings
DEBUG=false
LOG_LEVEL=INFO
```

## Step 3: Setup Frontend

```bash
cd ../frontend
bash setup.sh
```

## Step 4: Install MCP Servers

```bash
cd ../backend
bash install_mcp_servers.sh
```

## Step 5: Test Installation

```bash
# Test backend
cd backend
source venv/bin/activate
python3.12 -m uvicorn main:app --host 0.0.0.0 --port 8000 --no-reload

# In another terminal, test frontend
cd frontend
npm run dev -- --host 0.0.0.0 --port 5000
```

## Step 6: Production Deployment

### Option A: Using systemd (Recommended)

Create backend service:

```bash
sudo nano /etc/systemd/system/archai-backend.service
```

```ini
[Unit]
Description=Archai Backend API
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/solutionbuilder_core/backend
Environment="PATH=/home/ec2-user/solutionbuilder_core/backend/venv/bin"
ExecStart=/home/ec2-user/solutionbuilder_core/backend/venv/bin/python3.12 -m uvicorn main:app --host 0.0.0.0 --port 8000 --no-reload
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create frontend service:

```bash
sudo nano /etc/systemd/system/archai-frontend.service
```

```ini
[Unit]
Description=Archai Frontend
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/solutionbuilder_core/frontend
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/npm run dev -- --host 0.0.0.0 --port 5000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start services:

```bash
sudo systemctl daemon-reload
sudo systemctl enable archai-backend
sudo systemctl enable archai-frontend
sudo systemctl start archai-backend
sudo systemctl start archai-frontend

# Check status
sudo systemctl status archai-backend
sudo systemctl status archai-frontend

# View logs
sudo journalctl -u archai-backend -f
sudo journalctl -u archai-frontend -f
```

### Option B: Using PM2 (Alternative)

```bash
# Install PM2 globally
sudo npm install -g pm2

# Start backend
cd /home/ec2-user/solutionbuilder_core/backend
source venv/bin/activate
pm2 start "python3.12 -m uvicorn main:app --host 0.0.0.0 --port 8000 --no-reload" --name archai-backend

# Start frontend
cd ../frontend
pm2 start "npm run dev -- --host 0.0.0.0 --port 5000" --name archai-frontend

# Save PM2 configuration
pm2 save
pm2 startup
```

## Step 7: Configure Firewall

```bash
# Allow ports through firewall (if using firewalld)
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

## Step 8: Access Application

- **Frontend**: http://your-ec2-public-ip:5000
- **Backend API**: http://your-ec2-public-ip:8000
- **API Docs**: http://your-ec2-public-ip:8000/docs

## Troubleshooting

### Python Version Issues

If Python 3.12 is not available:

```bash
# Install Python 3.12 from source or use Amazon Linux Extras
sudo amazon-linux-extras install python3.12

# Or use alternatives
sudo alternatives --set python3 /usr/bin/python3.12
```

### Graphviz Not Found

```bash
# Verify Graphviz installation
which dot
dot -V

# If not found, reinstall
sudo yum reinstall -y graphviz
```

### MCP Server Issues

```bash
# Verify uv installation
pip3.12 list | grep uv

# Reinstall uv if needed
pip3.12 install uv

# Test MCP server commands
awslabs.cfn-mcp-server --help
awslabs.aws-diagram-mcp-server --help
```

### Port Already in Use

```bash
# Check what's using the port
sudo lsof -i :8000
sudo lsof -i :5000

# Kill process if needed
sudo kill -9 <PID>
```

### Permission Issues

```bash
# Ensure proper ownership
sudo chown -R ec2-user:ec2-user /home/ec2-user/solutionbuilder_core

# Ensure scripts are executable
chmod +x backend/setup.sh
chmod +x backend/start.sh
chmod +x frontend/setup.sh
```

## Security Considerations

1. **Use IAM Roles**: Prefer IAM roles over access keys when possible
2. **HTTPS**: Use a reverse proxy (nginx/Apache) with SSL certificates
3. **Firewall**: Restrict access to necessary ports only
4. **Secrets**: Never commit `.env` files; use AWS Secrets Manager
5. **Updates**: Keep system packages updated regularly

## Next Steps

- Set up nginx reverse proxy for HTTPS
- Configure CloudWatch logging
- Set up auto-scaling if needed
- Configure backup strategies
- Set up monitoring and alerts

