"""
Inter-account funds transfer view.
"""

from typing import Callable, List
import tkinter as tk
from tkinter import ttk

from config import CURRENCY_SYMBOL
from core.models import Account
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


class TransferView(tk.Frame):
    """View allowing transfer between linked accounts or third-party account."""

    SAMPLE_TARGETS = [
        ("ACT-1002-SAV", "Personal Savings (Alexander Vance)"),
        ("ACT-2001-CHK", "Eleanor Sterling (Checking)"),
        ("ACT-3001-CHK", "Marcus Brody (Checking)"),
    ]

    def __init__(
        self,
        parent,
        source_account: Account,
        on_transfer: Callable[[str, float], None],
        on_back: Callable[[], None]
    ):
        super().__init__(parent, bg=COLOR_SCREEN_BG)
        self.source_account = source_account
        self.on_transfer = on_transfer
        self.on_back = on_back
        self.amount_str = ""

        self._build_view()

    def _build_view(self) -> None:
        tk.Label(
            self,
            text="FUNDS TRANSFER",
            font=FONT_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_SCREEN_BG
        ).pack(pady=(0, 4))

        tk.Label(
            self,
            text=f"From: {self.source_account.account_type.value} ({self.source_account.account_number}) | Bal: {CURRENCY_SYMBOL}{self.source_account.balance:,.2f}",
            font=FONT_BODY,
            fg=COLOR_ACCENT_CYAN,
            bg=COLOR_SCREEN_BG
        ).pack(pady=(0, 14))

        form_frame = tk.Frame(self, bg=COLOR_SCREEN_BG)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        # Destination Account
        tk.Label(
            form_frame,
            text="Select Destination Account:",
            font=FONT_SMALL,
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_SCREEN_BG
        ).pack(anchor="w")

        self.target_var = tk.StringVar(value=self.SAMPLE_TARGETS[0][0])
        target_display = [f"{acc} - {desc}" for acc, desc in self.SAMPLE_TARGETS if acc != self.source_account.account_number]
        self.combo = ttk.Combobox(
            form_frame,
            values=target_display,
            state="readonly",
            font=FONT_BODY
        )
        if target_display:
            self.combo.set(target_display[0])
        self.combo.pack(fill=tk.X, pady=(2, 10))

        # Transfer Amount Display
        tk.Label(
            form_frame,
            text="Transfer Amount (Use Keypad):",
            font=FONT_SMALL,
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_SCREEN_BG
        ).pack(anchor="w")

        self.amount_display = tk.Label(
            form_frame,
            text=f"{CURRENCY_SYMBOL} 0",
            font=("Segoe UI", 22, "bold"),
            fg=COLOR_TEXT_PRIMARY,
            bg="#0F172A",
            highlightbackground="#38BDF8",
            highlightthickness=1,
            pady=6
        )
        self.amount_display.pack(fill=tk.X, pady=(2, 16))

        # Quick preset buttons
        preset_bar = tk.Frame(form_frame, bg=COLOR_SCREEN_BG)
        preset_bar.pack(fill=tk.X, pady=(0, 14))
        for amt in [50, 100, 250, 500]:
            btn = tk.Button(
                preset_bar,
                text=f"{CURRENCY_SYMBOL}{amt}",
                font=FONT_BODY,
                fg=COLOR_TEXT_PRIMARY,
                bg="#1E293B",
                activebackground=COLOR_SCREEN_SURFACE_ALT,
                bd=0,
                padx=8,
                pady=4,
                cursor="hand2",
                command=lambda a=amt: self._set_amount(a)
            )
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)

        # Action Buttons
        btn_bar = tk.Frame(form_frame, bg=COLOR_SCREEN_BG)
        btn_bar.pack(fill=tk.X)

        confirm_btn = tk.Button(
            btn_bar,
            text="EXECUTE TRANSFER ▶",
            font=FONT_BODY_BOLD,
            fg="#FFFFFF",
            bg=COLOR_SUCCESS,
            activebackground="#059669",
            bd=0,
            pady=10,
            cursor="hand2",
            command=self._handle_confirm
        )
        confirm_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

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

    def _set_amount(self, amt: int) -> None:
        self.amount_str = str(amt)
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
        selected = self.combo.get().split(" - ")[0].strip()
        if val > 0 and selected:
            self.on_transfer(selected, val)
