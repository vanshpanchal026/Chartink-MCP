import os
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from chartink_mcp.client import ChartinkClient

# Load environment variables from .env if present
load_dotenv()

# Initialize FastMCP Server
mcp = FastMCP("chartink")

# Lazy client instance
_client: Optional[ChartinkClient] = None


def get_client() -> ChartinkClient:
    global _client
    if _client is None:
        _client = ChartinkClient()
    return _client


@mcp.tool()
def run_scan(scan_clause: str) -> str:
    """Execute a custom technical scan formula on Chartink and return raw JSON.

    Parameters:
      scan_clause: The Chartink scan formula string.
        Examples:
          '( {cash} ( latest close > latest open and latest volume > 100000 ) )'
          '( {33489} ( latest rsi( 14 ) > 60 and latest close > latest ema( close, 20 ) ) )'
    """
    client = get_client()
    result = client.run_scan(scan_clause)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_screener(screener: str) -> str:
    """Fetch and run any Chartink screener by slug or URL, returning raw JSON results.

    Parameters:
      screener: Slug (e.g., '15-minute-stock-breakouts') or full URL
                (e.g., 'https://chartink.com/screener/high-momentum-breakout').
    """
    client = get_client()
    result = client.get_screener(screener)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_screener_info(screener: str) -> str:
    """Get metadata, formula, and description of a Chartink screener without running it.

    Parameters:
      screener: Slug (e.g., 'bullish-for-next-day') or full URL.
    """
    client = get_client()
    result = client.get_screener_info(screener)
    return json.dumps(result, indent=2)


@mcp.tool()
def search_popular_screeners(query: str = "") -> str:
    """Search popular and pre-defined Chartink screener strategies.

    Parameters:
      query: Filter by keyword (e.g., 'breakout', 'rsi', 'momentum', 'volume').
             Leave empty to list all top screeners.
    """
    client = get_client()
    result = client.search_popular_screeners(query)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_my_screeners() -> str:
    """Retrieve saved screeners from the authenticated user's Chartink account.

    Requires CHARTINK_EMAIL and CHARTINK_PASSWORD to be configured in .env
    or mcp_config.json.
    """
    client = get_client()
    result = client.get_my_screeners()
    return json.dumps(result, indent=2)


@mcp.tool()
def get_my_watchlist() -> str:
    """Get available watchlists, market segments, and indices from Chartink."""
    client = get_client()
    result = client.get_my_watchlist()
    return json.dumps(result, indent=2)


def main():
    import sys
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("setup", "install", "--setup", "-s", "config", "configure"):
        sys.argv.pop(1)
        from chartink_mcp.installer import main as installer_main
        installer_main()
        return

    mcp.run()


if __name__ == "__main__":
    main()
