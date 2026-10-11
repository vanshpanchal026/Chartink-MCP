import json
from chartink_mcp.server import (
    run_scan,
    get_screener,
    get_screener_info,
    search_popular_screeners,
    get_my_watchlist,
    get_my_screeners,
)


def run_all_tests():
    print("--- Test 1: search_popular_screeners ---")
    pop = json.loads(search_popular_screeners("breakout"))
    print(f"Found {len(pop)} popular screeners for 'breakout'")
    assert len(pop) > 0, "No popular screeners found"

    print("--- Test 2: get_screener_info ---")
    info = json.loads(get_screener_info("15-minute-stock-breakouts"))
    print(f"Screener Name: {info.get('name')}")
    assert "atlas_query" in info, "Missing atlas_query in screener info"

    print("--- Test 3: get_screener (execution) ---")
    stocks = json.loads(get_screener("15-minute-stock-breakouts"))
    data = stocks.get("data", [])
    print(f"Total stocks returned: {len(data)}")
    assert len(data) > 0, "Expected stocks in breakout scan"

    print("--- Test 4: run_scan (custom clause) ---")
    custom_res = json.loads(
        run_scan("( {cash} ( latest close > 500 and latest close > latest open ) )")
    )
    custom_data = custom_res.get("data", [])
    print(f"Custom scan stocks count: {len(custom_data)}")
    assert len(custom_data) > 0, "Expected stocks in custom scan"

    print("--- Test 5: get_my_watchlist ---")
    wl = json.loads(get_my_watchlist())
    watchlists = wl.get("watchlists", [])
    print(f"Watchlists count: {len(watchlists)}")
    assert len(watchlists) > 0, "Expected default watchlists"

    print("--- Test 6: get_my_screeners (unauthenticated fallback check) ---")
    my_sc = json.loads(get_my_screeners())
    print(f"My screeners status: {my_sc.get('status')}")

    print("\n>>> ALL TESTS PASSED SUCCESSFULLY! <<<")


if __name__ == "__main__":
    run_all_tests()
