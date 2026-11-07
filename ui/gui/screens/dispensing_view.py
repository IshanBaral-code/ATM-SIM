"""
Cash dispensing animation and bill breakdown view.
"""

from typing import Callable, Dict
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


class DispensingView(tk.Frame):
    """View shown while and after cash is physically dispensed."""

    def __init__(
        self,
        parent,
        amount: float,
        bills: Dict[int, int],
        on_print_receipt: Callable[[], None],
        on_finish: Callable[[], None]
    ):
        super().__init__(parent, bg=COLOR_SCREEN_BG)
        self.amount = amount
        self.bills = bills
        self.on_print_receipt = on_print_receipt
        self.on_finish = on_finish

        self._build_view()

    def _build_view(self) -> None:
        center_frame = tk.Frame(self, bg=COLOR_SCREEN_BG)
        center_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        # Animated Icon
        tk.Label(
            center_frame,
            text="💵",
            font=("Segoe UI", 42),
            bg=COLOR_SCREEN_BG
        ).pack(pady=(0, 4))

        tk.Label(
            center_frame,
            text="PLEASE COLLECT YOUR CASH",
            font=FONT_TITLE,
            fg="#34D399",
            bg=COLOR_SCREEN_BG
        ).pack()

        tk.Label(
            center_frame,
            text=f"Total Dispensed: {CURRENCY_SYMBOL}{self.amount:,.2f}",
            font=FONT_HEADING,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_SCREEN_BG
        ).pack(pady=(4, 12))

        # Denomination Breakdown Card
        breakdown_card = tk.Frame(
            center_frame,
            bg=COLOR_SCREEN_SURFACE,
            highlightbackground="#10B981",
            highlightthickness=1,
            padx=20,
            pady=12
        )
        breakdown_card.pack(fill=tk.X, pady=(0, 16))

        tk.Label(
            breakdown_card,
            text="DISPENSED BANKNOTE BREAKDOWN",
            font=FONT_SMALL,
            fg=COLOR_ACCENT_CYAN,
            bg=COLOR_SCREEN_SURFACE
        ).pack(pady=(0, 6))

        for denom in sorted(self.bills.keys(), reverse=True):
            count = self.bills[denom]
            if count > 0:
                row = tk.Frame(breakdown_card, bg=COLOR_SCREEN_SURFACE)
                row.pack(fill=tk.X, pady=2)

                subtotal = denom * count
                tk.Label(
                    row,
                    text=f"•  {count} x {CURRENCY_SYMBOL}{denom} Bill(s)",
                    font=FONT_BODY_BOLD,
                    fg=COLOR_TEXT_PRIMARY,
                    bg=COLOR_SCREEN_SURFACE
                ).pack(side=tk.LEFT)

                tk.Label(
                    row,
                    text=f"= {CURRENCY_SYMBOL}{subtotal:,.2f}",
                    font=FONT_BODY,
                    fg="#34D399",
                    bg=COLOR_SCREEN_SURFACE
                ).pack(side=tk.RIGHT)

        # Guidance notice
        tk.Label(
            center_frame,
            text="The cash dispenser shutter below is open.\nPlease remove your banknotes and select an option:",
            font=FONT_SMALL,
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_SCREEN_BG,
            justify=tk.CENTER
        ).pack(pady=(0, 14))

        # Action Buttons
        btn_bar = tk.Frame(center_frame, bg=COLOR_SCREEN_BG)
        btn_bar.pack(fill=tk.X)

        receipt_btn = tk.Button(
            btn_bar,
            text="🖨 Print Receipt",
            font=FONT_BODY_BOLD,
            fg="#FFFFFF",
            bg="#2563EB",
            activebackground="#1D4ED8",
            bd=0,
            pady=10,
            cursor="hand2",
            command=self.on_print_receipt
        )
        receipt_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        finish_btn = tk.Button(
            btn_bar,
            text="Continue / Another Transaction ▶",
            font=FONT_BODY_BOLD,
            fg="#FFFFFF",
            bg=COLOR_SUCCESS,
            activebackground="#059669",
            bd=0,
            pady=10,
            cursor="hand2",
            command=self.on_finish
        )
        finish_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))
