"""Internal commands for NotebookLM Tools."""

import typer
from rich.console import Console

console = Console()

# Internal command group
internal_app = typer.Typer(
    name="internal",
    help="Internal commands for NotebookLM Tools",
    no_args_is_help=True,
    rich_markup_mode="rich",
)


@internal_app.command("setup")
def internal_setup():
    """Internal setup command for NotebookLM Tools.

    Automatically:
    1. Installs dependencies
    2. Detects local AI tools and provides interactive multi-select configuration
    3. Configures MCP server for selected tools
    4. Executes authentication and ID retrieval
    """
    import subprocess
    import sys
    import os
    import shutil
    from pathlib import Path
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Confirm, Prompt
    from rich.table import Table
    from notebooklm_tools.core.auth import AuthManager
    from notebooklm_tools.utils.config import get_config

    console = Console()

    console.print("[bold]NotebookLM Internal Setup[/bold]")
    console.print("This will guide you through the complete setup process.")
    console.print()

    # Step 1: Install dependencies
    console.print("[bold]Step 1: Checking dependencies...[/bold]")
    with Progress(
        SpinnerColumn(),
        TextColumn("{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task("Checking dependencies...", total=None)
        try:
            # Check if notebooklm-mcp-cli is already installed
            import importlib
            try:
                importlib.import_module("notebooklm_tools")
                console.print("[green]✓[/green] Dependencies already installed")
            except ImportError:
                # If not installed, install from PyPI
                console.print("[yellow]⚠[/yellow] Dependencies not found, installing...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "notebooklm-mcp-cli"],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if result.returncode == 0:
                    console.print("[green]✓[/green] Dependencies installed successfully")
                else:
                    console.print("[yellow]⚠[/yellow] Dependency installation might have issues:")
                    console.print(f"[dim]{result.stderr[:500]}...[/dim]")
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] Error checking dependencies: {e}")
        progress.update(task, completed=True)

    console.print()

    # Step 2: Detect and configure AI tools
    console.print("[bold]Step 2: Detecting and configuring AI tools...[/bold]")
    
    # MCP server command - the binary that clients will execute
    MCP_SERVER_CMD = "notebooklm-mcp"

    # Client definitions
    CLIENT_REGISTRY = {
        "claude-code": {
            "name": "Claude Code",
            "description": "Anthropic CLI (claude command)",
            "has_auto_setup": True,
        },
        "gemini": {
            "name": "Gemini CLI",
            "description": "Google Gemini CLI",
            "has_auto_setup": True,
        },
        "cursor": {
            "name": "Cursor",
            "description": "Cursor AI editor",
            "has_auto_setup": True,
        },
        "windsurf": {
            "name": "Windsurf",
            "description": "Codeium Windsurf editor",
            "has_auto_setup": True,
        },
        "cline": {
            "name": "Cline CLI",
            "description": "Cline CLI terminal agent",
            "has_auto_setup": True,
        },
        "antigravity": {
            "name": "Antigravity",
            "description": "Google Antigravity AI IDE",
            "has_auto_setup": True,
        },
        "codex": {
            "name": "Codex CLI",
            "description": "OpenAI Codex CLI",
            "has_auto_setup": True,
        },
        "opencode": {
            "name": "OpenCode",
            "description": "OpenCode terminal AI assistant",
            "has_auto_setup": True,
        },
    }

    # Helper functions
    def _find_mcp_server_path():
        """Find the full path to the notebooklm-mcp binary."""
        return shutil.which(MCP_SERVER_CMD)

    def _read_json_config(path):
        """Read a JSON config file, returning empty dict if missing or invalid."""
        if not path.exists():
            return {}
        try:
            import json
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return {}

    def _write_json_config(path, config):
        """Write a JSON config file, creating parent dirs as needed."""
        path.parent.mkdir(parents=True, exist_ok=True)
        import json
        path.write_text(json.dumps(config, indent=2) + "\n")

    def _is_configured(config, key="notebooklm-mcp"):
        """Check if notebooklm-mcp is already in an mcpServers config."""
        servers = config.get("mcpServers", {})
        return key in servers or "notebooklm" in servers

    def _add_mcp_server(config, key="notebooklm-mcp", extra=None):
        """Add notebooklm-mcp to an mcpServers config dict."""
        config.setdefault("mcpServers", {})
        entry = {"command": MCP_SERVER_CMD, "args": []}
        if extra:
            entry.update(extra)
        config["mcpServers"][key] = entry
        return config

    def _gemini_config_path():
        """Get Gemini CLI config path."""
        return Path.home() / ".gemini" / "settings.json"

    def _cursor_config_path(level="user"):
        """Get Cursor MCP config path."""
        import platform
        if level == "project":
            return Path(".cursor") / "mcp.json"
        # User-level
        system = platform.system()
        if system == "Darwin":
            return Path.home() / ".cursor" / "mcp.json"
        elif system == "Windows":
            appdata = Path(os.environ.get("APPDATA", ""))
            return appdata / "Cursor" / "User" / "mcp.json"
        else:
            return Path.home() / ".config" / "cursor" / "mcp.json"

    def _windsurf_config_path():
        """Get Windsurf MCP config path."""
        import platform
        system = platform.system()
        if system == "Darwin":
            return Path.home() / ".codeium" / "windsurf" / "mcp_config.json"
        elif system == "Windows":
            appdata = Path(os.environ.get("APPDATA", ""))
            return appdata / "Codeium" / "windsurf" / "mcp_config.json"
        else:
            return Path.home() / ".config" / "codeium" / "windsurf" / "mcp_config.json"

    def _cline_config_path():
        """Get Cline CLI MCP settings path."""
        return Path.home() / ".cline" / "data" / "settings" / "cline_mcp_settings.json"

    def _antigravity_config_path():
        """Get Google Antigravity MCP config path."""
        return Path.home() / ".gemini" / "antigravity" / "mcp_config.json"

    def _codex_config_path():
        """Get Codex CLI config directory path."""
        return Path.home() / ".codex"

    def _opencode_config_path():
        """Get OpenCode global config path."""
        return Path.home() / ".config" / "opencode" / "opencode.json"

    def _detect_tool(client_id):
        """Check if an AI tool is installed/present on the system."""
        checks = {
            "claude-code": lambda: shutil.which("claude") is not None,
            "gemini": lambda: shutil.which("gemini") is not None,
            "cursor": lambda: shutil.which("cursor") is not None or (Path.home() / ".cursor").exists(),
            "windsurf": lambda: shutil.which("windsurf") is not None,
            "cline": lambda: shutil.which("cline") is not None,
            "antigravity": lambda: shutil.which("antigravity") is not None,
            "codex": lambda: shutil.which("codex") is not None,
            "opencode": lambda: shutil.which("opencode") is not None,
        }
        check_fn = checks.get(client_id)
        if not check_fn:
            return False
        try:
            return check_fn()
        except Exception:
            return False

    def _is_already_configured(client_id):
        """Check if MCP is already configured for a client."""
        try:
            if client_id == "claude-code":
                claude_cmd = shutil.which("claude")
                if claude_cmd:
                    result = subprocess.run(
                        [claude_cmd, "mcp", "list"],
                        capture_output=True, text=True, timeout=5,
                    )
                    return "notebooklm" in result.stdout.lower()
                return False

            elif client_id == "gemini":
                config = _read_json_config(_gemini_config_path())
                return _is_configured(config, "notebooklm")
            elif client_id == "cursor":
                config = _read_json_config(_cursor_config_path())
                return _is_configured(config)
            elif client_id == "windsurf":
                config = _read_json_config(_windsurf_config_path())
                return _is_configured(config)
            elif client_id == "cline":
                config = _read_json_config(_cline_config_path())
                return _is_configured(config)
            elif client_id == "antigravity":
                config = _read_json_config(_antigravity_config_path())
                return _is_configured(config, "notebooklm")
            elif client_id == "codex":
                codex_cmd = shutil.which("codex")
                if codex_cmd:
                    result = subprocess.run(
                        [codex_cmd, "mcp", "list"],
                        capture_output=True, text=True, timeout=5,
                    )
                    return "notebooklm" in result.stdout.lower()
                else:
                    # Check config.toml directly
                    import tomllib
                    toml_path = _codex_config_path() / "config.toml"
                    if toml_path.exists():
                        config = tomllib.loads(toml_path.read_text())
                        mcp = config.get("mcp_servers", {})
                        return "notebooklm" in mcp or "notebooklm-mcp" in mcp
            elif client_id == "opencode":
                config = _read_json_config(_opencode_config_path())
                mcp = config.get("mcp", {})
                return "notebooklm" in mcp or "notebooklm-mcp" in mcp
        except Exception:
            pass
        return False

    def _setup_claude_code():
        """Add MCP to Claude Code via `claude mcp add`."""
        claude_cmd = shutil.which("claude")
        if not claude_cmd:
            console.print("[yellow]Warning:[/yellow] 'claude' command not found in PATH")
            console.print("  Install Claude Code: https://docs.anthropic.com/en/docs/claude-code")
            console.print()
            console.print("  Manual setup — add to [dim]~/.claude/settings.json[/dim]:")
            console.print('    "mcpServers": { "notebooklm-mcp": { "command": "notebooklm-mcp" } }')
            return False

        try:
            result = subprocess.run(
                [claude_cmd, "mcp", "add", "-s", "user", "notebooklm-mcp", "--", MCP_SERVER_CMD],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                console.print(f"[green]✓[/green] Added to Claude Code (user scope)")
                return True
            elif "already exists" in result.stderr.lower():
                console.print(f"[green]✓[/green] Already configured in Claude Code")
                return True
            else:
                console.print(f"[yellow]Warning:[/yellow] claude mcp add returned: {result.stderr.strip()}")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            console.print(f"[yellow]Warning:[/yellow] Could not run claude command: {e}")
            return False

    def _setup_gemini():
        """Add MCP to Gemini CLI config."""
        config_path = _gemini_config_path()
        config = _read_json_config(config_path)

        if _is_configured(config, "notebooklm"):
            console.print(f"[green]✓[/green] Already configured in Gemini CLI")
            return True

        _add_mcp_server(config, key="notebooklm", extra={"trust": True})
        _write_json_config(config_path, config)
        console.print(f"[green]✓[/green] Added to Gemini CLI")
        console.print(f"  [dim]{config_path}[/dim]")
        return True

    def _setup_cursor(level="user"):
        """Add MCP to Cursor config."""
        config_path = _cursor_config_path(level)
        config = _read_json_config(config_path)

        if _is_configured(config):
            console.print(f"[green]✓[/green] Already configured in Cursor ({level})")
            return True

        _add_mcp_server(config)
        _write_json_config(config_path, config)
        console.print(f"[green]✓[/green] Added to Cursor ({level})")
        console.print(f"  [dim]{config_path}[/dim]")
        return True

    def _setup_windsurf():
        """Add MCP to Windsurf config."""
        config_path = _windsurf_config_path()
        config = _read_json_config(config_path)

        if _is_configured(config):
            console.print(f"[green]✓[/green] Already configured in Windsurf")
            return True

        _add_mcp_server(config)
        _write_json_config(config_path, config)
        console.print(f"[green]✓[/green] Added to Windsurf")
        console.print(f"  [dim]{config_path}[/dim]")
        return True

    def _setup_cline():
        """Add MCP to Cline CLI config."""
        config_path = _cline_config_path()
        config = _read_json_config(config_path)

        if _is_configured(config):
            console.print(f"[green]✓[/green] Already configured in Cline CLI")
            return True

        _add_mcp_server(config)
        _write_json_config(config_path, config)
        console.print(f"[green]✓[/green] Added to Cline CLI")
        console.print(f"  [dim]{config_path}[/dim]")
        return True

    def _setup_antigravity():
        """Add MCP to Google Antigravity config."""
        config_path = _antigravity_config_path()
        config = _read_json_config(config_path)

        if _is_configured(config, "notebooklm"):
            console.print(f"[green]✓[/green] Already configured in Antigravity")
            return True

        _add_mcp_server(config, key="notebooklm")
        _write_json_config(config_path, config)
        console.print(f"[green]✓[/green] Added to Antigravity")
        console.print(f"  [dim]{config_path}[/dim]")
        return True

    def _setup_codex():
        """Add MCP to Codex CLI via `codex mcp add` (preferred) or config.toml fallback."""
        codex_cmd = shutil.which("codex")
        if codex_cmd:
            try:
                result = subprocess.run(
                    [codex_cmd, "mcp", "add", "notebooklm-mcp", "--", MCP_SERVER_CMD],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    console.print(f"[green]✓[/green] Added to Codex CLI")
                    return True
                elif "already exists" in result.stderr.lower():
                    console.print(f"[green]✓[/green] Already configured in Codex CLI")
                    return True
                else:
                    console.print(f"[yellow]Warning:[/yellow] codex mcp add returned: {result.stderr.strip()}")
                    return False
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
                console.print(f"[yellow]Warning:[/yellow] Could not run codex command: {e}")
                return False
        else:
            # Fallback: write config.toml directly
            config_path = _codex_config_path() / "config.toml"

            if config_path.exists():
                try:
                    import tomllib
                    content = config_path.read_text()
                    config = tomllib.loads(content)
                    mcp_servers = config.get("mcp_servers", {})
                    if "notebooklm" in mcp_servers or "notebooklm-mcp" in mcp_servers:
                        console.print(f"[green]✓[/green] Already configured in Codex CLI")
                        return True
                except Exception:
                    content = config_path.read_text() if config_path.exists() else ""
            else:
                content = ""

            section = '''
# NotebookLM MCP server
[mcp_servers.notebooklm]
command = "notebooklm-mcp"
args = []
enabled = true
'''
            new_content = content.rstrip() + "\n" + section if content.strip() else section.lstrip()

            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(new_content)
            console.print(f"[green]✓[/green] Added to Codex CLI (config.toml)")
            console.print(f"  [dim]{config_path}[/dim]")
            return True

    def _setup_opencode():
        """Add MCP to OpenCode config."""
        OPENCODE_MCP_TIMEOUT_MS = 300_000
        
        def _ensure_opencode_timeout(config):
            """Set ``experimental.mcp_timeout`` if not already present."""
            experimental = config.setdefault("experimental", {})
            if "mcp_timeout" not in experimental:
                experimental["mcp_timeout"] = OPENCODE_MCP_TIMEOUT_MS

        config_path = _opencode_config_path()
        config = _read_json_config(config_path)

        mcp = config.get("mcp", {})
        if "notebooklm" in mcp or "notebooklm-mcp" in mcp:
            # Still ensure timeout is set even if server entry already exists
            _ensure_opencode_timeout(config)
            _write_json_config(config_path, config)
            console.print(f"[green]✓[/green] Already configured in OpenCode")
            return True

        mcp["notebooklm"] = {
            "type": "local",
            "command": [MCP_SERVER_CMD],
            "enabled": True,
            "timeout": OPENCODE_MCP_TIMEOUT_MS,
        }
        config["mcp"] = mcp

        # Set global experimental timeout
        _ensure_opencode_timeout(config)

        _write_json_config(config_path, config)
        console.print(f"[green]✓[/green] Added to OpenCode")
        console.print(f"  [dim]{config_path}[/dim]")
        return True

    # Scan for AI tools
    console.print("\n[bold]Scanning for AI tools...[/bold]\n")

    detected = []  # (client_id, info, is_configured, has_auto)
    not_found = []

    for client_id, info in CLIENT_REGISTRY.items():
        is_present = _detect_tool(client_id)
        if is_present:
            has_auto = info["has_auto_setup"]
            already = _is_already_configured(client_id) if has_auto else False
            detected.append((client_id, info, already, has_auto))
        else:
            not_found.append((client_id, info))

    # Display results table
    table = Table(title="Detected AI Tools")
    table.add_column("#", justify="right", style="cyan", width=3)
    table.add_column("Tool", style="bold")
    table.add_column("Status", justify="center")

    configurable = []  # indices of tools that can be auto-configured
    for i, (client_id, info, already, has_auto) in enumerate(detected):
        num = str(i + 1)
        if not has_auto:
            table.add_row(num, info["name"], "[dim]use nlm skill install[/dim]")
        elif already:
            table.add_row(num, info["name"], "[green]✓ configured[/green]")
        else:
            table.add_row(num, info["name"], "[yellow]detected[/yellow]")
            configurable.append(i)

    console.print(table)

    if not_found:
        names = ", ".join(info["name"] for _, info in not_found)
        console.print(f"\n[dim]Not found: {names}[/dim]")

    if not configurable:
        if detected:
            console.print("\n[green]All detected tools are already configured! ✓[/green]")
        else:
            console.print("\n[yellow]No supported AI tools detected on your system.[/yellow]")
            console.print("[dim]Use 'nlm setup add <client>' to configure a specific tool.[/dim]")
    else:
        # Interactive selection
        unconfigured_names = [
            f"{detected[i][1]['name']} ({detected[i][0]})"
            for i in configurable
        ]
        console.print(f"\n[bold]Unconfigured tools:[/bold] {', '.join(unconfigured_names)}")
        console.print()

        choice = Prompt.ask(
            "Configure which tools? [cyan]all/yes[/cyan] / comma-separated numbers / [cyan]none[/cyan]",
            default="all",
        ).strip().lower()

        if choice == "none" or choice == "n":
            console.print("Cancelled.")
        else:
            # Determine which tools to configure
            if choice == "all" or choice == "a" or choice == "yes" or choice == "y":
                selected_indices = configurable
            else:
                try:
                    nums = [int(n.strip()) for n in choice.split(",")]
                    selected_indices = []
                    for n in nums:
                        idx = n - 1
                        if idx in configurable:
                            selected_indices.append(idx)
                        else:
                            console.print(f"[yellow]Skipping #{n} — already configured or invalid[/yellow]")
                except ValueError:
                    console.print("[red]Invalid input. Use 'all', 'none', or comma-separated numbers.[/red]")
                    selected_indices = []

            if selected_indices:
                # Execute setup for selected tools
                console.print()
                setup_fns = {
                    "claude-code": _setup_claude_code,
                    "gemini": _setup_gemini,
                    "cursor": _setup_cursor,
                    "windsurf": _setup_windsurf,
                    "cline": _setup_cline,
                    "antigravity": _setup_antigravity,
                    "codex": _setup_codex,
                    "opencode": _setup_opencode,
                }

                success_count = 0
                for idx in selected_indices:
                    client_id, info, _, _has_auto = detected[idx]
                    fn = setup_fns.get(client_id)
                    if fn:
                        if fn():
                            success_count += 1

                console.print(f"\n[green]✓ Configured {success_count} tool(s)[/green]")
                if success_count > 0:
                    console.print("[dim]Restart the configured tools to activate the MCP server.[/dim]")

    console.print()

    # Step 3: Authenticate and retrieve ID
    console.print("[bold]Step 3: Authenticating with NotebookLM...[/bold]")
    
    # Check if already authenticated
    auth = AuthManager()
    try:
        profile = auth.load_profile()
        console.print(f"[green]✓[/green] Already authenticated as: {profile.email or 'Unknown'}")
    except Exception:
        console.print("[yellow]⚠[/yellow] Not authenticated. Starting authentication process...")
        
        # Import the login function from main.py
        from notebooklm_tools.cli.main import login_callback
        import typer
        from typer import Context
        
        # Create a mock context
        class MockContext:
            def __init__(self):
                self.invoked_subcommand = None
        
        ctx = MockContext()
        
        try:
            # Run login with default options
            login_callback(
                ctx=ctx,
                manual=False,
                check=False,
                profile=None,
                cookie_file=None,
                provider="builtin",
                cdp_url="http://127.0.0.1:18800",
                force=False,
                clear=False
            )
            console.print("[green]✓[/green] Authentication successful")
        except Exception as e:
            console.print(f"[red]✗[/red] Authentication failed: {e}")
            console.print("[dim]You can manually authenticate later with 'nlm login'[/dim]")

    console.print()

    # Step 4: Verify setup
    console.print("[bold]Step 4: Verifying setup...[/bold]")
    
    # Check if MCP server is available
    mcp_path = _find_mcp_server_path()
    if mcp_path:
        console.print(f"[green]✓[/green] MCP server found: {mcp_path}")
    else:
        console.print("[yellow]⚠[/yellow] MCP server not found in PATH")
        console.print("[dim]Make sure the package is installed correctly[/dim]")

    # Check if auth is valid
    try:
        auth = AuthManager()
        profile = auth.load_profile()
        console.print("[green]✓[/green] Authentication profile is valid")
    except Exception:
        console.print("[yellow]⚠[/yellow] Authentication profile not found or invalid")

    console.print()
    console.print("[bold green]Setup completed![/bold green]")
    console.print("You can now use NotebookLM with your configured AI tools.")
    console.print("To start the MCP server, simply use any NotebookLM command.")


@internal_app.command("auth")
def internal_auth():
    """Internal auth command for NotebookLM Tools.

    Automatically:
    1. Opens browser and extracts cookies
    2. Saves authentication information to config file
    3. Detects and retrieves company's NotebookLM ID
    4. Saves the ID to config file
    """
    import re
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from notebooklm_tools.core.auth import AuthManager
    from notebooklm_tools.core.client import NotebookLMClient
    from notebooklm_tools.utils.config import get_config, save_config
    from notebooklm_tools.utils.cdp import extract_cookies_via_cdp, get_page_html

    console = Console()

    console.print("[bold]NotebookLM Internal Auth[/bold]")
    console.print("This will authenticate with NotebookLM and retrieve company ID.")
    console.print()

    # Step 1: Authenticate and extract cookies
    console.print("[bold]Step 1: Authenticating with NotebookLM...[/bold]")
    
    try:
        # Use built-in CDP authentication
        result = extract_cookies_via_cdp(
            auto_launch=True,
            wait_for_login=True,
            login_timeout=300,
            profile_name="default"
        )
        
        cookies = result["cookies"]
        csrf_token = result.get("csrf_token", "")
        session_id = result.get("session_id", "")
        email = result.get("email", "")
        build_label = result.get("build_label", "")
        
        # Save to profile
        auth = AuthManager()
        auth.save_profile(
            cookies=cookies,
            csrf_token=csrf_token,
            session_id=session_id,
            email=email,
            build_label=build_label
        )
        
        console.print("[green]✓[/green] Authentication successful")
        console.print(f"  Account: {email or 'Unknown'}")
        console.print(f"  Cookies extracted: {len(cookies)}")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Authentication failed: {e}")
        console.print("[dim]Please try again or use 'nlm login' manually.[/dim]")
        return

    console.print()

    # Step 2: Detect and retrieve company's NotebookLM ID
    console.print("[bold]Step 2: Detecting company NotebookLM ID...[/bold]")
    
    try:
        # Load the profile
        auth = AuthManager()
        profile = auth.load_profile()
        
        # Create a client to access the API
        with NotebookLMClient(
            cookies=profile.cookies,
            csrf_token=profile.csrf_token or "",
            session_id=profile.session_id or "",
        ) as client:
            # List notebooks to trigger API call and get company info
            notebooks = client.list_notebooks()
            
            # Get the company ID from the client's internal state or API response
            # We'll extract it from the page HTML since it's not directly available in the API
            from notebooklm_tools.utils.cdp import extract_cookies_from_page
            cdp_result = extract_cookies_from_page("http://localhost:9222", wait_for_login=False)
            html = cdp_result.get("html", "")
            
            # Extract company ID from HTML
            # Look for patterns like "companyId": "..." or "organizationId": "..."
            company_id = None
            patterns = [
                r'"companyId":"([^"]+)"',
                r'"organizationId":"([^"]+)"',
                r'company_id=([^&"]+)',
                r'org_id=([^&"]+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, html)
                if match:
                    company_id = match.group(1)
                    break
            
            if not company_id:
                # Try to get company ID from API response headers or other sources
                # For now, we'll use a fallback approach
                console.print("[yellow]⚠[/yellow] Company ID not found in page HTML")
                console.print("[dim]Trying alternative methods...[/dim]")
                
                # Try to extract from the list_notebooks response
                # This is a fallback and may not work
                import json
                notebooks_json = json.dumps(notebooks)
                company_match = re.search(r'"company_id":"([^"]+)"', notebooks_json)
                if company_match:
                    company_id = company_match.group(1)
        
        if company_id:
            console.print(f"[green]✓[/green] Company NotebookLM ID found: {company_id}")
            
            # Step 3: Save company ID to config
            console.print("[bold]Step 3: Saving company ID to config...[/bold]")
            
            config = get_config()
            # Add company_id to the config
            if not hasattr(config, 'company'):
                from pydantic import BaseModel
                class CompanyConfig(BaseModel):
                    id: str = ""
                config.company = CompanyConfig()
            config.company.id = company_id
            
            # Save the updated config
            save_config(config)
            console.print("[green]✓[/green] Company ID saved to config")
        else:
            console.print("[yellow]⚠[/yellow] Company ID not detected")
            console.print("[dim]The company ID may not be available for your account type.[/dim]")
            
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to detect company ID: {e}")
        console.print("[dim]The company ID may not be available for your account type.[/dim]")

    console.print()
    console.print("[bold green]Auth process completed![/bold green]")
    console.print("Authentication information has been saved to your profile.")
    if 'company_id' in locals() and company_id:
        console.print(f"Company NotebookLM ID: {company_id}")



@internal_app.command("install")
def internal_install():
    """Internal install command for NotebookLM Tools.

    Automatically:
    1. Installs dependencies
    2. Detects local AI tools and provides interactive multi-select configuration
    3. Configures MCP server for selected tools
    4. Executes authentication and ID retrieval
    """
    import subprocess
    import sys
    import os
    import shutil
    from pathlib import Path
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Confirm, Prompt
    from rich.table import Table
    from notebooklm_tools.core.auth import AuthManager
    from notebooklm_tools.utils.config import get_config

    console = Console()

    console.print("[bold]NotebookLM Internal Install[/bold]")
    console.print("This will guide you through the complete installation process.")
    console.print()

    # Step 1: Install dependencies
    console.print("[bold]Step 1: Checking dependencies...[/bold]")
    with Progress(
        SpinnerColumn(),
        TextColumn("{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task("Checking dependencies...", total=None)
        try:
            # Check if notebooklm-mcp-cli is already installed
            import importlib
            try:
                importlib.import_module("notebooklm_tools")
                console.print("[green]✓[/green] Dependencies already installed")
            except ImportError:
                # If not installed, install from PyPI
                console.print("[yellow]⚠[/yellow] Dependencies not found, installing...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "notebooklm-mcp-cli"],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if result.returncode == 0:
                    console.print("[green]✓[/green] Dependencies installed successfully")
                else:
                    console.print("[yellow]⚠[/yellow] Dependency installation might have issues:")
                    console.print(f"[dim]{result.stderr[:500]}...[/dim]")
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] Error checking dependencies: {e}")
        progress.update(task, completed=True)

    console.print()

    # Step 2: Detect and configure AI tools
    console.print("[bold]Step 2: Detecting and configuring AI tools...[/bold]")
    
    # MCP server command - the binary that clients will execute
    MCP_SERVER_CMD = "notebooklm-mcp"

    # Client definitions
    CLIENT_REGISTRY = {
        "claude-code": {
            "name": "Claude Code",
            "description": "Anthropic CLI (claude command)",
            "has_auto_setup": True,
        },
        "gemini": {
            "name": "Gemini CLI",
            "description": "Google Gemini CLI",
            "has_auto_setup": True,
        },
        "cursor": {
            "name": "Cursor",
            "description": "Cursor AI editor",
            "has_auto_setup": True,
        },
        "windsurf": {
            "name": "Windsurf",
            "description": "Codeium Windsurf editor",
            "has_auto_setup": True,
        },
        "cline": {
            "name": "Cline CLI",
            "description": "Cline CLI terminal agent",
            "has_auto_setup": True,
        },
        "antigravity": {
            "name": "Antigravity",
            "description": "Google Antigravity AI IDE",
            "has_auto_setup": True,
        },
        "codex": {
            "name": "Codex CLI",
            "description": "OpenAI Codex CLI",
            "has_auto_setup": True,
        },
        "opencode": {
            "name": "OpenCode",
            "description": "OpenCode terminal AI assistant",
            "has_auto_setup": True,
        },
    }

    # Helper functions
    def _find_mcp_server_path():
        """Find the full path to the notebooklm-mcp binary."""
        return shutil.which(MCP_SERVER_CMD)

    def _read_json_config(path):
        """Read a JSON config file, returning empty dict if missing or invalid."""
        if not path.exists():
            return {}
        try:
            import json
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return {}

    def _write_json_config(path, config):
        """Write a JSON config file, creating parent dirs as needed."""
        path.parent.mkdir(parents=True, exist_ok=True)
        import json
        path.write_text(json.dumps(config, indent=2) + "\n")

    def _is_configured(config, key="notebooklm-mcp"):
        """Check if notebooklm-mcp is already in an mcpServers config."""
        servers = config.get("mcpServers", {})
        return key in servers or "notebooklm" in servers

    def _add_mcp_server(config, key="notebooklm-mcp", extra=None):
        """Add notebooklm-mcp to an mcpServers config dict."""
        config.setdefault("mcpServers", {})
        entry = {"command": MCP_SERVER_CMD, "args": []}
        if extra:
            entry.update(extra)
        config["mcpServers"][key] = entry
        return config

    def _gemini_config_path():
        """Get Gemini CLI config path."""
        return Path.home() / ".gemini" / "settings.json"

    def _cursor_config_path(level="user"):
        """Get Cursor MCP config path."""
        import platform
        if level == "project":
            return Path(".cursor") / "mcp.json"
        # User-level
        system = platform.system()
        if system == "Darwin":
            return Path.home() / ".cursor" / "mcp.json"
        elif system == "Windows":
            appdata = Path(os.environ.get("APPDATA", ""))
            return appdata / "Cursor" / "User" / "mcp.json"
        else:
            return Path.home() / ".config" / "cursor" / "mcp.json"

    def _windsurf_config_path():
        """Get Windsurf MCP config path."""
        import platform
        system = platform.system()
        if system == "Darwin":
            return Path.home() / ".codeium" / "windsurf" / "mcp_config.json"
        elif system == "Windows":
            appdata = Path(os.environ.get("APPDATA", ""))
            return appdata / "Codeium" / "windsurf" / "mcp_config.json"
        else:
            return Path.home() / ".config" / "codeium" / "windsurf" / "mcp_config.json"

    def _cline_config_path():
        """Get Cline CLI MCP settings path."""
        return Path.home() / ".cline" / "data" / "settings" / "cline_mcp_settings.json"

    def _antigravity_config_path():
        """Get Google Antigravity MCP config path."""
        return Path.home() / ".gemini" / "antigravity" / "mcp_config.json"

    def _codex_config_path():
        """Get Codex CLI config directory path."""
        return Path.home() / ".codex"

    def _opencode_config_path():
        """Get OpenCode global config path."""
        return Path.home() / ".config" / "opencode" / "opencode.json"

    def _detect_tool(client_id):
        """Check if an AI tool is installed/present on the system."""
        checks = {
            "claude-code": lambda: shutil.which("claude") is not None,
            "gemini": lambda: shutil.which("gemini") is not None,
            "cursor": lambda: shutil.which("cursor") is not None or (Path.home() / ".cursor").exists(),
            "windsurf": lambda: shutil.which("windsurf") is not None,
            "cline": lambda: shutil.which("cline") is not None,
            "antigravity": lambda: shutil.which("antigravity") is not None,
            "codex": lambda: shutil.which("codex") is not None,
            "opencode": lambda: shutil.which("opencode") is not None,
        }
        check_fn = checks.get(client_id)
        if not check_fn:
            return False
        try:
            return check_fn()
        except Exception:
            return False

    def _is_already_configured(client_id):
        """Check if MCP is already configured for a client."""
        try:
            if client_id == "claude-code":
                claude_cmd = shutil.which("claude")
                if claude_cmd:
                    result = subprocess.run(
                        [claude_cmd, "mcp", "list"],
                        capture_output=True, text=True, timeout=5,
                    )
                    return "notebooklm" in result.stdout.lower()
                return False

            elif client_id == "gemini":
                config = _read_json_config(_gemini_config_path())
                return _is_configured(config, "notebooklm")
            elif client_id == "cursor":
                config = _read_json_config(_cursor_config_path())
                return _is_configured(config)
            elif client_id == "windsurf":
                config = _read_json_config(_windsurf_config_path())
                return _is_configured(config)
            elif client_id == "cline":
                config = _read_json_config(_cline_config_path())
                return _is_configured(config)
            elif client_id == "antigravity":
                config = _read_json_config(_antigravity_config_path())
                return _is_configured(config, "notebooklm")
            elif client_id == "codex":
                codex_cmd = shutil.which("codex")
                if codex_cmd:
                    result = subprocess.run(
                        [codex_cmd, "mcp", "list"],
                        capture_output=True, text=True, timeout=5,
                    )
                    return "notebooklm" in result.stdout.lower()
                else:
                    # Check config.toml directly
                    import tomllib
                    toml_path = _codex_config_path() / "config.toml"
                    if toml_path.exists():
                        config = tomllib.loads(toml_path.read_text())
                        mcp = config.get("mcp_servers", {})
                        return "notebooklm" in mcp or "notebooklm-mcp" in mcp
            elif client_id == "opencode":
                config = _read_json_config(_opencode_config_path())
                mcp = config.get("mcp", {})
                return "notebooklm" in mcp or "notebooklm-mcp" in mcp
        except Exception:
            pass
        return False

    def _setup_claude_code():
        """Add MCP to Claude Code via `claude mcp add`."""
        claude_cmd = shutil.which("claude")
        if not claude_cmd:
            console.print("[yellow]Warning:[/yellow] 'claude' command not found in PATH")
            console.print("  Install Claude Code: https://docs.anthropic.com/en/docs/claude-code")
            console.print()
            console.print("  Manual setup — add to [dim]~/.claude/settings.json[/dim]:")
            console.print('    "mcpServers": { "notebooklm-mcp": { "command": "notebooklm-mcp" } }')
            return False

        try:
            result = subprocess.run(
                [claude_cmd, "mcp", "add", "-s", "user", "notebooklm-mcp", "--", MCP_SERVER_CMD],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                console.print(f"[green]✓[/green] Added to Claude Code (user scope)")
                return True
            elif "already exists" in result.stderr.lower():
                console.print(f"[green]✓[/green] Already configured in Claude Code")
                return True
            else:
                console.print(f"[yellow]Warning:[/yellow] claude mcp add returned: {result.stderr.strip()}")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            console.print(f"[yellow]Warning:[/yellow] Could not run claude command: {e}")
            return False

    def _setup_gemini():
        """Add MCP to Gemini CLI config."""
        config_path = _gemini_config_path()
        config = _read_json_config(config_path)

        if _is_configured(config, "notebooklm"):
            console.print(f"[green]✓[/green] Already configured in Gemini CLI")
            return True

        _add_mcp_server(config, key="notebooklm", extra={"trust": True})
        _write_json_config(config_path, config)
        console.print(f"[green]✓[/green] Added to Gemini CLI")
        console.print(f"  [dim]{config_path}[/dim]")
        return True

    def _setup_cursor(level="user"):
        """Add MCP to Cursor config."""
        config_path = _cursor_config_path(level)
        config = _read_json_config(config_path)

        if _is_configured(config):
            console.print(f"[green]✓[/green] Already configured in Cursor ({level})")
            return True

        _add_mcp_server(config)
        _write_json_config(config_path, config)
        console.print(f"[green]✓[/green] Added to Cursor ({level})")
        console.print(f"  [dim]{config_path}[/dim]")
        return True

    def _setup_windsurf():
        """Add MCP to Windsurf config."""
        config_path = _windsurf_config_path()
        config = _read_json_config(config_path)

        if _is_configured(config):
            console.print(f"[green]✓[/green] Already configured in Windsurf")
            return True

        _add_mcp_server(config)
        _write_json_config(config_path, config)
        console.print(f"[green]✓[/green] Added to Windsurf")
        console.print(f"  [dim]{config_path}[/dim]")
        return True

    def _setup_cline():
        """Add MCP to Cline CLI config."""
        config_path = _cline_config_path()
        config = _read_json_config(config_path)

        if _is_configured(config):
            console.print(f"[green]✓[/green] Already configured in Cline CLI")
            return True

        _add_mcp_server(config)
        _write_json_config(config_path, config)
        console.print(f"[green]✓[/green] Added to Cline CLI")
        console.print(f"  [dim]{config_path}[/dim]")
        return True

    def _setup_antigravity():
        """Add MCP to Google Antigravity config."""
        config_path = _antigravity_config_path()
        config = _read_json_config(config_path)

        if _is_configured(config, "notebooklm"):
            console.print(f"[green]✓[/green] Already configured in Antigravity")
            return True

        _add_mcp_server(config, key="notebooklm")
        _write_json_config(config_path, config)
        console.print(f"[green]✓[/green] Added to Antigravity")
        console.print(f"  [dim]{config_path}[/dim]")
        return True

    def _setup_codex():
        """Add MCP to Codex CLI via `codex mcp add` (preferred) or config.toml fallback."""
        codex_cmd = shutil.which("codex")
        if codex_cmd:
            try:
                result = subprocess.run(
                    [codex_cmd, "mcp", "add", "notebooklm-mcp", "--", MCP_SERVER_CMD],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    console.print(f"[green]✓[/green] Added to Codex CLI")
                    return True
                elif "already exists" in result.stderr.lower():
                    console.print(f"[green]✓[/green] Already configured in Codex CLI")
                    return True
                else:
                    console.print(f"[yellow]Warning:[/yellow] codex mcp add returned: {result.stderr.strip()}")
                    return False
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
                console.print(f"[yellow]Warning:[/yellow] Could not run codex command: {e}")
                return False
        else:
            # Fallback: write config.toml directly
            config_path = _codex_config_path() / "config.toml"

            if config_path.exists():
                try:
                    import tomllib
                    content = config_path.read_text()
                    config = tomllib.loads(content)
                    mcp_servers = config.get("mcp_servers", {})
                    if "notebooklm" in mcp_servers or "notebooklm-mcp" in mcp_servers:
                        console.print(f"[green]✓[/green] Already configured in Codex CLI")
                        return True
                except Exception:
                    content = config_path.read_text() if config_path.exists() else ""
            else:
                content = ""

            section = '''
# NotebookLM MCP server
[mcp_servers.notebooklm]
command = "notebooklm-mcp"
args = []
enabled = true
'''
            new_content = content.rstrip() + "\n" + section if content.strip() else section.lstrip()

            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(new_content)
            console.print(f"[green]✓[/green] Added to Codex CLI (config.toml)")
            console.print(f"  [dim]{config_path}[/dim]")
            return True

    def _setup_opencode():
        """Add MCP to OpenCode config."""
        OPENCODE_MCP_TIMEOUT_MS = 300_000
        
        def _ensure_opencode_timeout(config):
            """Set ``experimental.mcp_timeout`` if not already present."""
            experimental = config.setdefault("experimental", {})
            if "mcp_timeout" not in experimental:
                experimental["mcp_timeout"] = OPENCODE_MCP_TIMEOUT_MS

        config_path = _opencode_config_path()
        config = _read_json_config(config_path)

        mcp = config.get("mcp", {})
        if "notebooklm" in mcp or "notebooklm-mcp" in mcp:
            # Still ensure timeout is set even if server entry already exists
            _ensure_opencode_timeout(config)
            _write_json_config(config_path, config)
            console.print(f"[green]✓[/green] Already configured in OpenCode")
            return True

        mcp["notebooklm"] = {
            "type": "local",
            "command": [MCP_SERVER_CMD],
            "enabled": True,
            "timeout": OPENCODE_MCP_TIMEOUT_MS,
        }
        config["mcp"] = mcp

        # Set global experimental timeout
        _ensure_opencode_timeout(config)

        _write_json_config(config_path, config)
        console.print(f"[green]✓[/green] Added to OpenCode")
        console.print(f"  [dim]{config_path}[/dim]")
        return True

    # Scan for AI tools
    console.print("\n[bold]Scanning for AI tools...[/bold]\n")

    detected = []  # (client_id, info, is_configured, has_auto)
    not_found = []

    for client_id, info in CLIENT_REGISTRY.items():
        is_present = _detect_tool(client_id)
        if is_present:
            has_auto = info["has_auto_setup"]
            already = _is_already_configured(client_id) if has_auto else False
            detected.append((client_id, info, already, has_auto))
        else:
            not_found.append((client_id, info))

    # Display results table
    table = Table(title="Detected AI Tools")
    table.add_column("#", justify="right", style="cyan", width=3)
    table.add_column("Tool", style="bold")
    table.add_column("Status", justify="center")

    configurable = []  # indices of tools that can be auto-configured
    for i, (client_id, info, already, has_auto) in enumerate(detected):
        num = str(i + 1)
        if not has_auto:
            table.add_row(num, info["name"], "[dim]use nlm skill install[/dim]")
        elif already:
            table.add_row(num, info["name"], "[green]✓ configured[/green]")
        else:
            table.add_row(num, info["name"], "[yellow]detected[/yellow]")
            configurable.append(i)

    console.print(table)

    if not_found:
        names = ", ".join(info["name"] for _, info in not_found)
        console.print(f"\n[dim]Not found: {names}[/dim]")

    if not configurable:
        if detected:
            console.print("\n[green]All detected tools are already configured! ✓[/green]")
        else:
            console.print("\n[yellow]No supported AI tools detected on your system.[/yellow]")
            console.print("[dim]Use 'nlm setup add <client>' to configure a specific tool.[/dim]")
    else:
        # Interactive selection
        unconfigured_names = [
            f"{detected[i][1]['name']} ({detected[i][0]})"
            for i in configurable
        ]
        console.print(f"\n[bold]Unconfigured tools:[/bold] {', '.join(unconfigured_names)}")
        console.print()

        choice = Prompt.ask(
            "Configure which tools? [cyan]all/yes[/cyan] / comma-separated numbers / [cyan]none[/cyan]",
            default="all",
        ).strip().lower()

        if choice == "none" or choice == "n":
            console.print("Cancelled.")
        else:
            # Determine which tools to configure
            if choice == "all" or choice == "a" or choice == "yes" or choice == "y":
                selected_indices = configurable
            else:
                try:
                    nums = [int(n.strip()) for n in choice.split(",")]
                    selected_indices = []
                    for n in nums:
                        idx = n - 1
                        if idx in configurable:
                            selected_indices.append(idx)
                        else:
                            console.print(f"[yellow]Skipping #{n} — already configured or invalid[/yellow]")
                except ValueError:
                    console.print("[red]Invalid input. Use 'all', 'none', or comma-separated numbers.[/red]")
                    selected_indices = []

            if selected_indices:
                # Execute setup for selected tools
                console.print()
                setup_fns = {
                    "claude-code": _setup_claude_code,
                    "gemini": _setup_gemini,
                    "cursor": _setup_cursor,
                    "windsurf": _setup_windsurf,
                    "cline": _setup_cline,
                    "antigravity": _setup_antigravity,
                    "codex": _setup_codex,
                    "opencode": _setup_opencode,
                }

                success_count = 0
                for idx in selected_indices:
                    client_id, info, _, _has_auto = detected[idx]
                    fn = setup_fns.get(client_id)
                    if fn:
                        if fn():
                            success_count += 1

                console.print(f"\n[green]✓ Configured {success_count} tool(s)[/green]")
                if success_count > 0:
                    console.print("[dim]Restart the configured tools to activate the MCP server.[/dim]")

    console.print()

    # Step 3: Authenticate and retrieve ID
    console.print("[bold]Step 3: Authenticating with NotebookLM...[/bold]")
    
    # Check if already authenticated
    auth = AuthManager()
    try:
        profile = auth.load_profile()
        console.print(f"[green]✓[/green] Already authenticated as: {profile.email or 'Unknown'}")
    except Exception:
        console.print("[yellow]⚠[/yellow] Not authenticated. Starting authentication process...")
        
        # Import the login function from main.py
        from notebooklm_tools.cli.main import login_callback
        import typer
        from typer import Context
        
        # Create a mock context
        class MockContext:
            def __init__(self):
                self.invoked_subcommand = None
        
        ctx = MockContext()
        
        try:
            # Run login with default options
            login_callback(
                ctx=ctx,
                manual=False,
                check=False,
                profile=None,
                cookie_file=None,
                provider="builtin",
                cdp_url="http://127.0.0.1:18800",
                force=False,
                clear=False
            )
            console.print("[green]✓[/green] Authentication successful")
        except Exception as e:
            console.print(f"[red]✗[/red] Authentication failed: {e}")
            console.print("[dim]You can manually authenticate later with 'nlm login'[/dim]")

    console.print()

    # Step 4: Verify setup
    console.print("[bold]Step 4: Verifying setup...[/bold]")
    
    # Check if MCP server is available
    mcp_path = _find_mcp_server_path()
    if mcp_path:
        console.print(f"[green]✓[/green] MCP server found: {mcp_path}")
    else:
        console.print("[yellow]⚠[/yellow] MCP server not found in PATH")
        console.print("[dim]Make sure the package is installed correctly[/dim]")

    # Check if auth is valid
    try:
        auth = AuthManager()
        profile = auth.load_profile()
        console.print("[green]✓[/green] Authentication profile is valid")
    except Exception:
        console.print("[yellow]⚠[/yellow] Authentication profile not found or invalid")

    console.print()
    console.print("[bold green]Installation completed![/bold green]")
    console.print("You can now use NotebookLM with your configured AI tools.")
    console.print("To start the MCP server, simply use any NotebookLM command.")


@internal_app.command("auth")
def internal_auth():
    """Internal auth command."""
    console.print("[bold]Internal auth command[/bold]")
    console.print("This is an internal auth command for NotebookLM Tools")


@internal_app.command("status")
def internal_status():
    """Internal status command."""
    console.print("[bold]Internal status command[/bold]")
    console.print("This is an internal status command for NotebookLM Tools")


@internal_app.command("config")
def internal_config():
    """Internal config command."""
    console.print("[bold]Internal config command[/bold]")
    console.print("This is an internal config command for NotebookLM Tools")
