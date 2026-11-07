"""
Cash deposit interface view.
"""

from typing import Callable
import tkinter as tk

from config import CURRENCY_SYMBOL
from ui.theme import (
    COLOR_ACCENT_CYAN,
    COLOR_SCREEN_BG,
    COLOR_SCREEN_SURFACE,
    COLOR_SCREEN_SURFACE_ALT,
    COLOR_SUCCESS,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_HEADING,
    FONT_SMALL,
    FONT_TITLE,
)


class DepositView(tk.Frame):
    """View allowing cash deposit into user's account."""

    def __init__(
        self,
        parent,
        account_number: str,
        on_deposit: Callable[[float], None],
        on_back: Callable[[], None]
    ):
        super().__init__(parent, bg=COLOR_SCREEN_BG)
        self.account_number = account_number
        self.on_deposit = on_deposit
        self.on_back = on_back
        self.amount_str = ""

        self._build_view()

    def _build_view(self) -> None:
        tk.Label(
            self,
            text="CASH DEPOSIT",
            font=FONT_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_SCREEN_BG
        ).pack(pady=(0, 4))

        tk.Label(
            self,
            text=f"Target Account: {self.account_number}",
            font=FONT_BODY,
            fg=COLOR_ACCENT_CYAN,
            bg=COLOR_SCREEN_BG
        ).pack(pady=(0, 14))

        center_frame = tk.Frame(self, bg=COLOR_SCREEN_BG)
        center_frame.pack(expand=True, fill=tk.BOTH, padx=20)

        # Quick amounts
        tk.Label(
            center_frame,
            text="Quick Deposit Presets:",
            font=FONT_SMALL,
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_SCREEN_BG
        ).pack(anchor="w")

        presets_frame = tk.Frame(center_frame, bg=COLOR_SCREEN_BG)
        presets_frame.pack(fill=tk.X, pady=(4, 14))

        for amt in [50, 100, 200, 500]:
            btn = tk.Button(
                presets_frame,
                text=f"+{CURRENCY_SYMBOL}{amt}",
                font=FONT_BODY_BOLD,
                fg="#34D399",
                bg="#1E293B",
                activebackground=COLOR_SCREEN_SURFACE_ALT,
                activeforeground="#34D399",
                bd=1,
                relief=tk.RAISED,
                highlightbackground="#334155",
                highlightthickness=1,
                padx=12,
                pady=8,
                cursor="hand2",
                command=lambda a=amt: self._add_preset(a)
            )
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        # Display Total
        tk.Label(
            center_frame,
            text="Total Deposit Amount to Insert:",
            font=FONT_SMALL,
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_SCREEN_BG
        ).pack(anchor="w", pady=(6, 2))

        self.amount_display = tk.Label(
            center_frame,
            text=f"{CURRENCY_SYMBOL} 0",
            font=("Segoe UI", 24, "bold"),
            fg="#34D399",
            bg="#0F172A",
            highlightbackground="#10B981",
            highlightthickness=1,
            pady=8
        )
        self.amount_display.pack(fill=tk.X, pady=(0, 14))

        # Action Buttons
        btn_bar = tk.Frame(center_frame, bg=COLOR_SCREEN_BG)
        btn_bar.pack(fill=tk.X)

        self.confirm_btn = tk.Button(
            btn_bar,
            text="CONFIRM & DEPOSIT ▶",
            font=FONT_BODY_BOLD,
            fg="#FFFFFF",
            bg=COLOR_SUCCESS,
            activebackground="#059669",
            bd=0,
            pady=10,
            cursor="hand2",
            command=self._handle_confirm
        )
        self.confirm_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        back_btn = tk.Button(
            btn_bar,
            text="◀ Cancel",
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

    def _add_preset(self, amount: int) -> None:
        current = int(self.amount_str) if self.amount_str else 0
        self.amount_str = str(current + amount)
        self._update_display()

    def append_digit(self, char: str) -> None:
        if len(self.amount_str) < 5:
            self.amount_str += char
            self._update_display()

    def remove_digit(self) -> None:
        if self.amount_str:
            self.amount_str = self.amount_str[:-1]
            self._update_display()

    def clear(self) -> None:
        self.amount_str = ""
        self._update_display()

    def _update_display(self) -> None:
        val = int(self.amount_str) if self.amount_str else 0
        self.amount_display.config(text=f"{CURRENCY_SYMBOL} {val:,}")

    def _handle_confirm(self) -> None:
        val = float(self.amount_str) if self.amount_str else 0.0
        if val > 0:
            self.on_deposit(val)
