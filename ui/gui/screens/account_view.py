"""
Account selection view for multi-account cards.
"""

from typing import Callable, List
import tkinter as tk

from core.models import Account
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


class AccountSelectView(tk.Frame):
    """Allows user to select which account to access."""

    def __init__(self, parent, accounts: List[Account], on_select_account: Callable[[str], None]):
        super().__init__(parent, bg=COLOR_SCREEN_BG)
        self.accounts = accounts
        self.on_select_account = on_select_account

        self._build_view()

    def _build_view(self) -> None:
        center_frame = tk.Frame(self, bg=COLOR_SCREEN_BG)
        center_frame.pack(expand=True, fill=tk.BOTH, padx=30, pady=20)

        tk.Label(
            center_frame,
            text="SELECT PRIMARY ACCOUNT",
            font=FONT_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_SCREEN_BG
        ).pack(pady=(0, 6))

        tk.Label(
            center_frame,
            text="Choose an account to conduct transactions for this session:",
            font=FONT_BODY,
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_SCREEN_BG
        ).pack(pady=(0, 20))

        # Account cards grid
        for acc in self.accounts:
            card_btn = tk.Button(
                center_frame,
                text=f"{acc.account_type.value}\nAccount: {acc.account_number}\nAvailable: ${acc.balance:,.2f}",
                font=FONT_BODY_BOLD,
                fg=COLOR_TEXT_PRIMARY,
                bg=COLOR_SCREEN_SURFACE,
                activebackground=COLOR_SCREEN_SURFACE_ALT,
                activeforeground=COLOR_ACCENT_CYAN,
                bd=1,
                relief=tk.RAISED,
                highlightbackground="#334155",
                highlightthickness=1,
                padx=20,
                pady=16,
                cursor="hand2",
                command=lambda a_num=acc.account_number: self.on_select_account(a_num)
            )
            card_btn.pack(fill=tk.X, pady=6)
