"""
Withdrawal and Fast Cash interface view.
"""

from typing import Callable
import tkinter as tk

from config import CURRENCY_SYMBOL, FAST_CASH_AMOUNTS
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


class WithdrawView(tk.Frame):
    """View allowing quick-pick fast cash or custom dollar amount withdrawal."""

    def __init__(
        self,
        parent,
        available_balance: float,
        on_withdraw: Callable[[float, bool], None],
        on_back: Callable[[], None]
    ):
        super().__init__(parent, bg=COLOR_SCREEN_BG)
        self.available_balance = available_balance
        self.on_withdraw = on_withdraw
        self.on_back = on_back
        self.amount_str = ""

        self._build_view()

    def _build_view(self) -> None:
        tk.Label(
            self,
            text="CASH WITHDRAWAL",
            font=FONT_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_SCREEN_BG
        ).pack(pady=(0, 4))

        tk.Label(
            self,
            text=f"Available Balance: {CURRENCY_SYMBOL}{self.available_balance:,.2f}",
            font=FONT_BODY_BOLD,
            fg="#34D399",
            bg=COLOR_SCREEN_BG
        ).pack(pady=(0, 14))

        # Main Layout: Left = Fast Cash grid, Right = Custom amount entry
        split_frame = tk.Frame(self, bg=COLOR_SCREEN_BG)
        split_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        split_frame.columnconfigure(0, weight=1)
        split_frame.columnconfigure(1, weight=1)

        # Left Column: Fast Cash
        left_box = tk.LabelFrame(
            split_frame,
            text=" Quick Fast Cash ",
            font=FONT_SMALL,
            fg=COLOR_ACCENT_CYAN,
            bg=COLOR_SCREEN_BG,
            padx=10,
            pady=10
        )
        left_box.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        fast_grid = tk.Frame(left_box, bg=COLOR_SCREEN_BG)
        fast_grid.pack(fill=tk.BOTH, expand=True)
        fast_grid.columnconfigure(0, weight=1)
        fast_grid.columnconfigure(1, weight=1)

        for i, amt in enumerate(FAST_CASH_AMOUNTS):
            r = i // 2
            c = i % 2
            btn = tk.Button(
                fast_grid,
                text=f"{CURRENCY_SYMBOL}{amt}",
                font=FONT_BODY_BOLD,
                fg=COLOR_TEXT_PRIMARY,
                bg="#1E293B",
                activebackground=COLOR_SCREEN_SURFACE_ALT,
                activeforeground=COLOR_ACCENT_CYAN,
                bd=1,
                relief=tk.RAISED,
                highlightbackground="#334155",
                highlightthickness=1,
                pady=10,
                cursor="hand2",
                command=lambda a=amt: self.on_withdraw(float(a), True)
            )
            btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")

        # Right Column: Custom Amount
        right_box = tk.LabelFrame(
            split_frame,
            text=" Other Amount ",
            font=FONT_SMALL,
            fg=COLOR_ACCENT_CYAN,
            bg=COLOR_SCREEN_BG,
            padx=12,
            pady=10
        )
        right_box.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        tk.Label(
            right_box,
            text="Enter custom amount (multiples of $10):",
            font=FONT_SMALL,
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_SCREEN_BG
        ).pack(anchor="w", pady=(0, 6))

        # Amount Display Box
        self.amount_display = tk.Label(
            right_box,
            text=f"{CURRENCY_SYMBOL} 0",
            font=("Segoe UI", 20, "bold"),
            fg=COLOR_TEXT_PRIMARY,
            bg="#0F172A",
            highlightbackground="#38BDF8",
            highlightthickness=1,
            pady=6
        )
        self.amount_display.pack(fill=tk.X, pady=(0, 10))

        # Action Buttons
        self.dispense_btn = tk.Button(
            right_box,
            text="DISPENSE CASH ▶",
            font=FONT_BODY_BOLD,
            fg="#FFFFFF",
            bg=COLOR_SUCCESS,
            activebackground="#059669",
            bd=0,
            pady=10,
            cursor="hand2",
            command=self._handle_custom_dispense
        )
        self.dispense_btn.pack(fill=tk.X, pady=(0, 6))

        back_btn = tk.Button(
            right_box,
            text="◀ Back to Menu",
            font=FONT_BODY,
            fg=COLOR_TEXT_SECONDARY,
            bg="#1E293B",
            activebackground="#334155",
            bd=0,
            pady=8,
            cursor="hand2",
            command=self.on_back
        )
        back_btn.pack(fill=tk.X)

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

    def _handle_custom_dispense(self) -> None:
        val = float(self.amount_str) if self.amount_str else 0.0
        if val > 0:
            self.on_withdraw(val, False)
