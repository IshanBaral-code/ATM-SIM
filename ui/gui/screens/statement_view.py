"""
Mini-Statement transaction history view.
"""

from typing import Callable, List
import tkinter as tk
from tkinter import ttk

from config import CURRENCY_SYMBOL
from core.models import Transaction, TransactionType
from ui.theme import (
    COLOR_ACCENT_CYAN,
    COLOR_SCREEN_BG,
    COLOR_SCREEN_SURFACE,
    COLOR_SCREEN_SURFACE_ALT,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_HEADING,
    FONT_SMALL,
    FONT_TITLE,
)


class StatementView(tk.Frame):
    """View displaying recent transaction history in a table."""

    def __init__(
        self,
        parent,
        transactions: List[Transaction],
        on_print_receipt: Callable[[], None],
        on_back: Callable[[], None]
    ):
        super().__init__(parent, bg=COLOR_SCREEN_BG)
        self.transactions = transactions
        self.on_print_receipt = on_print_receipt
        self.on_back = on_back

        self._build_view()

    def _build_view(self) -> None:
        tk.Label(
            self,
            text="RECENT ACCOUNT ACTIVITY",
            font=FONT_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_SCREEN_BG
        ).pack(pady=(0, 4))

        tk.Label(
            self,
            text="Displaying your last 8 transactions:",
            font=FONT_SMALL,
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_SCREEN_BG
        ).pack(pady=(0, 10))

        # Table container
        table_frame = tk.Frame(self, bg=COLOR_SCREEN_SURFACE, padx=4, pady=4)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 12))

        # Header Row
        hdr = tk.Frame(table_frame, bg="#1E293B", pady=6, padx=8)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="DATE/TIME", width=16, anchor="w", font=FONT_SMALL, fg=COLOR_ACCENT_CYAN, bg="#1E293B").pack(side=tk.LEFT)
        tk.Label(hdr, text="TRANSACTION TYPE", width=22, anchor="w", font=FONT_SMALL, fg=COLOR_ACCENT_CYAN, bg="#1E293B").pack(side=tk.LEFT)
        tk.Label(hdr, text="AMOUNT", width=14, anchor="e", font=FONT_SMALL, fg=COLOR_ACCENT_CYAN, bg="#1E293B").pack(side=tk.LEFT)
        tk.Label(hdr, text="BALANCE", width=14, anchor="e", font=FONT_SMALL, fg=COLOR_ACCENT_CYAN, bg="#1E293B").pack(side=tk.RIGHT)

        # Transaction Rows
        if not self.transactions:
            tk.Label(
                table_frame,
                text="No recent transactions recorded on this card.",
                font=FONT_BODY,
                fg=COLOR_TEXT_MUTED,
                bg=COLOR_SCREEN_SURFACE,
                pady=20
            ).pack()
        else:
            list_frame = tk.Frame(table_frame, bg=COLOR_SCREEN_SURFACE)
            list_frame.pack(fill=tk.BOTH, expand=True)

            for i, tx in enumerate(self.transactions[:8]):
                row_bg = COLOR_SCREEN_SURFACE if i % 2 == 0 else "#151F38"
                row = tk.Frame(list_frame, bg=row_bg, pady=4, padx=8)
                row.pack(fill=tk.X)

                dt_str = tx.timestamp.strftime("%m/%d %H:%M")
                is_credit = tx.tx_type in (TransactionType.DEPOSIT, TransactionType.TRANSFER_IN)
                amt_color = "#34D399" if is_credit else "#F87171"
                prefix = "+" if is_credit else "-"
                amt_str = f"{prefix}{CURRENCY_SYMBOL}{tx.amount:,.2f}"

                tk.Label(row, text=dt_str, width=16, anchor="w", font=FONT_SMALL, fg=COLOR_TEXT_SECONDARY, bg=row_bg).pack(side=tk.LEFT)
                tk.Label(row, text=tx.tx_type.value, width=22, anchor="w", font=FONT_SMALL, fg=COLOR_TEXT_PRIMARY, bg=row_bg).pack(side=tk.LEFT)
                tk.Label(row, text=amt_str, width=14, anchor="e", font=FONT_SMALL, fg=amt_color, bg=row_bg).pack(side=tk.LEFT)
                tk.Label(row, text=f"{CURRENCY_SYMBOL}{tx.balance_after:,.2f}", width=14, anchor="e", font=FONT_SMALL, fg=COLOR_TEXT_PRIMARY, bg=row_bg).pack(side=tk.RIGHT)

        # Buttons
        btn_bar = tk.Frame(self, bg=COLOR_SCREEN_BG)
        btn_bar.pack(fill=tk.X, padx=10)

        print_btn = tk.Button(
            btn_bar,
            text="🖨 Print Statement Slip",
            font=FONT_BODY_BOLD,
            fg="#FFFFFF",
            bg="#2563EB",
            activebackground="#1D4ED8",
            bd=0,
            pady=10,
            cursor="hand2",
            command=self.on_print_receipt
        )
        print_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        back_btn = tk.Button(
            btn_bar,
            text="◀ Back to Menu",
            font=FONT_BODY,
            fg=COLOR_TEXT_SECONDARY,
            bg="#1E293B",
            activebackground="#334155",
            bd=0,
            pady=10,
            cursor="hand2",
            command=self.on_back
        )
        back_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))
