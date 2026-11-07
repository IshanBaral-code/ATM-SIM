"""
Balance inquiry view.
"""

from typing import Callable
import tkinter as tk

from config import CURRENCY_SYMBOL, DAILY_WITHDRAWAL_LIMIT
from core.models import Account
from ui.theme import (
    COLOR_ACCENT_BLUE,
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


class BalanceView(tk.Frame):
    """View displaying current balances, ledger, and daily ATM limits."""

    def __init__(
        self,
        parent,
        account: Account,
        on_print_receipt: Callable[[], None],
        on_back: Callable[[], None],
        on_eject: Callable[[], None]
    ):
        super().__init__(parent, bg=COLOR_SCREEN_BG)
        self.account = account
        self.on_print_receipt = on_print_receipt
        self.on_back = on_back
        self.on_eject = on_eject

        self._build_view()

    def _build_view(self) -> None:
        center_frame = tk.Frame(self, bg=COLOR_SCREEN_BG)
        center_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        tk.Label(
            center_frame,
            text="ACCOUNT BALANCE INQUIRY",
            font=FONT_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_SCREEN_BG
        ).pack(pady=(0, 14))

        # Balance Card Panel
        card_panel = tk.Frame(
            center_frame,
            bg=COLOR_SCREEN_SURFACE,
            highlightbackground="#2A3859",
            highlightthickness=1,
            padx=20,
            pady=16
        )
        card_panel.pack(fill=tk.X, pady=(0, 18))

        rows = [
            ("Account Holder:", self.account.holder_name),
            ("Account Number:", self.account.account_number),
            ("Account Type:", self.account.account_type.value),
            ("Available Balance:", f"{CURRENCY_SYMBOL}{self.account.balance:,.2f}"),
            ("Ledger Balance:", f"{CURRENCY_SYMBOL}{self.account.balance:,.2f}"),
            ("Daily ATM Limit:", f"{CURRENCY_SYMBOL}{DAILY_WITHDRAWAL_LIMIT:,.2f}"),
            ("Withdrawn Today:", f"{CURRENCY_SYMBOL}{self.account.daily_withdrawn_today:,.2f}"),
        ]

        for i, (label, val) in enumerate(rows):
            r_frame = tk.Frame(card_panel, bg=COLOR_SCREEN_SURFACE)
            r_frame.pack(fill=tk.X, pady=3)

            is_avail = label == "Available Balance:"
            lbl_color = COLOR_TEXT_SECONDARY if not is_avail else COLOR_ACCENT_CYAN
            val_color = COLOR_TEXT_PRIMARY if not is_avail else "#34D399"
            val_font = FONT_BODY_BOLD if not is_avail else ("Segoe UI", 13, "bold")

            tk.Label(
                r_frame,
                text=label,
                font=FONT_BODY,
                fg=lbl_color,
                bg=COLOR_SCREEN_SURFACE
            ).pack(side=tk.LEFT)

            tk.Label(
                r_frame,
                text=val,
                font=val_font,
                fg=val_color,
                bg=COLOR_SCREEN_SURFACE
            ).pack(side=tk.RIGHT)

        # Action Buttons
        btn_bar = tk.Frame(center_frame, bg=COLOR_SCREEN_BG)
        btn_bar.pack(fill=tk.X)

        print_btn = tk.Button(
            btn_bar,
            text="🖨 Print Balance Slip",
            font=FONT_BODY_BOLD,
            fg="#FFFFFF",
            bg="#2563EB",
            activebackground="#1D4ED8",
            bd=0,
            pady=10,
            cursor="hand2",
            command=self.on_print_receipt
        )
        print_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        menu_btn = tk.Button(
            btn_bar,
            text="◀ Another Transaction",
            font=FONT_BODY,
            fg=COLOR_TEXT_PRIMARY,
            bg="#1E293B",
            activebackground="#334155",
            bd=0,
            pady=10,
            cursor="hand2",
            command=self.on_back
        )
        menu_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 4))

        eject_btn = tk.Button(
            btn_bar,
            text="⏏ Done & Exit",
            font=FONT_BODY,
            fg="#F87171",
            bg="#3B1B22",
            activebackground="#4C1D24",
            bd=0,
            pady=10,
            cursor="hand2",
            command=self.on_eject
        )
        eject_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))
