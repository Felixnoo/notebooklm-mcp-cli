# NotebookLM MCP Server Deployment Guide

This guide provides instructions for deploying the NotebookLM MCP Server with automatic startup, restart functionality, and basic monitoring.

## Directory Structure

```
deploy/
├── .env.example          # Environment variables template
├── systemd/             # Systemd service configuration
│   └── notebooklm-mcp.service
├── monitoring/          # Monitoring configuration
│   └── prometheus.yml
└── scripts/             # Deployment and maintenance scripts
    ├── deploy.sh        # Deployment script
    └── health_check.sh  # Health check script
```

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- systemd (for service management)
- curl (for health checks)
- Prometheus (for monitoring, optional)

## Deployment Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/jacob-bd/notebooklm-mcp-cli.git
   cd notebooklm-mcp-cli
   ```

2. **Configure environment variables**
   ```bash
   cp deploy/.env.example deploy/.env
   # Edit deploy/.env to set your configuration
   ```

3. **Run the deployment script**
   ```bash
   bash deploy/scripts/deploy.sh
   ```

4. **Verify the deployment**
   ```bash
   bash deploy/scripts/health_check.sh
   ```

## Configuration Options

### Environment Variables

See `.env.example` for all available configuration options. Key settings include:

- `NOTEBOOKLM_MCP_TRANSPORT`: Transport type (stdio, http, https, sse)
- `NOTEBOOKLM_MCP_HOST`: Host to bind
- `NOTEBOOKLM_MCP_PORT`: Port to listen on
- `NOTEBOOKLM_MCP_PATH`: MCP endpoint path
- `NOTEBOOKLM_MCP_STATELESS`: Enable stateless mode
- `NOTEBOOKLM_MCP_DEBUG`: Enable debug logging

### Systemd Service

The systemd service is configured to:
- Run as the `ubuntu` user
- Start automatically on system boot
- Restart automatically on failure
- Use the environment variables from `.env`

## Monitoring

### Health Check Endpoint

The server provides a health check endpoint at `http://<host>:<port>/health` that returns the service status.

### Prometheus Monitoring

To set up Prometheus monitoring:

1. Install Prometheus
2. Copy the Prometheus configuration:
   ```bash
   sudo cp deploy/monitoring/prometheus.yml /etc/prometheus/
   ```
3. Restart Prometheus:
   ```bash
   sudo systemctl restart prometheus
   ```

## Maintenance

### Service Management

- Start service: `sudo systemctl start notebooklm-mcp.service`
- Stop service: `sudo systemctl stop notebooklm-mcp.service`
- Restart service: `sudo systemctl restart notebooklm-mcp.service`
- Check status: `sudo systemctl status notebooklm-mcp.service`

### Logs

- View logs: `sudo journalctl -u notebooklm-mcp.service`
- Follow logs: `sudo journalctl -u notebooklm-mcp.service -f`

### Updating the Server

1. Pull the latest changes:
   ```bash
   git pull
   ```
2. Re-run the deployment script:
   ```bash
   bash deploy/scripts/deploy.sh
   ```
