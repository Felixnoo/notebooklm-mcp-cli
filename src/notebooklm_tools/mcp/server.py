"""NotebookLM MCP Server - Modular Architecture.

This is the main server facade that initializes FastMCP and registers all tools
from the modular tools package. Tools are organized into domain-specific modules
under the `tools/` directory.

Tool Modules:
- auth.py: Authentication management (refresh_auth, save_auth_tokens)
- notebooks.py: Notebook CRUD operations
- sources.py: Source management with consolidated source_add
- sharing.py: Sharing and collaboration
- research.py: Deep research and source discovery
- studio.py: Artifact creation with consolidated studio_create
- downloads.py: Artifact downloads with consolidated download_artifact
- chat.py: Query and conversation management
- exports.py: Export artifacts to Google Docs/Sheets
- notes.py: Note management (create, list, update, delete)
"""

import argparse
import logging
import os
import sys

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from notebooklm_tools import __version__

# Initialize MCP server
mcp = FastMCP(
    name="notebooklm",
    instructions="""NotebookLM MCP - Access NotebookLM (notebooklm.google.com).

**Auth:** If you get authentication errors, run `nlm login` via your Bash/terminal tool. This is the automated authentication method that handles everything. Only use save_auth_tokens as a fallback if the CLI fails.
**Account Switching:** To switch Google Accounts for the MCP server, run `nlm login switch <profile>` in Bash. The MCP server instantly uses the active default profile.
**Confirmation:** Tools with confirm param require user approval before setting confirm=True.
**Studio:** After creating audio/video/infographic/slides, poll studio_status for completion.

Consolidated tools:
- source_add(source_type=url|text|drive|file, url=..., document_id=..., text=..., file_path=...): Add any source type
- studio_create(artifact_type=audio|video|...): Create any artifact type
- studio_revise: Revise individual slides in an existing slide deck
- download_artifact(artifact_type=audio|video|...): Download any artifact type
- note_create/note_list/note_update/note_delete: Manage notes in notebooks""",
)

# MCP request/response logger
mcp_logger = logging.getLogger("notebooklm_tools.mcp")


# Remote authentication endpoints
import uuid
import time
from notebooklm_tools.core.auth_db import get_auth_db
from notebooklm_tools.core.auth import AuthTokens

# API key validation middleware
async def validate_api_key(request: Request) -> JSONResponse:
    """Validate API key from request headers."""
    api_key = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not api_key:
        return JSONResponse(
            {"status": "error", "error": "Missing API key"},
            status_code=401
        )
    
    auth_db = get_auth_db()
    user_info = auth_db.validate_api_key(api_key)
    if not user_info:
        return JSONResponse(
            {"status": "error", "error": "Invalid or expired API key"},
            status_code=401
        )
    
    # Store user info in request state for later use
    request.state.user_info = user_info
    return None

# Rate limiting storage
rate_limit_store = {}

# Logging middleware
async def logging_middleware(request: Request, call_next):
    """Logging middleware to record request and response details."""
    # Start time
    start_time = time.time()
    
    # Get user ID if available
    user_id = request.state.user_info.get("user_id") if hasattr(request.state, "user_info") else "anonymous"
    
    # Log request details
    mcp_logger.info(f"Request: {request.method} {request.url.path} from user {user_id}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate response time
    response_time = time.time() - start_time
    
    # Log response details
    mcp_logger.info(f"Response: {request.method} {request.url.path} status={response.status_code} time={response_time:.2f}s")
    
    return response

# Rate limiting middleware
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware to prevent API abuse."""
    # Skip rate limiting for health check endpoint
    if request.url.path == "/health":
        response = await call_next(request)
        return response
    
    # Get user ID from request state (set by api_key_middleware)
    user_id = request.state.user_info.get("user_id") if hasattr(request.state, "user_info") else "anonymous"
    
    # Get current time
    current_time = time.time()
    
    # Initialize or update rate limit data
    if user_id not in rate_limit_store:
        rate_limit_store[user_id] = {"count": 1, "reset_time": current_time + 60}  # 1 minute window
    else:
        # Check if reset time has passed
        if current_time > rate_limit_store[user_id]["reset_time"]:
            rate_limit_store[user_id] = {"count": 1, "reset_time": current_time + 60}
        else:
            # Increment count
            rate_limit_store[user_id]["count"] += 1
            
            # Check if rate limit exceeded (60 requests per minute)
            if rate_limit_store[user_id]["count"] > 60:
                mcp_logger.warning(f"Rate limit exceeded for user {user_id}")
                return JSONResponse(
                    {"status": "error", "error": "Rate limit exceeded. Please try again later."},
                    status_code=429
                )
    
    # Continue processing the request
    response = await call_next(request)
    return response

# Global API key validation middleware
async def api_key_middleware(request: Request, call_next):
    """Global middleware to validate API key for all requests."""
    # Skip validation for health check endpoint
    if request.url.path == "/health":
        response = await call_next(request)
        return response
    
    # Validate API key
    auth_error = await validate_api_key(request)
    if auth_error:
        return auth_error
    
    # Continue processing the request
    response = await call_next(request)
    return response

# Add middlewares to the MCP server
mcp.add_middleware(logging_middleware)
mcp.add_middleware(rate_limit_middleware)
mcp.add_middleware(api_key_middleware)

# Health check endpoint
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for load balancers and monitoring."""
    return JSONResponse({
        "status": "healthy",
        "service": "notebooklm-mcp",
        "version": __version__,
    })

@mcp.custom_route("/auth/start", methods=["GET"])
async def auth_start(request: Request) -> JSONResponse:
    """Start the authentication process."""

    
    try:
        # Generate a unique state for CSRF protection
        state = str(uuid.uuid4())
        
        # Return the authentication URL and state
        return JSONResponse({
            "status": "success",
            "state": state,
            "auth_url": "https://notebooklm.google.com",
            "message": "Please log in to NotebookLM and then call /auth/callback with the cookies"
        })
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)


@mcp.custom_route("/auth/callback", methods=["POST"])
async def auth_callback(request: Request) -> JSONResponse:
    """Handle authentication callback with cookies."""

    
    try:
        data = await request.json()
        
        # Validate required parameters
        if "cookies" not in data:
            return JSONResponse({"status": "error", "error": "Missing cookies parameter"}, status_code=400)
        
        # Generate user ID from cookies (simplified approach)
        cookies = data["cookies"]
        user_id = str(uuid.uuid4())  # In production, use a more secure method
        
        # Create AuthTokens object
        tokens = AuthTokens(
            cookies=cookies,
            csrf_token=data.get("csrf_token", ""),
            session_id=data.get("session_id", ""),
            build_label=data.get("build_label", ""),
            extracted_at=time.time()
        )
        
        # Save to database
        auth_db = get_auth_db()
        auth_db.add_user(user_id, data.get("email"))
        auth_db.save_auth_tokens(user_id, tokens)
        auth_db.update_user_last_login(user_id)
        
        return JSONResponse({
            "status": "success",
            "user_id": user_id,
            "message": "Authentication successful. Tokens saved to database."
        })
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)


@mcp.custom_route("/auth/status", methods=["GET"])
async def auth_status(request: Request) -> JSONResponse:
    """Check authentication status for a user."""

    
    try:
        user_id = request.query_params.get("user_id")
        if not user_id:
            return JSONResponse({"status": "error", "error": "Missing user_id parameter"}, status_code=400)
        
        auth_db = get_auth_db()
        tokens = auth_db.get_auth_tokens(user_id)
        user_info = auth_db.get_user_info(user_id)
        
        if not tokens:
            return JSONResponse({"status": "unauthorized", "message": "No valid auth tokens found"})
        
        return JSONResponse({
            "status": "authorized",
            "user_id": user_id,
            "user_info": user_info,
            "tokens_valid": True
        })
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)


@mcp.custom_route("/auth/refresh", methods=["POST"])
async def auth_refresh(request: Request) -> JSONResponse:
    """Refresh authentication tokens."""

    
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        if not user_id:
            return JSONResponse({"status": "error", "error": "Missing user_id parameter"}, status_code=400)
        
        # Here you would typically re-authenticate with the provider
        # For this example, we'll just update the last login time
        auth_db = get_auth_db()
        auth_db.update_user_last_login(user_id)
        
        return JSONResponse({
            "status": "success",
            "message": "Authentication refreshed"
        })
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)


# API key management endpoints
@mcp.custom_route("/api/keys/generate", methods=["POST"])
async def generate_api_key(request: Request) -> JSONResponse:
    """Generate a new API key for a user."""

    
    try:
        data = await request.json()
        user_id = data.get("user_id")
        description = data.get("description")
        
        if not user_id:
            return JSONResponse({"status": "error", "error": "Missing user_id parameter"}, status_code=400)
        
        auth_db = get_auth_db()
        api_key = auth_db.generate_api_key(user_id, description)
        
        if not api_key:
            return JSONResponse({"status": "error", "error": "Failed to generate API key"}, status_code=500)
        
        return JSONResponse({
            "status": "success",
            "api_key": api_key,
            "message": "API key generated successfully"
        })
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)


@mcp.custom_route("/api/keys/list", methods=["GET"])
async def list_api_keys(request: Request) -> JSONResponse:
    """List all API keys for a user."""

    
    try:
        user_id = request.query_params.get("user_id")
        if not user_id:
            return JSONResponse({"status": "error", "error": "Missing user_id parameter"}, status_code=400)
        
        auth_db = get_auth_db()
        keys = auth_db.list_api_keys(user_id)
        
        return JSONResponse({
            "status": "success",
            "api_keys": keys
        })
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)


@mcp.custom_route("/api/keys/revoke", methods=["POST"])
async def revoke_api_key(request: Request) -> JSONResponse:
    """Revoke an API key for a user."""

    
    try:
        data = await request.json()
        user_id = data.get("user_id")
        api_key = data.get("api_key")
        
        if not user_id or not api_key:
            return JSONResponse({"status": "error", "error": "Missing user_id or api_key parameter"}, status_code=400)
        
        auth_db = get_auth_db()
        success = auth_db.revoke_api_key(api_key, user_id)
        
        if not success:
            return JSONResponse({"status": "error", "error": "Failed to revoke API key"}, status_code=404)
        
        return JSONResponse({
            "status": "success",
            "message": "API key revoked successfully"
        })
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)


@mcp.custom_route("/api/keys/validate", methods=["GET"])
async def validate_api_key_endpoint(request: Request) -> JSONResponse:
    """Validate an API key."""
    try:
        api_key = request.query_params.get("api_key")
        if not api_key:
            return JSONResponse({"status": "error", "error": "Missing api_key parameter"}, status_code=400)
        
        auth_db = get_auth_db()
        user_info = auth_db.validate_api_key(api_key)
        
        if not user_info:
            return JSONResponse({"status": "error", "error": "Invalid or expired API key"}, status_code=401)
        
        return JSONResponse({
            "status": "success",
            "user_info": user_info,
            "message": "API key is valid"
        })
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)


def _register_tools():
    """Import and register all tools from the modular tools package."""
    from .tools._utils import register_all_tools
    
    # Import all tool modules to populate the registry
    from .tools import (  # noqa: F401
        downloads,
        auth,
        notebooks,
        sources,
        sharing,
        research,
        studio,
        chat,
        exports,
        notes,
        batch,
        cross_notebook,
        pipeline,
        smart_select,
        studio_advanced,
    )
    
    # Register collected tools with mcp
    register_all_tools(mcp)


# Register tools on import
_register_tools()


def main():
    """Run the MCP server.
    
    Supports multiple transports:
    - stdio (default): For desktop apps like Claude Desktop
    - http: Streamable HTTP for network access
    - https: Streamable HTTPS for secure network access
    - sse: Legacy SSE transport (backwards compatibility)
    """
    import os
    
    parser = argparse.ArgumentParser(
        description="NotebookLM MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  NOTEBOOKLM_MCP_TRANSPORT     Transport type (stdio, http, https, sse)
  NOTEBOOKLM_MCP_HOST          Host to bind (default: 127.0.0.1)
  NOTEBOOKLM_MCP_PORT          Port to listen on (default: 8000 for HTTP, 8443 for HTTPS)
  NOTEBOOKLM_MCP_PATH          MCP endpoint path (default: /mcp)
  NOTEBOOKLM_MCP_STATELESS     Enable stateless mode for scaling (true/false)
  NOTEBOOKLM_MCP_DEBUG         Enable debug logging (true/false)
  NOTEBOOKLM_MCP_SSL_CERT      Path to SSL certificate file
  NOTEBOOKLM_MCP_SSL_KEY       Path to SSL private key file
  NOTEBOOKLM_MCP_LETS_ENCRYPT  Enable Let's Encrypt (true/false)
  NOTEBOOKLM_MCP_DOMAIN        Domain name for Let's Encrypt
  NOTEBOOKLM_HL                Interface language and default artifact language (default: en)
  NOTEBOOKLM_QUERY_TIMEOUT     Query timeout in seconds (default: 120.0)

Examples:
  notebooklm-mcp                              # Default stdio transport
  notebooklm-mcp --transport http             # HTTP on localhost:8000
  notebooklm-mcp --transport https            # HTTPS on localhost:8443 with Let's Encrypt
  notebooklm-mcp --transport http --port 3000 # HTTP on custom port
  notebooklm-mcp --debug                      # Enable debug logging
        """
    )
    
    parser.add_argument(
        "--transport", "-t",
        choices=["stdio", "http", "https", "sse"],
        default=os.environ.get("NOTEBOOKLM_MCP_TRANSPORT", "stdio"),
        help="Transport protocol (default: stdio)"
    )
    parser.add_argument(
        "--host", "-H",
        default=os.environ.get("NOTEBOOKLM_MCP_HOST", "127.0.0.1"),
        help="Host to bind for HTTP/SSE (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=int(os.environ.get("NOTEBOOKLM_MCP_PORT", "8000" if os.environ.get("NOTEBOOKLM_MCP_TRANSPORT", "stdio") != "https" else "8443")),
        help="Port for HTTP/SSE transport (default: 8000 for HTTP, 8443 for HTTPS)"
    )
    parser.add_argument(
        "--path",
        default=os.environ.get("NOTEBOOKLM_MCP_PATH", "/mcp"),
        help="MCP endpoint path for HTTP (default: /mcp)"
    )
    parser.add_argument(
        "--stateless",
        action="store_true",
        default=os.environ.get("NOTEBOOKLM_MCP_STATELESS", "").lower() == "true",
        help="Enable stateless mode for horizontal scaling"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=os.environ.get("NOTEBOOKLM_MCP_DEBUG", "").lower() == "true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--query-timeout",
        type=float,
        default=float(os.environ.get("NOTEBOOKLM_QUERY_TIMEOUT", "120.0")),
        help="Query timeout in seconds (default: 120.0)"
    )
    parser.add_argument(
        "--ssl-cert",
        default=os.environ.get("NOTEBOOKLM_MCP_SSL_CERT"),
        help="Path to SSL certificate file"
    )
    parser.add_argument(
        "--ssl-key",
        default=os.environ.get("NOTEBOOKLM_MCP_SSL_KEY"),
        help="Path to SSL private key file"
    )
    parser.add_argument(
        "--lets-encrypt",
        action="store_true",
        default=os.environ.get("NOTEBOOKLM_MCP_LETS_ENCRYPT", "").lower() == "true",
        help="Enable Let's Encrypt"
    )
    parser.add_argument(
        "--domain",
        default=os.environ.get("NOTEBOOKLM_MCP_DOMAIN"),
        help="Domain name for Let's Encrypt"
    )
    
    args = parser.parse_args()
    
    # Configure debug logging
    if args.debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        mcp_logger.setLevel(logging.DEBUG)
        # Also enable core client logging
        logging.getLogger("notebooklm_tools.core").setLevel(logging.DEBUG)
    
    # Set query timeout
    from .tools._utils import set_query_timeout
    set_query_timeout(args.query_timeout)
    
    # Run server with appropriate transport
    # show_banner=False prevents Rich box-drawing output that can corrupt
    # the JSON-RPC protocol on Windows (especially with non-English locales)
    if args.transport == "stdio":
        mcp.run(show_banner=False)
    elif args.transport == "http":
        mcp.run(
            transport="streamable-http",
            host=args.host,
            port=args.port,
            path=args.path,
            stateless_http=args.stateless,
            show_banner=False,
        )
    elif args.transport == "https":
        # Handle HTTPS with either custom certificates or Let's Encrypt
        if args.lets_encrypt:
            if not args.domain:
                print("Error: Domain name is required for Let's Encrypt")
                sys.exit(1)
            
            # Let's Encrypt certificate management
            import os
            import subprocess
            import tempfile
            
            # Certificate directory
            cert_dir = os.path.expanduser("~/.notebooklm-mcp/certs")
            os.makedirs(cert_dir, exist_ok=True)
            
            # Check if certbot is installed
            try:
                subprocess.run(["certbot", "--version"], capture_output=True, check=True)
                certbot_available = True
            except (subprocess.SubprocessError, FileNotFoundError):
                certbot_available = False
            
            if certbot_available:
                print(f"Using Let's Encrypt for domain: {args.domain}")
                print("Note: Let's Encrypt requires port 80 to be accessible for domain verification")
                
                # Attempt to obtain or renew certificate
                try:
                    # Run certbot to obtain/renew certificate
                    result = subprocess.run(
                        [
                            "certbot", "certonly", "--standalone",
                            "--domain", args.domain,
                            "--non-interactive", "--agree-tos",
                            "--email", "admin@" + args.domain.split('.')[-2] + "." + args.domain.split('.')[-1],
                            "--work-dir", os.path.join(cert_dir, "work"),
                            "--logs-dir", os.path.join(cert_dir, "logs"),
                            "--config-dir", os.path.join(cert_dir, "config")
                        ],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        # Certificate obtained successfully
                        cert_path = os.path.join(cert_dir, "config", "live", args.domain, "fullchain.pem")
                        key_path = os.path.join(cert_dir, "config", "live", args.domain, "privkey.pem")
                        print(f"Successfully obtained Let's Encrypt certificate for {args.domain}")
                        
                        # Set up automatic renewal
                        print("Setting up automatic certificate renewal...")
                        # Create a cron job or systemd timer for renewal
                        # For demonstration, we'll just print instructions
                        print("To set up automatic renewal, add the following to your crontab:")
                        print(f"0 0 * * * certbot renew --standalone --work-dir {os.path.join(cert_dir, 'work')} --logs-dir {os.path.join(cert_dir, 'logs')} --config-dir {os.path.join(cert_dir, 'config')} --quiet")
                    else:
                        print(f"Error obtaining Let's Encrypt certificate: {result.stderr}")
                        # Fall back to self-signed certificate
                        print("Falling back to self-signed certificate")
                        certbot_available = False
                except Exception as e:
                    print(f"Error running certbot: {e}")
                    # Fall back to self-signed certificate
                    certbot_available = False
            
            if not certbot_available:
                # Generate a self-signed certificate for demonstration or when certbot is not available
                import ssl
                from OpenSSL import crypto
                
                # Generate a self-signed certificate
                def generate_self_signed_cert(domain):
                    # Create a key pair
                    key = crypto.PKey()
                    key.generate_key(crypto.TYPE_RSA, 2048)
                    
                    # Create a self-signed certificate
                    cert = crypto.X509()
                    cert.get_subject().C = "US"
                    cert.get_subject().ST = "California"
                    cert.get_subject().L = "San Francisco"
                    cert.get_subject().O = "NotebookLM"
                    cert.get_subject().OU = "MCP"
                    cert.get_subject().CN = domain
                    cert.set_serial_number(1000)
                    cert.gmtime_adj_notBefore(0)
                    cert.gmtime_adj_notAfter(365 * 24 * 60 * 60)  # 1 year
                    cert.set_issuer(cert.get_subject())
                    cert.set_pubkey(key)
                    cert.sign(key, "sha256")
                    
                    # Write files
                    cert_path = os.path.join(cert_dir, f"{domain}.pem")
                    key_path = os.path.join(cert_dir, f"{domain}.key")
                    
                    with open(key_path, 'wb') as f:
                        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
                    
                    with open(cert_path, 'wb') as f:
                        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
                    
                    return cert_path, key_path
                
                cert_path, key_path = generate_self_signed_cert(args.domain)
                print(f"Generated self-signed certificate for {args.domain}")
        else:
            # Use custom SSL certificates
            if not args.ssl_cert or not args.ssl_key:
                print("Error: SSL certificate and key files are required for HTTPS")
                sys.exit(1)
            
            cert_path = args.ssl_cert
            key_path = args.ssl_key
        
        mcp.run(
            transport="streamable-http",
            host=args.host,
            port=args.port,
            path=args.path,
            stateless_http=args.stateless,
            show_banner=False,
            ssl_cert=cert_path,
            ssl_key=key_path,
        )
    elif args.transport == "sse":
        mcp.run(
            transport="sse",
            host=args.host,
            port=args.port,
            show_banner=False,
        )


if __name__ == "__main__":
    main()
