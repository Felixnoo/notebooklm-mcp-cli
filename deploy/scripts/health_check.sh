#!/bin/bash

set -e

echo "=== NotebookLM MCP Server Health Check ==="

# Variables
HOST="localhost"
PORT="8000"

# Check if service is running
echo "Checking if service is running..."
if systemctl is-active --quiet notebooklm-mcp.service; then
    echo "✓ Service is running"
else
    echo "✗ Service is not running"
    exit 1
fi

# Check if health endpoint is accessible
echo "Checking health endpoint..."
RESPONSE=$(curl -s http://$HOST:$PORT/health)

if echo "$RESPONSE" | grep -q "healthy"; then
    echo "✓ Health endpoint is accessible"
    echo "Response: $RESPONSE"
else
    echo "✗ Health endpoint is not accessible"
    echo "Response: $RESPONSE"
    exit 1
fi

echo "=== Health check completed successfully! ==="
