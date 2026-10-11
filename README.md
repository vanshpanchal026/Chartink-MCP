# Chartink MCP

[![Python](https://img.shields.io/badge/Python-3.10+-181717?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Protocol](https://img.shields.io/badge/Protocol-MCP-181717?style=flat-square)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-MIT-181717?style=flat-square)](LICENSE)

A Model Context Protocol (MCP) server connecting AI assistants directly to Chartink.com. It enables real-time scanning of Indian equity markets (NSE/BSE) using custom technical formulas or pre-built screeners with raw JSON output.

---

## ⚡ Core Features

- **Custom Technical Scanning**: Run arbitrary Atlas queries (RSI, moving average crossovers, candlestick patterns) on demand.
- **Screener Library Execution**: Fetch and execute any public or private Chartink screener by URL or slug.
- **Zero-Clone Setup**: Connect immediately to any supported AI client with a single-line automated command.
- **Raw JSON Precision**: Returns unformatted, high-precision market data directly from Chartink's processing engine.

---

## 🚀 Quick Start

Run the automated setup wizard to detect and configure your installed AI environments without cloning the repository:

```bash
uvx --from git+https://github.com/vanshpanchal026/Chartink-MCP.git chartink-mcp setup
```

Once installed, query your AI assistant directly:

```text
User: Run the '15-minute-stock-breakouts' screener on Chartink.
Agent: [Invokes get_screener("15-minute-stock-breakouts")]
Result: {
  "recordsTotal": 44,
  "data": [
    { "nsecode": "PTCIL", "close": 24535, "per_chg": 0.27, "volume": 28898 }
  ]
}
```

---

## ⚙️ Configuration & Reference

<details>
<summary><strong>Client Setup, Credentials, and API Reference</strong></summary>

### Native CLI Commands

Add the MCP server directly via your agent's command line interface:

```bash
# Antigravity CLI
agy mcp add chartink --command uvx --args "--from" "git+https://github.com/vanshpanchal026/Chartink-MCP.git" "chartink-mcp"

# OpenAI Codex CLI
codex mcp add chartink -- uvx --from git+https://github.com/vanshpanchal026/Chartink-MCP.git chartink-mcp

# Claude Code CLI
claude mcp add chartink -- uvx --from git+https://github.com/vanshpanchal026/Chartink-MCP.git chartink-mcp
```

### Manual Configuration (`mcp_config.json`)

To configure manually in Claude Desktop, Cursor, or Antigravity:

```json
{
  "mcpServers": {
    "chartink": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/vanshpanchal026/Chartink-MCP.git",
        "chartink-mcp"
      ],
      "env": {
        "PYTHONUTF8": "1",
        "CHARTINK_EMAIL": "your_email@example.com",
        "CHARTINK_PASSWORD": "your_password"
      }
    }
  }
}
```

> **Note**: Public screeners and custom formulas work without credentials. Authentication is only required for private/saved dashboard screens.

### Available Tools

| Tool | Parameters | Description |
| :--- | :--- | :--- |
| `run_scan` | `scan_clause` *(string)* | Executes a custom Atlas query formula and returns raw results. |
| `get_screener` | `screener` *(string)* | Runs any screener by slug (e.g., `bullish-for-next-day`) or full URL. |
| `get_screener_info` | `screener` *(string)* | Returns the metadata, description, and formula without executing it. |
| `search_popular_screeners` | `query` *(string)* | Searches curated breakout, momentum, and volume screener templates. |
| `get_my_screeners` | *None* | Fetches private saved screeners (requires account credentials). |
| `get_my_watchlist` | *None* | Retrieves available watchlist indices and market segments. |

### Local Development

```bash
# Clone repository
git clone https://github.com/vanshpanchal026/Chartink-MCP.git
cd Chartink-MCP

# Run server locally
uv run chartink-mcp

# Run test suite
uv run python test_run.py
```

</details>

---

## 📄 License & Contributing

Distributed under the [MIT License](LICENSE). Contributions, bug reports, and feature requests are welcome via [GitHub Issues](https://github.com/vanshpanchal026/Chartink-MCP/issues) and Pull Requests.
