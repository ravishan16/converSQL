#!/usr/bin/env python3
"""
Minimal Cloudflare D1 Logger
Lightweight logging service for user activity and queries.
"""

import os
from typing import Any, Dict, List, Optional

import requests  # type: ignore[import-untyped]
from dotenv import load_dotenv

load_dotenv()


class D1Logger:
    """Minimal Cloudflare D1 database logger."""

    def __init__(self):
        self.account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.database_id = os.getenv("CLOUDFLARE_D1_DATABASE_ID")
        self.api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        self.enabled = bool(self.account_id and self.database_id and self.api_token)

    def is_enabled(self) -> bool:
        """Check if D1 logging is enabled."""
        return self.enabled

    def _execute_query(self, sql: str, params: Optional[List[Any]] = None) -> Optional[Dict[str, Any]]:
        """Execute a D1 query via REST API."""
        if not self.enabled:
            return None

        url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/d1/database/{self.database_id}/query"

        headers = {"Authorization": f"Bearer {self.api_token}", "Content-Type": "application/json"}

        payload: Dict[str, Any] = {"sql": sql}

        if params:
            payload["params"] = params

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                # Silent fail - don't break the app if logging fails
                return None
        except Exception:
            # Silent fail
            return None

    def log_user_login(self, user_id: str, email: str, user_agent: str = None):
        """Log user login event."""
        if not self.enabled:
            return

        sql = """
        INSERT INTO user_logins (user_id, email, user_agent)
        VALUES (?, ?, ?)
        """

        self._execute_query(sql, [user_id, email, user_agent or ""])

    def log_user_query(
        self, user_id: str, email: str, question: str, sql_query: str, ai_provider: str, execution_time: float
    ):
        """Log user query event."""
        if not self.enabled:
            return

        sql = """
        INSERT INTO user_queries (user_id, email, question, sql_query, ai_provider, execution_time)
        VALUES (?, ?, ?, ?, ?, ?)
        """

        self._execute_query(sql, [user_id, email, question, sql_query, ai_provider, execution_time])

    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get basic user statistics."""
        if not self.enabled:
            return {}

        sql = """
        SELECT
            COUNT(*) as total_queries,
            MIN(query_time) as first_query,
            MAX(query_time) as last_query
        FROM user_queries
        WHERE user_id = ?
        """

        result = self._execute_query(sql, [user_id])
        if result and result.get("success") and result.get("result"):
            return result["result"][0] if result["result"] else {}
        return {}


# Global logger instance
_d1_logger: Optional[D1Logger] = None


def get_d1_logger() -> D1Logger:
    """Get or create global D1 logger instance."""
    global _d1_logger
    if _d1_logger is None:
        _d1_logger = D1Logger()
    return _d1_logger
