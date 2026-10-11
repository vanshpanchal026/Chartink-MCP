# Chartink MCP Server

A Model Context Protocol (MCP) server for **Chartink.com**, giving AI agents direct access to execute live technical screeners, scan formulas, and saved screeners for Indian stock markets (NSE / BSE).

---

## ⚡ Quick Start: 1-Command Auto Setup (Zero Clone)

Any user or AI agent can connect this MCP server in seconds without cloning the repository!

Run this in your terminal or give this command to your agent:

```bash
uvx --from git+https://github.com/vanshpanchal026/Chartink-MCP.git chartink-mcp setup
```

The setup wizard will:
1. Ask for your Chartink Email & Password (or press Enter to skip for free/public scans).
2. Auto-detect installed AI clients (**Antigravity**, **Codex**, **Claude Desktop**, **Cursor**, **Windsurf**).
3. Inject the configuration directly into their config files!

---

## 🤖 Native One-Line Commands by AI Agent

If you prefer to add Chartink MCP directly via your agent's native CLI without the setup wizard:

### 1. Antigravity CLI (`agy`)
```bash
agy mcp add chartink --command uvx --args "--from" "git+https://github.com/vanshpanchal026/Chartink-MCP.git" "chartink-mcp"
```
*Or add to `~/.gemini/antigravity/mcp_config.json`.*

### 2. OpenAI Codex CLI
```bash
codex mcp add chartink -- uvx --from git+https://github.com/vanshpanchal026/Chartink-MCP.git chartink-mcp
```
*Or add to `~/.codex/mcp.json`.*

### 3. Claude Code CLI
```bash
claude mcp add chartink -- uvx --from git+https://github.com/vanshpanchal026/Chartink-MCP.git chartink-mcp
```

### 4. Cursor IDE
Add to **Settings > Features > MCP > Add New MCP Server**:
- **Name**: `chartink`
- **Type**: `command`
- **Command**: `uvx --from git+https://github.com/vanshpanchal026/Chartink-MCP.git chartink-mcp`

### 5. Windsurf / Codeium
Add to `~/.codeium/windsurf/mcp_config.json`.

---

## 🚀 Features & Tools

All tools return exact **raw JSON** from Chartink's API for algorithmic precision:

- **`run_scan`**: Run any custom technical scan formula (RSI, Moving Averages, MACD, Volume, Candlestick patterns, Multi-timeframe).
- **`get_screener`**: Fetch and run any Chartink screener by slug or URL (e.g., `15-minute-stock-breakouts`, `high-momentum-breakout`).
- **`get_screener_info`**: Inspect the scan conditions / `atlas_query` and metadata of any screener without running it.
- **`search_popular_screeners`**: Quick access to top momentum, breakout, and reversal strategies.
- **`get_my_screeners`**: Access private saved screeners from your Chartink account.
- **`get_my_watchlist`**: Retrieve market segments, watchlists, and indices.

---

## 🔐 Authentication

Just like Screener.in's `SCREENER_USERNAME` / `SCREENER_PASSWORD`, Chartink credentials can be configured via:

1. **Auto Setup Wizard**: Run `uvx --from git+... chartink-mcp setup`
2. **Local `.env` File**:
   ```env
   CHARTINK_EMAIL=your_email@example.com
   CHARTINK_PASSWORD=your_password
   ```
3. **Manual `mcp_config.json`**:
   ```json
   "chartink": {
     "command": "uvx",
     "args": ["--from", "git+https://github.com/vanshpanchal026/Chartink-MCP.git", "chartink-mcp"],
     "env": {
       "PYTHONUTF8": "1",
       "CHARTINK_EMAIL": "your_email@example.com",
       "CHARTINK_PASSWORD": "your_password"
     }
   }
   ```
*Note: Public screeners and custom formulas work seamlessly without authentication.*

---

## 💻 Manual / Local Development

```bash
# Clone the repository
git clone https://github.com/vanshpanchal026/Chartink-MCP.git
cd chartink-mcp

# Run server
uv run chartink-mcp

# Run test suite
uv run python test_run.py
```
