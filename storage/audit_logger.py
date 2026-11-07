"""
Regulatory and operational audit logging for Apex Federal Bank.
"""

from datetime import datetime
import sqlite3
from typing import Optional

from config import AUDIT_LOG_PATH
from core.security import mask_card_number


class AuditLogger:
    """Logs high-priority security, compliance, and transaction events."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def log_event(
        self,
        event_type: str,
        card_number: Optional[str] = None,
        details: str = "",
        severity: str = "INFO"
    ) -> None:
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        masked_card = mask_card_number(card_number) if card_number else "N/A"

        # 1. Log to DB
        try:
            with self.conn:
                self.conn.execute(
                    """INSERT INTO audit_logs (timestamp, event_type, card_masked, details, severity)
                       VALUES (?, ?, ?, ?, ?)""",
                    (timestamp_str, event_type, masked_card, details, severity)
                )
        except Exception:
            pass  # Fall back to file if DB is busy

        # 2. Append to file
        try:
            line = f"[{timestamp_str}] [{severity:5}] [{event_type:18}] Card: {masked_card:<19} | {details}\n"
            with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception:
            pass
