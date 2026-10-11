import os
import sys
import json
import getpass
import platform
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple


def get_known_config_paths() -> Dict[str, Path]:
    """Returns standard MCP config file paths for common AI clients across platforms."""
    system = platform.system()
    home = Path.home()
    configs: Dict[str, Path] = {}

    # 1. Antigravity (App & Global configs)
    configs["Antigravity"] = home / ".gemini" / "antigravity" / "mcp_config.json"
    configs["Antigravity (Global)"] = home / ".gemini" / "config" / "mcp_config.json"
    configs["Antigravity IDE"] = home / ".gemini" / "antigravity-ide" / "mcp_config.json"

    # 2. Codex
    configs["Codex"] = home / ".codex" / "mcp.json"
    configs["Codex Config"] = home / ".codex" / "config.json"
    configs["OpenAI MCP"] = home / ".openai" / "mcp.json"

    # 3. Claude Desktop
    if system == "Windows":
        appdata = Path(os.environ.get("APPDATA", str(home / "AppData" / "Roaming")))
        configs["Claude Desktop"] = appdata / "Claude" / "claude_desktop_config.json"
    elif system == "Darwin":  # macOS
        configs["Claude Desktop"] = (
            home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        )
    else:  # Linux
        configs["Claude Desktop"] = home / ".config" / "Claude" / "claude_desktop_config.json"

    # 4. Cursor
    configs["Cursor"] = home / ".cursor" / "mcp.json"

    # 5. Windsurf
    configs["Windsurf"] = home / ".codeium" / "windsurf" / "mcp_config.json"

    return configs


def update_mcp_config(file_path: Path, server_config: Dict[str, Any]) -> bool:
    """Safely updates or inserts the 'chartink' server into an MCP config file."""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        data: Dict[str, Any] = {}
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
            except Exception:
                data = {}

        if not isinstance(data, dict):
            data = {}

        if "mcpServers" not in data or not isinstance(data["mcpServers"], dict):
            data["mcpServers"] = {}

        data["mcpServers"]["chartink"] = server_config

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return True
    except Exception as e:
        print(f"    [!] Error writing to {file_path}: {e}", file=sys.stderr)
        return False


def run_setup(
    email: str = "",
    password: str = "",
    repo_url: str = "",
    target_client: str = "all",
    non_interactive: bool = False,
):
    print("\n" + "=" * 55)
    print("      Chartink MCP - One-Command Auto Setup Wizard")
    print("=" * 55)

    if not non_interactive:
        if not email:
            try:
                email = input("\n[1/3] Chartink Email (press Enter to skip for public scans): ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nSetup cancelled.")
                return

        if email and not password:
            try:
                password = getpass.getpass("[2/3] Chartink Password (hidden): ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nSetup cancelled.")
                return

        if not repo_url:
            default_repo = "https://github.com/vanshpanchal026/Chartink-MCP"
            try:
                entered_repo = input(
                    f"\n[3/3] GitHub Repo URL [Default: {default_repo}]: "
                ).strip()
                repo_url = entered_repo if entered_repo else default_repo
            except (KeyboardInterrupt, EOFError):
                repo_url = default_repo

    if not repo_url:
        repo_url = "https://github.com/vanshpanchal026/Chartink-MCP"

    # Normalize git source for uvx
    git_source = repo_url
    if not git_source.startswith("git+"):
        git_source = f"git+{git_source}.git" if not git_source.endswith(".git") else f"git+{git_source}"

    # Build server config
    server_config: Dict[str, Any] = {
        "command": "uvx",
        "args": [
            "--from",
            git_source,
            "chartink-mcp",
        ],
        "env": {
            "PYTHONUTF8": "1",
        },
    }

    if email:
        server_config["env"]["CHARTINK_EMAIL"] = email
    if password:
        server_config["env"]["CHARTINK_PASSWORD"] = password

    print("\nScanning AI clients and configuring MCP...")
    known_configs = get_known_config_paths()
    configured_any = False

    for client_name, config_path in known_configs.items():
        if target_client.lower() != "all" and target_client.lower() not in client_name.lower():
            continue

        # Check if parent dir exists or file exists
        parent_exists = config_path.parent.exists()
        file_exists = config_path.exists()

        if parent_exists or file_exists or client_name in ("Antigravity", "Claude Desktop"):
            success = update_mcp_config(config_path, server_config)
            if success:
                print(f"  [OK] {client_name}: Successfully configured -> {config_path}")
                configured_any = True
            else:
                print(f"  [FAILED] {client_name}: Failed to configure")
        else:
            print(f"  [--] {client_name}: Not detected (Skipped)")

    print("\n" + "-" * 55)
    if configured_any:
        print("Success! Chartink MCP has been connected to your AI agent(s).")
        print("Simply restart your AI client (Claude Desktop / Cursor / Antigravity)")
        print("and ask it: 'Run a breakout stock scan using Chartink'!")
    else:
        print("No AI client configs were updated.")

    print("\nTip: Native 1-line commands for AI CLI agents:")
    print(f"  * Antigravity CLI: agy mcp add chartink --command uvx --args \"--from\" \"{git_source}\" \"chartink-mcp\"")
    print(f"  * OpenAI Codex:    codex mcp add chartink -- uvx --from {git_source} chartink-mcp")
    print(f"  * Claude Code CLI: claude mcp add chartink -- uvx --from {git_source} chartink-mcp")
    print("=" * 55 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Chartink MCP Setup Wizard")
    parser.add_argument("--email", default="", help="Chartink Email")
    parser.add_argument("--password", default="", help="Chartink Password")
    parser.add_argument("--repo", default="", help="GitHub Repository URL")
    parser.add_argument(
        "--client",
        default="all",
        help="Target client: 'all', 'antigravity', 'codex', 'claude', 'cursor', 'windsurf'",
    )
    parser.add_argument(
        "-y", "--yes", action="store_true", help="Non-interactive mode"
    )
    args = parser.parse_args()

    run_setup(
        email=args.email,
        password=args.password,
        repo_url=args.repo,
        target_client=args.client,
        non_interactive=args.yes,
    )


if __name__ == "__main__":
    main()
