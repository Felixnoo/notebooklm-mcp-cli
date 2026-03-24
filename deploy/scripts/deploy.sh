#!/bin/bash

set -e

echo "=== NotebookLM MCP Server Deployment Script ==="

# Variables
DEPLOY_DIR="/opt/notebooklm-mcp"
USER="ubuntu"
GROUP="ubuntu"

# Create deployment directory
echo "Creating deployment directory..."
sudo mkdir -p $DEPLOY_DIR
sudo chown $USER:$GROUP $DEPLOY_DIR

# Copy project files
echo "Copying project files..."
cp -r . $DEPLOY_DIR
cd $DEPLOY_DIR

# Install dependencies
echo "Installing dependencies..."
pip install -e .

# Create environment file if not exists
if [ ! -f ".env" ]; then
    echo "Creating environment file..."
    cp deploy/.env.example .env
    echo "Please update .env file with your configuration"
fi

# Setup systemd service
echo "Setting up systemd service..."
sudo cp deploy/systemd/notebooklm-mcp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable notebooklm-mcp.service

# Start service
echo "Starting NotebookLM MCP Server..."
sudo systemctl start notebooklm-mcp.service

echo "=== Deployment completed successfully! ==="
echo "Service status:"
sudo systemctl status notebooklm-mcp.service
