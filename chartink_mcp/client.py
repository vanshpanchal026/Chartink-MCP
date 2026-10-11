import os
import json
import re
import urllib.parse
from typing import Optional, Dict, Any, List
import requests
from bs4 import BeautifulSoup


class ChartinkClient:
    BASE_URL = "https://chartink.com"
    PROCESS_URL = "https://chartink.com/screener/process"
    LOGIN_URL = "https://chartink.com/login"
    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
    }

    POPULAR_SCREENERS = [
        {
            "slug": "15-minute-stock-breakouts",
            "name": "15 Minute Stock Breakouts",
            "description": "Intraday breakout stocks crossing 15m highs with volume expansion",
        },
        {
            "slug": "bullish-for-next-day",
            "name": "Bullish for Next Day",
            "description": "Multi-indicator bullish continuation for swing / positional longs",
        },
        {
            "slug": "high-momentum-breakout",
            "name": "High Momentum Breakout",
            "description": "High momentum stocks breaking out on daily / weekly timeframes",
        },
        {
            "slug": "rsi-above-55-and-breakout",
            "name": "RSI Above 55 and Breakout",
            "description": "RSI entering bullish momentum zone combined with price breakout",
        },
        {
            "slug": "52-week-high-stocks",
            "name": "52 Week High Breakouts",
            "description": "Stocks trading near or breaking out of 52-week highs",
        },
        {
            "slug": "volume-shockers",
            "name": "Volume Shockers",
            "description": "Unusual surge in volume indicating institutional participation",
        },
        {
            "slug": "bullish-engulfing",
            "name": "Bullish Engulfing",
            "description": "Daily bullish engulfing candlestick pattern",
        },
        {
            "slug": "golden-cross",
            "name": "Golden Cross (50 EMA > 200 EMA)",
            "description": "50 EMA crossing above 200 EMA trend reversal signal",
        },
        {
            "slug": "supertrend-positive-breakout",
            "name": "Supertrend Positive Breakout",
            "description": "Price crossing above Supertrend indicator",
        },
        {
            "slug": "intraday-buying-volume",
            "name": "Intraday Buying Volume",
            "description": "High intraday volume with bullish close",
        },
    ]

    def __init__(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        session_cookie: Optional[str] = None,
    ):
        self.email = email or os.getenv("CHARTINK_EMAIL")
        self.password = password or os.getenv("CHARTINK_PASSWORD")
        self.session_cookie = session_cookie or os.getenv("CHARTINK_SESSION_COOKIE")
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)
        self.csrf_token: Optional[str] = None
        self.is_authenticated = False
        self.user_data: Optional[Dict[str, Any]] = None

        if self.session_cookie:
            self.session.cookies.set("ci_session", self.session_cookie, domain="chartink.com")
            self.is_authenticated = True

    def _ensure_csrf(self, url: str = "https://chartink.com/screener/") -> str:
        """Fetches a fresh CSRF token and warms up cookies."""
        resp = self.session.get(url, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        meta = soup.find("meta", {"name": "csrf-token"})
        if meta and meta.get("content"):
            self.csrf_token = meta["content"]
            self.session.headers.update({"X-CSRF-TOKEN": self.csrf_token})
            return self.csrf_token

        # Fallback to XSRF-TOKEN cookie if available
        xsrf = self.session.cookies.get("XSRF-TOKEN")
        if xsrf:
            token = urllib.parse.unquote(xsrf)
            self.csrf_token = token
            self.session.headers.update({"X-CSRF-TOKEN": token})
            return token

        raise RuntimeError("Failed to obtain CSRF token from Chartink.")

    def login(self) -> Dict[str, Any]:
        """Logs into Chartink using Inertia.js credentials auth."""
        if not self.email or not self.password:
            return {"authenticated": False, "message": "No credentials configured"}

        try:
            # 1. Fetch login page to get XSRF-TOKEN & Inertia version
            r = self.session.get(self.LOGIN_URL, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")
            app_div = soup.find("div", {"id": "app"})
            version = ""
            if app_div and app_div.get("data-page"):
                try:
                    data = json.loads(app_div["data-page"])
                    version = data.get("version", "")
                except Exception:
                    pass

            xsrf = self.session.cookies.get("XSRF-TOKEN")
            if not xsrf:
                return {"authenticated": False, "message": "Failed to get XSRF token"}

            xsrf_token = urllib.parse.unquote(xsrf)
            headers = {
                "X-XSRF-TOKEN": xsrf_token,
                "X-Inertia": "true",
                "Content-Type": "application/json",
                "Referer": self.LOGIN_URL,
            }
            if version:
                headers["X-Inertia-Version"] = version

            payload = {
                "email": self.email,
                "password": self.password,
                "remember": True,
            }

            resp = self.session.post(
                self.LOGIN_URL,
                json=payload,
                headers=headers,
                timeout=15,
            )

            # Check for Inertia error props
            try:
                data = resp.json()
                errors = data.get("props", {}).get("errors", {})
                if errors:
                    err_msg = ", ".join(f"{k}: {v}" for k, v in errors.items())
                    return {"authenticated": False, "error": err_msg}

                user = data.get("props", {}).get("user")
                if user:
                    self.is_authenticated = True
                    self.user_data = user
                    return {"authenticated": True, "user": user}
            except Exception:
                pass

            if resp.status_code in (200, 302):
                self.is_authenticated = True
                return {"authenticated": True, "status_code": resp.status_code}

            return {"authenticated": False, "status_code": resp.status_code}
        except Exception as e:
            return {"authenticated": False, "error": str(e)}

    def run_scan(self, scan_clause: str) -> Dict[str, Any]:
        """
        Executes a scan clause directly on Chartink.
        Returns the exact raw JSON response from Chartink process API.
        """
        if not self.csrf_token:
            self._ensure_csrf()

        headers = {
            "X-CSRF-TOKEN": self.csrf_token,
            "Referer": "https://chartink.com/screener/",
        }

        resp = self.session.post(
            self.PROCESS_URL,
            data={"scan_clause": scan_clause},
            headers=headers,
            timeout=20,
        )

        # Handle CSRF token mismatch / expiry
        if resp.status_code in (419, 403):
            self._ensure_csrf()
            headers["X-CSRF-TOKEN"] = self.csrf_token
            resp = self.session.post(
                self.PROCESS_URL,
                data={"scan_clause": scan_clause},
                headers=headers,
                timeout=20,
            )

        resp.raise_for_status()
        return resp.json()

    def _normalize_slug(self, url_or_slug: str) -> str:
        s = url_or_slug.strip().rstrip("/")
        if "chartink.com/screener/" in s:
            return s.split("chartink.com/screener/")[-1].split("?")[0]
        if s.startswith("/screener/"):
            return s.replace("/screener/", "").split("?")[0]
        return s

    def get_screener_info(self, url_or_slug: str) -> Dict[str, Any]:
        """
        Retrieves screener configuration (name, description, atlas_query, author)
        from a Chartink screener page without executing the scan.
        """
        slug = self._normalize_slug(url_or_slug)
        url = f"{self.BASE_URL}/screener/{slug}"
        resp = self.session.get(url, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        meta = soup.find("meta", {"name": "csrf-token"})
        if meta and meta.get("content"):
            self.csrf_token = meta["content"]
            self.session.headers.update({"X-CSRF-TOKEN": self.csrf_token})

        scanner = soup.find("scanner")
        if not scanner or not scanner.get(":scan-json"):
            # Check for fallback textarea
            textarea = soup.find("textarea", {"name": "scan_clause"})
            if textarea and textarea.text.strip():
                return {
                    "slug": slug,
                    "name": slug.replace("-", " ").title(),
                    "atlas_query": textarea.text.strip(),
                }
            raise ValueError(f"Could not find scan formula for screener '{slug}'")

        scan_json = json.loads(scanner[":scan-json"])
        atlas_query = scan_json.get("atlas_query")
        if not atlas_query:
            raise ValueError(f"No atlas_query found for screener '{slug}'")

        return {
            "slug": slug,
            "name": scan_json.get("name", slug.replace("-", " ").title()),
            "description": scan_json.get("description", ""),
            "atlas_query": atlas_query,
            "created_at": scan_json.get("created_at"),
            "updated_at": scan_json.get("updated_at"),
            "can_copy": scan_json.get("can_copy", False),
        }

    def get_screener(self, url_or_slug: str) -> Dict[str, Any]:
        """
        Fetches and runs a saved or public Chartink screener by slug or URL.
        Returns the exact raw JSON output from Chartink.
        """
        info = self.get_screener_info(url_or_slug)
        raw_result = self.run_scan(info["atlas_query"])
        return raw_result

    def get_my_screeners(self) -> Dict[str, Any]:
        """
        Fetches the authenticated user's private/saved screeners and dashboards.
        """
        if not self.is_authenticated:
            auth_res = self.login()
            if not auth_res.get("authenticated"):
                return {
                    "status": "unauthenticated",
                    "message": "Login required to fetch saved screeners. Set CHARTINK_EMAIL and CHARTINK_PASSWORD.",
                    "auth_attempt": auth_res,
                }

        # Request user dashboard or screener page
        r = self.session.get(f"{self.BASE_URL}/screener/", timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        scanner = soup.find("scanner")
        if scanner and scanner.get(":current-user"):
            try:
                user = json.loads(scanner[":current-user"])
                return {"status": "authenticated", "user": user}
            except Exception:
                pass

        return {"status": "authenticated", "user_data": self.user_data or {}}

    def get_my_watchlist(self) -> Dict[str, Any]:
        """
        Fetches available watchlists and segment indices from Chartink.
        """
        r = self.session.get(f"{self.BASE_URL}/screener/", timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        scanner = soup.find("scanner")
        if scanner and scanner.get(":watchlist-json"):
            try:
                watchlists = json.loads(scanner[":watchlist-json"])
                return {"status": "success", "watchlists": watchlists}
            except Exception:
                pass
        return {"status": "error", "message": "Failed to extract watchlists"}

    def search_popular_screeners(self, query: str = "") -> List[Dict[str, Any]]:
        """
        Returns a list of curated top Chartink screeners matching the search query.
        """
        q = query.strip().lower()
        if not q:
            return self.POPULAR_SCREENERS

        results = []
        for s in self.POPULAR_SCREENERS:
            if (
                q in s["slug"].lower()
                or q in s["name"].lower()
                or q in s["description"].lower()
            ):
                results.append(s)
        return results
