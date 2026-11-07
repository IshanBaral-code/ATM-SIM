"""
PIN entry and authentication view.
"""

import tkinter as tk
from core.security import mask_card_number
from ui.theme import (
    COLOR_ACCENT_CYAN,
    COLOR_DANGER,
    COLOR_SCREEN_BG,
    COLOR_SCREEN_SURFACE,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_HEADING,
    FONT_SMALL,
    FONT_TITLE,
)


class PINView(tk.Frame):
    """Encapsulates the secure PIN entry display with animated pin dots."""

    def __init__(self, parent, holder_name: str, card_number: str, on_submit=None, on_cancel=None):
        super().__init__(parent, bg=COLOR_SCREEN_BG)
        self.holder_name = holder_name
        self.card_number = card_number
        self.on_submit = on_submit
        self.on_cancel = on_cancel
        self.pin_digits: list[str] = []

        self._build_view()

    def _build_view(self) -> None:
        center_frame = tk.Frame(self, bg=COLOR_SCREEN_BG)
        center_frame.pack(expand=True)

        tk.Label(
            center_frame,
            text="🔐",
            font=("Segoe UI", 36),
            bg=COLOR_SCREEN_BG
        ).pack()

        tk.Label(
            center_frame,
            text="SECURITY AUTHENTICATION",
            font=FONT_HEADING,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_SCREEN_BG
        ).pack(pady=(2, 6))

        # Cardholder Badge
        cardholder_box = tk.Frame(center_frame, bg=COLOR_SCREEN_SURFACE, padx=20, pady=8)
        cardholder_box.pack(pady=(0, 16))

        tk.Label(
            cardholder_box,
            text=f"Welcome, {self.holder_name.upper()}",
            font=FONT_BODY_BOLD,
            fg=COLOR_ACCENT_CYAN,
            bg=COLOR_SCREEN_SURFACE
        ).pack()

        tk.Label(
            cardholder_box,
            text=f"Card: {mask_card_number(self.card_number)}",
            font=FONT_SMALL,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_SCREEN_SURFACE
        ).pack(pady=(2, 0))

        # Prompt
        tk.Label(
            center_frame,
            text="Please enter your 4-digit Secret PIN:",
            font=FONT_BODY,
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_SCREEN_BG
        ).pack(pady=(0, 12))

        # PIN Dot Slots Frame
        self.dots_frame = tk.Frame(center_frame, bg=COLOR_SCREEN_BG)
        self.dots_frame.pack(pady=(0, 20))

        self.dot_labels = []
        for i in range(4):
            lbl = tk.Label(
                self.dots_frame,
                text="○",
                font=("Segoe UI", 26),
                fg="#475569",
                bg=COLOR_SCREEN_SURFACE,
                width=3,
                height=1,
                highlightbackground="#334155",
                highlightthickness=1
            )
            lbl.pack(side=tk.LEFT, padx=6)
            self.dot_labels.append(lbl)

        # Instructions
        tk.Label(
            center_frame,
            text="Use the numeric keypad below to type digits.\nPress GREEN [ENTER] when done or RED [CANCEL] to abort.",
            font=FONT_SMALL,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_SCREEN_BG,
            justify=tk.CENTER
        ).pack()

        # Warning
        tk.Label(
            center_frame,
            text="⚠ 3 consecutive failed attempts will permanently lock this card.",
            font=FONT_SMALL,
            fg="#F59E0B",
            bg=COLOR_SCREEN_BG
        ).pack(pady=(12, 0))

    def append_digit(self, char: str) -> None:
        if len(self.pin_digits) < 6:
            self.pin_digits.append(char)
            self._update_dots()

    def remove_digit(self) -> None:
        if self.pin_digits:
            self.pin_digits.pop()
            self._update_dots()

    def clear(self) -> None:
        self.pin_digits.clear()
        self._update_dots()

    def get_pin(self) -> str:
        return "".join(self.pin_digits)

    def _update_dots(self) -> None:
        count = len(self.pin_digits)
        # Ensure we have enough dot labels
        while len(self.dot_labels) < max(4, count):
            lbl = tk.Label(
                self.dots_frame,
                text="○",
                font=("Segoe UI", 26),
                fg="#475569",
                bg=COLOR_SCREEN_SURFACE,
                width=3,
                height=1,
                highlightbackground="#334155",
                highlightthickness=1
            )
            lbl.pack(side=tk.LEFT, padx=6)
            self.dot_labels.append(lbl)

        for i, lbl in enumerate(self.dot_labels):
            if i < count:
                lbl.config(text="●", fg="#38BDF8")
            else:
                lbl.config(text="○", fg="#475569")
