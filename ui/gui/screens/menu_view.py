"""
Main banking transactions dashboard view.
"""

from typing import Callable
import tkinter as tk

from core.models import Account
from ui.theme import (
    COLOR_ACCENT_BLUE,
    COLOR_ACCENT_CYAN,
    COLOR_DANGER,
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


class MainMenuView(tk.Frame):
    """Main ATM transaction hub with clean responsive grid buttons."""

    def __init__(
        self,
        parent,
        account: Account,
        on_action: Callable[[str], None]
    ):
        super().__init__(parent, bg=COLOR_SCREEN_BG)
        self.account = account
        self.on_action = on_action

        self._build_view()

    def _build_view(self) -> None:
        # Top Account Overview Strip
        info_bar = tk.Frame(self, bg=COLOR_SCREEN_SURFACE, padx=16, pady=10)
        info_bar.pack(fill=tk.X, pady=(0, 16))

        tk.Label(
            info_bar,
            text=f"ACTIVE: {self.account.account_type.value}  ({self.account.account_number})",
            font=FONT_BODY_BOLD,
            fg=COLOR_ACCENT_CYAN,
            bg=COLOR_SCREEN_SURFACE
        ).pack(side=tk.LEFT)

        tk.Label(
            info_bar,
            text=f"AVAILABLE: ${self.account.balance:,.2f}",
            font=FONT_BODY_BOLD,
            fg="#34D399",
            bg=COLOR_SCREEN_SURFACE
        ).pack(side=tk.RIGHT)

        # Title
        tk.Label(
            self,
            text="PLEASE SELECT A TRANSACTION",
            font=FONT_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_SCREEN_BG
        ).pack(pady=(0, 14))

        # 2-column Grid of Banking Operations
        grid_frame = tk.Frame(self, bg=COLOR_SCREEN_BG)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)

        buttons = [
            ("⚡ Fast Cash $100", "fast_cash_100", 0, 0, "#1E293B", "#38BDF8"),
            ("🏧 Custom Withdrawal", "withdraw", 0, 1, "#1E293B", "#38BDF8"),
            ("📥 Cash Deposit", "deposit", 1, 0, "#1E293B", "#34D399"),
            ("🔄 Transfer Funds", "transfer", 1, 1, "#1E293B", "#38BDF8"),
            ("📊 Balance Inquiry", "balance", 2, 0, "#1E293B", "#F59E0B"),
            ("🧾 Mini-Statement", "statement", 2, 1, "#1E293B", "#F59E0B"),
            ("🔑 Change PIN", "change_pin", 3, 0, "#1E293B", "#94A3B8"),
            ("⏏ Finish & Eject Card", "eject", 3, 1, "#3B1B22", "#F87171"),
        ]

        for text, action, r, c, bg, text_color in buttons:
            btn = tk.Button(
                grid_frame,
                text=text,
                font=FONT_BODY_BOLD,
                fg=text_color,
                bg=bg,
                activebackground=COLOR_SCREEN_SURFACE_ALT,
                activeforeground=COLOR_ACCENT_CYAN,
                bd=1,
                relief=tk.RAISED,
                highlightbackground="#334155",
                highlightthickness=1,
                pady=12,
                cursor="hand2",
                command=lambda act=action: self.on_action(act)
            )
            btn.grid(row=r, column=c, padx=8, pady=6, sticky="nsew")
