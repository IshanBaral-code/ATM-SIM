"""
Tactile hardware keypad component emulating physical ATM PIN pads with function keys.
"""

import tkinter as tk
from ui.theme import (
    COLOR_DANGER,
    COLOR_DANGER_HOVER,
    COLOR_FRAME_BORDER,
    COLOR_KEYPAD_BG,
    COLOR_KEYPAD_BTN,
    COLOR_KEYPAD_BTN_HOVER,
    COLOR_KEYPAD_TEXT,
    COLOR_SUCCESS,
    COLOR_SUCCESS_HOVER,
    COLOR_TEXT_PRIMARY,
    COLOR_WARNING,
    COLOR_WARNING_HOVER,
    FONT_KEYPAD,
    FONT_KEYPAD_FN,
)


class ATMKeypad(tk.Frame):
    """Encapsulates the tactile ATM PIN Pad and action buttons."""

    def __init__(self, parent, on_digit=None, on_clear=None, on_cancel=None, on_enter=None, **kwargs):
        super().__init__(parent, bg=COLOR_KEYPAD_BG, highlightbackground=COLOR_FRAME_BORDER, highlightthickness=2, padx=14, pady=12, **kwargs)
        self.on_digit = on_digit
        self.on_clear = on_clear
        self.on_cancel = on_cancel
        self.on_enter = on_enter

        self._build_keypad()

    def _build_keypad(self) -> None:
        grid_frame = tk.Frame(self, bg=COLOR_KEYPAD_BG)
        grid_frame.pack()

        # 3x4 numeric keys
        num_keys = [
            ("1", 0, 0), ("2", 0, 1), ("3", 0, 2),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2),
            (".", 3, 0), ("0", 3, 1), ("00", 3, 2),
        ]

        for char, r, c in num_keys:
            btn = tk.Button(
                grid_frame,
                text=char,
                font=FONT_KEYPAD,
                fg=COLOR_KEYPAD_TEXT,
                bg=COLOR_KEYPAD_BTN,
                activebackground=COLOR_KEYPAD_BTN_HOVER,
                activeforeground=COLOR_TEXT_PRIMARY,
                width=5,
                height=2,
                bd=1,
                relief=tk.RAISED,
                cursor="hand2",
                command=lambda ch=char: self._press_digit(ch)
            )
            btn.grid(row=r, column=c, padx=4, pady=4)

        # Action column (Cancel, Clear, Blank, Enter)
        action_keys = [
            ("CANCEL", COLOR_DANGER, COLOR_DANGER_HOVER, self._press_cancel, 0),
            ("CLEAR",  COLOR_WARNING, COLOR_WARNING_HOVER, self._press_clear, 1),
            ("BLANK",  "#1E293B", "#334155", None, 2),
            ("ENTER",  COLOR_SUCCESS, COLOR_SUCCESS_HOVER, self._press_enter, 3),
        ]

        for label, bg, active_bg, cmd, r in action_keys:
            btn = tk.Button(
                grid_frame,
                text=label,
                font=FONT_KEYPAD_FN,
                fg="#FFFFFF" if bg != "#1E293B" else "#64748B",
                bg=bg,
                activebackground=active_bg,
                activeforeground="#FFFFFF",
                width=8,
                height=2,
                bd=1,
                relief=tk.RAISED,
                cursor="hand2" if cmd else "arrow",
                command=cmd
            )
            btn.grid(row=r, column=3, padx=(10, 4), pady=4)

    def _press_digit(self, char: str) -> None:
        if self.on_digit:
            self.on_digit(char)

    def _press_clear(self) -> None:
        if self.on_clear:
            self.on_clear()

    def _press_cancel(self) -> None:
        if self.on_cancel:
            self.on_cancel()

    def _press_enter(self) -> None:
        if self.on_enter:
            self.on_enter()
